from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .timeseries import TimeSeries
import os


@dataclass
class Portfolio:
    """
    DataClass que representa una cartera de inversión.
    Combina múltiples series de precios (TimeSeries) con pesos específicos.
    """
    
    components: List[TimeSeries]
    weights: Dict[str, float]
    
    # Métricas de la cartera calculadas automáticamente
    portfolio_return: float = field(init=False)
    portfolio_volatility: float = field(init=False)
    covariance_matrix: np.ndarray = field(init=False, repr=False)
    
    def __post_init__(self):
        """
        Valida y calcula las métricas de la cartera al inicializar.
        """
        # Validar que los pesos sumen 1 (o cerca de 1)
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=0.01):
            # Normalizar pesos si no suman 1
            print(f"⚠️ Los pesos suman {total_weight:.4f}, se normalizarán a 1.0")
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
        
        # Validar que todos los componentes tengan peso asignado
        component_tickers = {ts.ticker for ts in self.components}
        weight_tickers = set(self.weights.keys())
        
        if component_tickers != weight_tickers:
            raise ValueError(f"Mismatch entre tickers: componentes={component_tickers}, pesos={weight_tickers}")
        
        # Calcular métricas de la cartera
        self._calculate_portfolio_metrics()
    
    def _calculate_portfolio_metrics(self):
        """Calcula rendimiento, volatilidad y matriz de covarianza de la cartera."""
        
        # Crear DataFrame con todos los rendimientos alineados por fecha
        returns_df = pd.DataFrame()
        
        for ts in self.components:
            # Asegurarnos de que Date sea el índice
            temp_df = ts.data.set_index('Date')[['Log_Returns']].copy()
            temp_df.columns = [ts.ticker]
            returns_df = returns_df.join(temp_df, how='outer') if not returns_df.empty else temp_df
        
        # Eliminar NaN (por diferentes fechas de inicio/fin)
        returns_df = returns_df.dropna()
        
        if returns_df.empty:
            raise ValueError("No hay datos overlapeados entre los componentes de la cartera")
        
        # Vector de pesos en el orden correcto
        weight_vector = np.array([self.weights[ticker] for ticker in returns_df.columns])
        
        # Calcular matriz de covarianza
        self.covariance_matrix = returns_df.cov().values
        
        # Rendimiento de la cartera: suma ponderada de rendimientos individuales
        mean_returns = returns_df.mean().values
        self.portfolio_return = np.dot(weight_vector, mean_returns)
        
        # Volatilidad de la cartera: sqrt(w^T * Cov * w)
        portfolio_variance = np.dot(weight_vector, np.dot(self.covariance_matrix, weight_vector))
        self.portfolio_volatility = np.sqrt(portfolio_variance)
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
        """Calcula el Ratio de Sharpe de la cartera."""
        annual_return = self.portfolio_return * periods_per_year
        annual_volatility = self.portfolio_volatility * np.sqrt(periods_per_year)
        
        if annual_volatility == 0:
            return 0.0
        
        return (annual_return - risk_free_rate) / annual_volatility
    
    def montecarlo_simulation(
        self,
        num_simulations: int = 1000,
        time_horizon: int = 252,
        confidence_level: float = 0.95,
        simulate_components: bool = False
    ) -> Dict:
        """
        Realiza simulación Monte Carlo usando Movimiento Browniano Geométrico (GBM).
        
        Formula GBM: S_t = S_{t-1} * exp((μ - 0.5*σ²)Δt + σ*sqrt(Δt)*Z)
        
        Args:
            num_simulations: Número de trayectorias a simular
            time_horizon: Días/períodos a proyectar
            confidence_level: Nivel de confianza para VaR (ej. 0.95)
            simulate_components: Si True, simula cada componente por separado
            
        Returns:
            Diccionario con resultados de la simulación
        """
        dt = 1  # Delta t (1 día)
        
        if simulate_components:
            # Simular cada componente individualmente
            component_simulations = {}
            
            for ts in self.components:
                initial_price = ts.data['Close'].iloc[-1]
                mu = ts.mean_return
                sigma = ts.stdev_return
                
                simulations = self._run_gbm_simulation(
                    initial_price, mu, sigma, num_simulations, time_horizon, dt
                )
                
                component_simulations[ts.ticker] = simulations
            
            return {
                'type': 'components',
                'simulations': component_simulations,
                'time_horizon': time_horizon,
                'num_simulations': num_simulations
            }
        
        else:
            # Simular la cartera como un todo
            # Calcular valor inicial de la cartera (usando último precio de cada componente)
            initial_portfolio_value = sum(
                ts.data['Close'].iloc[-1] * self.weights[ts.ticker] * 100  # *100 para escalar
                for ts in self.components
            )
            
            mu = self.portfolio_return
            sigma = self.portfolio_volatility
            
            simulations = self._run_gbm_simulation(
                initial_portfolio_value, mu, sigma, num_simulations, time_horizon, dt
            )
            
            # Calcular VaR (Value at Risk)
            final_values = simulations[:, -1]
            var_percentile = (1 - confidence_level) * 100
            var = np.percentile(final_values, var_percentile)
            var_loss = initial_portfolio_value - var
            
            return {
                'type': 'portfolio',
                'simulations': simulations,
                'initial_value': initial_portfolio_value,
                'mean_final_value': np.mean(final_values),
                'var': var,
                'var_loss': var_loss,
                'confidence_level': confidence_level,
                'percentile_5': np.percentile(final_values, 5),
                'percentile_95': np.percentile(final_values, 95),
                'time_horizon': time_horizon,
                'num_simulations': num_simulations
            }
    
    def _run_gbm_simulation(
        self,
        initial_value: float,
        mu: float,
        sigma: float,
        num_simulations: int,
        time_horizon: int,
        dt: float
    ) -> np.ndarray:
        """
        Ejecuta la simulación GBM.
        
        Returns:
            Array de forma (num_simulations, time_horizon+1) con las trayectorias
        """
        # Inicializar matriz de simulaciones
        simulations = np.zeros((num_simulations, time_horizon + 1))
        simulations[:, 0] = initial_value
        
        # Generar números aleatorios de distribución normal estándar
        Z = np.random.standard_normal((num_simulations, time_horizon))
        
        # Aplicar fórmula GBM
        for t in range(1, time_horizon + 1):
            drift = (mu - 0.5 * sigma**2) * dt
            diffusion = sigma * np.sqrt(dt) * Z[:, t-1]
            simulations[:, t] = simulations[:, t-1] * np.exp(drift + diffusion)
        
        return simulations
    
    def plot_montecarlo(
        self,
        simulation_results: Dict,
        filename: Optional[str] = None,
        show_plot: bool = True
    ):
        """
        Visualiza los resultados de la simulación Monte Carlo.
        
        Args:
            simulation_results: Resultados de montecarlo_simulation()
            filename: Ruta para guardar la imagen (opcional)
            show_plot: Si True, muestra el plot
        """
        plt.figure(figsize=(14, 8))
        
        if simulation_results['type'] == 'portfolio':
            simulations = simulation_results['simulations']
            
            # Plot todas las trayectorias (con transparencia)
            for i in range(simulations.shape[0]):
                plt.plot(simulations[i, :], color='skyblue', alpha=0.05, linewidth=0.5)
            
            # Calcular y plotear percentiles
            percentile_5 = np.percentile(simulations, 5, axis=0)
            percentile_95 = np.percentile(simulations, 95, axis=0)
            mean_trajectory = np.mean(simulations, axis=0)
            
            plt.plot(percentile_5, color='red', linewidth=2, label='Percentil 5% (Riesgo)', linestyle='--')
            plt.plot(percentile_95, color='green', linewidth=2, label='Percentil 95%', linestyle='--')
            plt.plot(mean_trajectory, color='darkblue', linewidth=2.5, label='Trayectoria Media')
            
            plt.title(f'Simulación Monte Carlo - Cartera ({simulation_results["num_simulations"]} simulaciones)', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('Días', fontsize=12)
            plt.ylabel('Valor de la Cartera ($)', fontsize=12)
            plt.legend(loc='best', fontsize=10)
            plt.grid(True, alpha=0.3)
            
            # Añadir información adicional
            textstr = f"Valor Inicial: ${simulation_results['initial_value']:.2f}\n"
            textstr += f"Valor Final Medio: ${simulation_results['mean_final_value']:.2f}\n"
            textstr += f"VaR ({simulation_results['confidence_level']*100:.0f}%): ${simulation_results['var']:.2f}\n"
            textstr += f"Pérdida Potencial: ${simulation_results['var_loss']:.2f}"
            
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=10,
                    verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if filename:
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Gráfico guardado en: {filename}")
        
        if show_plot:
            plt.show()
        
        plt.close()
    
    def report(self, filename: Optional[str] = None, show_warnings: bool = True) -> str:
        """
        Genera un reporte completo en formato Markdown.
        
        Args:
            filename: Ruta para guardar el archivo .md (opcional)
            show_warnings: Si True, incluye sección de advertencias
            
        Returns:
            String con el contenido del reporte en Markdown
        """
        md_content = []
        
        # Header
        md_content.append("# 📊 Reporte de Análisis de Cartera\n")
        md_content.append(f"**Fecha de generación:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_content.append("---\n")
        
        # Resumen Ejecutivo
        md_content.append("## 📈 Resumen Ejecutivo\n")
        annual_return = self.portfolio_return * 252
        annual_volatility = self.portfolio_volatility * np.sqrt(252)
        
        md_content.append(f"- **Rendimiento Anualizado:** {annual_return:.2%}")
        md_content.append(f"- **Volatilidad Anualizada:** {annual_volatility:.2%}")
        md_content.append(f"- **Número de Activos:** {len(self.components)}")
        md_content.append(f"- **Ratio de Sharpe de la Cartera:** {self.calculate_sharpe_ratio():.4f}\n")
        
        # Métricas Clave
        md_content.append("## 🎯 Métricas Clave\n")
        
        # Simular para obtener VaR
        mc_results = self.montecarlo_simulation(num_simulations=1000, time_horizon=252)
        
        md_content.append(f"- **Value at Risk (VaR 95%):** ${mc_results['var']:.2f}")
        md_content.append(f"- **Pérdida Potencial (VaR):** ${mc_results['var_loss']:.2f}")
        md_content.append(f"- **Valor Esperado (1 año):** ${mc_results['mean_final_value']:.2f}\n")
        
        # Análisis por Activo
        md_content.append("## 📊 Análisis por Activo\n")
        md_content.append("| Ticker | Peso | Rend. Anualizado | Volatilidad | Sharpe Ratio | CAGR |")
        md_content.append("|--------|------|------------------|-------------|--------------|------|")
        
        for ts in self.components:
            ticker = ts.ticker
            weight = self.weights[ticker]
            annual_ret = ts.mean_return * 252
            annual_vol = ts.stdev_return * np.sqrt(252)
            sharpe = ts.calculate_sharpe_ratio()
            cagr = ts.calculate_cagr()
            
            md_content.append(
                f"| {ticker} | {weight:.2%} | {annual_ret:.2%} | {annual_vol:.2%} | {sharpe:.4f} | {cagr:.2%} |"
            )
        
        md_content.append("")
        
        # Advertencias
        if show_warnings:
            md_content.append("## ⚠️ Advertencias y Consideraciones\n")
            warnings = []
            
            for ts in self.components:
                # Advertencia si menos de 1 año de datos
                days = (ts.data['Date'].iloc[-1] - ts.data['Date'].iloc[0]).days
                if days < 365:
                    warnings.append(f"- **{ts.ticker}:** Solo {days} días de datos históricos (<1 año)")
                
                # Advertencia si peso muy alto
                if self.weights[ts.ticker] > 0.5:
                    warnings.append(f"- **{ts.ticker}:** Peso muy concentrado ({self.weights[ts.ticker]:.1%})")
            
            # Advertencia de volatilidad extrema
            if annual_volatility > 0.4:
                warnings.append(f"- **Cartera:** Alta volatilidad ({annual_volatility:.1%}), riesgo elevado")
            
            if warnings:
                md_content.extend(warnings)
            else:
                md_content.append("✅ No se detectaron advertencias significativas.")
            
            md_content.append("")
        
        # Conclusión
        md_content.append("## 💡 Conclusión\n")
        md_content.append("### Resultados de Simulación Monte Carlo\n")
        md_content.append(f"Basado en {mc_results['num_simulations']} simulaciones a {mc_results['time_horizon']} días:\n")
        md_content.append(f"- **Escenario optimista (Percentil 95%):** ${mc_results['percentile_95']:.2f}")
        md_content.append(f"- **Escenario esperado (Media):** ${mc_results['mean_final_value']:.2f}")
        md_content.append(f"- **Escenario pesimista (Percentil 5%):** ${mc_results['percentile_5']:.2f}\n")
        
        if self.calculate_sharpe_ratio() > 1.0:
            md_content.append("✅ La cartera muestra un Sharpe Ratio favorable (>1.0), indicando buena compensación riesgo-retorno.")
        else:
            md_content.append("⚠️ El Sharpe Ratio es bajo (<1.0), considere revisar la composición de la cartera.")
        
        # Unir todo el contenido
        report = "\n".join(md_content)
        
        # Guardar si se especifica filename
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Reporte guardado en: {filename}")
        
        return report
    
    def plots_report(
        self,
        save_dir: Optional[str] = None,
        show_plots: bool = True
    ):
        """
        Genera todas las visualizaciones clave del portafolio.
        
        Args:
            save_dir: Directorio donde guardar las imágenes (opcional)
            show_plots: Si True, muestra los plots en pantalla
        """
        import os
        
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # 1. Simulación Monte Carlo
        print("🎲 Generando simulación Monte Carlo...")
        mc_results = self.montecarlo_simulation(num_simulations=1000, time_horizon=252)
        mc_filename = os.path.join(save_dir, 'montecarlo_simulation.png') if save_dir else None
        self.plot_montecarlo(mc_results, filename=mc_filename, show_plot=show_plots)
        
        # 2. Distribución de Rendimientos
        print("📊 Generando distribución de rendimientos...")
        self._plot_returns_distribution(save_dir, show_plots)
        
        # 3. Gráfico de Pesos
        print("🥧 Generando gráfico de pesos...")
        self._plot_weights(save_dir, show_plots)
        
        print("✅ Visualizaciones completadas")
    
    def _plot_returns_distribution(self, save_dir: Optional[str], show_plot: bool):
        """Genera histograma de distribución de rendimientos."""
        plt.figure(figsize=(12, 6))
        
        # Combinar todos los rendimientos de los componentes ponderados
        all_returns = []
        for ts in self.components:
            returns = ts.data['Log_Returns'].dropna() * self.weights[ts.ticker]
            all_returns.extend(returns.values)
        
        all_returns = np.array(all_returns)
        
        # Histograma
        plt.hist(all_returns, bins=50, alpha=0.7, color='steelblue', edgecolor='black', density=True)
        
        # Curva de distribución normal teórica
        mu, sigma = all_returns.mean(), all_returns.std()
        x = np.linspace(all_returns.min(), all_returns.max(), 100)
        from scipy.stats import norm
        plt.plot(x, norm.pdf(x, mu, sigma), 'r-', linewidth=2, label='Distribución Normal Teórica')
        
        plt.title('Distribución de Rendimientos de la Cartera', fontsize=14, fontweight='bold')
        plt.xlabel('Rendimiento Logarítmico', fontsize=12)
        plt.ylabel('Densidad', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_dir:
            filename = os.path.join(save_dir, 'returns_distribution.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"📊 Gráfico guardado en: {filename}")
        
        if show_plot:
            plt.show()
        
        plt.close()
    
    def _plot_weights(self, save_dir: Optional[str], show_plot: bool):
        """Genera gráfico de pesos de la cartera."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        tickers = list(self.weights.keys())
        weights = list(self.weights.values())
        colors = plt.cm.Set3(range(len(tickers)))
        
        # Gráfico de pastel
        ax1.pie(weights, labels=tickers, autopct='%1.1f%%', colors=colors, startangle=90)
        ax1.set_title('Distribución de Pesos (Pie Chart)', fontsize=12, fontweight='bold')
        
        # Gráfico de barras
        ax2.bar(tickers, weights, color=colors, edgecolor='black')
        ax2.set_title('Distribución de Pesos (Bar Chart)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Peso (%)', fontsize=10)
        ax2.set_xlabel('Ticker', fontsize=10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Formatear eje Y como porcentaje
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        
        plt.tight_layout()
        
        if save_dir:
            filename = os.path.join(save_dir, 'portfolio_weights.png')
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"🥧 Gráfico guardado en: {filename}")
        
        if show_plot:
            plt.show()
        
        plt.close()
    
    def __repr__(self) -> str:
        """Representación en string del Portfolio"""
        tickers = [ts.ticker for ts in self.components]
        return (f"Portfolio(components={len(self.components)}, tickers={tickers}, "
                f"return={self.portfolio_return:.6f}, volatility={self.portfolio_volatility:.6f})")