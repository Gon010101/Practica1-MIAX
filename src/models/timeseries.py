from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from typing import Optional, Dict, Tuple
from scipy import stats


@dataclass
class TimeSeries:
    """
    DataClass que encapsula una serie de precios históricos de un activo.
    Calcula automáticamente métricas estadísticas clave sobre los retornos.
    
    Las dos métricas fundamentales en finanzas:
    - media de retornos: mide el rendimiento esperado
    - desviación típica de retornos: mide el riesgo/volatilidad
    """
    
    ticker: str
    data: pd.DataFrame
    source: str
    period: str
    
    # Métricas calculadas automáticamente sobre los RETORNOS
    mean_return: float = field(init=False)      # Media de retornos diarios
    stdev_return: float = field(init=False)     # Desviación típica de retornos
    
    # Métricas adicionales calculadas automáticamente
    median_return: float = field(init=False)    # Mediana de retornos
    skewness: float = field(init=False)         # Asimetría de la distribución
    kurtosis: float = field(init=False)         # Curtosis (colas pesadas)
    min_return: float = field(init=False)       # Peor retorno diario
    max_return: float = field(init=False)       # Mejor retorno diario
    
    def __post_init__(self):
        """
        Calcula automáticamente las métricas estadísticas al inicializar el objeto.
        Se ejecuta después de __init__.
        
        Todas las métricas se calculan sobre los RETORNOS LOGARÍTMICOS,
        no sobre los precios brutos.
        """
        if 'Log_Returns' not in self.data.columns:
            raise ValueError("El DataFrame debe contener columna 'Log_Returns'")
        
        # Excluir NaN (el primer valor no tiene retorno)
        returns = self.data['Log_Returns'].dropna()
        
        # Validar que tenemos datos suficientes
        if len(returns) < 2:
            raise ValueError(f"Datos insuficientes para {self.ticker}: solo {len(returns)} retornos válidos")
        
        # Calcular métricas fundamentales (aplicadas automáticamente)
        self.mean_return = returns.mean()           # Rendimiento promedio
        self.stdev_return = returns.std()           # Riesgo/volatilidad
        
        # Calcular métricas adicionales
        self.median_return = returns.median()
        self.skewness = returns.skew()              # Asimetría
        self.kurtosis = returns.kurtosis()          # Curtosis
        self.min_return = returns.min()
        self.max_return = returns.max()
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
        """
        Calcula el Ratio de Sharpe del activo.
        
        Sharpe Ratio = (Rendimiento - Tasa Libre de Riesgo) / Volatilidad
        
        Mide el exceso de retorno por unidad de riesgo.
        Un Sharpe > 1 se considera bueno, > 2 excelente.
        
        Args:
            risk_free_rate: Tasa libre de riesgo anualizada (default: 2%)
            periods_per_year: Períodos de trading por año (default: 252 días)
            
        Returns:
            Ratio de Sharpe anualizado
        """
        # Anualizar rendimiento y volatilidad
        annual_return = self.mean_return * periods_per_year
        annual_volatility = self.stdev_return * np.sqrt(periods_per_year)
        
        # Calcular Sharpe Ratio
        if annual_volatility == 0:
            return 0.0
        
        sharpe = (annual_return - risk_free_rate) / annual_volatility
        return sharpe
    
    def calculate_cagr(self) -> float:
        """
        Calcula la Tasa de Crecimiento Anual Compuesta (CAGR).
        
        Formula: CAGR = (Precio_Final / Precio_Inicial)^(1/años) - 1
        
        Mide el crecimiento anual promedio asumiendo reinversión de ganancias.
        
        Returns:
            CAGR como decimal (ej. 0.15 = 15%)
        """
        if len(self.data) < 2:
            return 0.0
        
        initial_price = self.data['Close'].iloc[0]
        final_price = self.data['Close'].iloc[-1]
        
        # Calcular número de años
        days = (self.data['Date'].iloc[-1] - self.data['Date'].iloc[0]).days
        years = days / 365.25
        
        if years == 0 or initial_price <= 0:
            return 0.0
        
        cagr = (final_price / initial_price) ** (1 / years) - 1
        return cagr
    
    def calculate_sortino_ratio(self, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
        """
        Calcula el Ratio de Sortino (similar a Sharpe pero penaliza solo volatilidad negativa).
        
        Sortino Ratio = (Rendimiento - Tasa Libre de Riesgo) / Downside Deviation
        
        Es más apropiado que Sharpe cuando la distribución de retornos es asimétrica.
        
        Args:
            risk_free_rate: Tasa libre de riesgo anualizada
            periods_per_year: Períodos de trading por año
            
        Returns:
            Ratio de Sortino anualizado
        """
        returns = self.data['Log_Returns'].dropna()
        
        # Calcular downside deviation (solo retornos negativos)
        negative_returns = returns[returns < 0]
        downside_deviation = negative_returns.std()
        
        if downside_deviation == 0:
            return 0.0
        
        annual_return = self.mean_return * periods_per_year
        annual_downside = downside_deviation * np.sqrt(periods_per_year)
        
        sortino = (annual_return - risk_free_rate) / annual_downside
        return sortino
    
    def calculate_max_drawdown(self) -> Tuple[float, pd.Timestamp, pd.Timestamp]:
        """
        Calcula la máxima caída (drawdown) desde un pico histórico.
        
        El drawdown mide la mayor pérdida desde el máximo histórico.
        Es una medida importante de riesgo para inversores.
        
        Returns:
            Tupla con (max_drawdown, fecha_pico, fecha_valle)
        """
        prices = self.data['Close']
        
        # Calcular el máximo acumulativo
        running_max = prices.expanding().max()
        
        # Calcular drawdown en cada momento
        drawdown = (prices - running_max) / running_max
        
        # Encontrar el máximo drawdown
        max_dd = drawdown.min()
        max_dd_idx = drawdown.idxmin()
        
        # Encontrar el pico previo
        peak_idx = prices[:max_dd_idx].idxmax()
        
        return max_dd, self.data['Date'].iloc[peak_idx], self.data['Date'].iloc[max_dd_idx]
    
    def calculate_var(self, confidence_level: float = 0.95) -> float:
        """
        Calcula el Value at Risk (VaR) usando el método paramétrico.
        
        VaR indica la pérdida máxima esperada en un periodo con un nivel de confianza dado.
        Ejemplo: VaR 95% = -2.5% significa que en el 95% de los días la pérdida no superará 2.5%
        
        Args:
            confidence_level: Nivel de confianza (default: 0.95)
            
        Returns:
            VaR como decimal (valor negativo indica pérdida)
        """
        returns = self.data['Log_Returns'].dropna()
        
        # Método paramétrico (asume distribución normal)
        z_score = stats.norm.ppf(1 - confidence_level)
        var = self.mean_return + z_score * self.stdev_return
        
        return var
    
    def calculate_cvar(self, confidence_level: float = 0.95) -> float:
        """
        Calcula el Conditional Value at Risk (CVaR o Expected Shortfall).
        
        CVaR es la pérdida esperada cuando la pérdida excede el VaR.
        Es más conservador que VaR y mide el riesgo de cola.
        
        Args:
            confidence_level: Nivel de confianza
            
        Returns:
            CVaR como decimal (valor negativo)
        """
        returns = self.data['Log_Returns'].dropna()
        var = self.calculate_var(confidence_level)
        
        # CVaR es la media de los retornos peores que VaR
        cvar = returns[returns <= var].mean()
        
        return cvar
    
    def test_normality(self) -> Dict[str, any]:
        """
        Realiza test de normalidad sobre los retornos.
        
        Usa el test de Shapiro-Wilk para determinar si los retornos siguen
        una distribución normal (hipótesis crucial en muchos modelos financieros).
        
        Returns:
            Diccionario con resultados del test
        """
        returns = self.data['Log_Returns'].dropna()
        
        # Test de Shapiro-Wilk
        statistic, p_value = stats.shapiro(returns)
        
        # Si p-value < 0.05, rechazamos normalidad
        is_normal = p_value > 0.05
        
        return {
            'test': 'Shapiro-Wilk',
            'statistic': statistic,
            'p_value': p_value,
            'is_normal': is_normal,
            'interpretation': 'Normal' if is_normal else 'No Normal',
            'note': 'p-value > 0.05 indica normalidad'
        }
    
    def calculate_rolling_metrics(self, window: int = 20) -> pd.DataFrame:
        """
        Calcula métricas móviles (rolling) para análisis de tendencias.
        
        Args:
            window: Tamaño de la ventana en días (default: 20 días = 1 mes aprox)
            
        Returns:
            DataFrame con métricas móviles
        """
        returns = self.data['Log_Returns'].dropna()
        
        rolling_df = pd.DataFrame({
            'Date': self.data['Date'].iloc[1:].values,  # Excluir primer valor (NaN en returns)
            'Return': returns.values,
            'Rolling_Mean': returns.rolling(window=window).mean().values,
            'Rolling_Std': returns.rolling(window=window).std().values
        })
        
        # Calcular Sharpe móvil
        rolling_df['Rolling_Sharpe'] = (rolling_df['Rolling_Mean'] / rolling_df['Rolling_Std']) * np.sqrt(252)
        
        return rolling_df
    
    def get_summary(self) -> dict:
        """
        Retorna un diccionario con las métricas principales del activo.
        
        Returns:
            Diccionario con métricas clave
        """
        max_dd, peak_date, valley_date = self.calculate_max_drawdown()
        
        return {
            'Ticker': self.ticker,
            'Source': self.source,
            'Period': self.period,
            'Data Points': len(self.data),
            'Start Date': self.data['Date'].iloc[0].strftime('%Y-%m-%d'),
            'End Date': self.data['Date'].iloc[-1].strftime('%Y-%m-%d'),
            '─── RETORNOS ───': '─'*20,
            'Mean Daily Return': f"{self.mean_return:.6f}",
            'Median Daily Return': f"{self.median_return:.6f}",
            'Daily Volatility (Std)': f"{self.stdev_return:.6f}",
            'Min Daily Return': f"{self.min_return:.6f}",
            'Max Daily Return': f"{self.max_return:.6f}",
            '─── ANUALIZADOS ───': '─'*20,
            'Annualized Return': f"{self.mean_return * 252:.4f} ({self.mean_return * 252:.2%})",
            'Annualized Volatility': f"{self.stdev_return * np.sqrt(252):.4f} ({self.stdev_return * np.sqrt(252):.2%})",
            'CAGR': f"{self.calculate_cagr():.4f} ({self.calculate_cagr():.2%})",
            '─── RATIOS ───': '─'*20,
            'Sharpe Ratio': f"{self.calculate_sharpe_ratio():.4f}",
            'Sortino Ratio': f"{self.calculate_sortino_ratio():.4f}",
            '─── RIESGO ───': '─'*20,
            'Max Drawdown': f"{max_dd:.2%}",
            'VaR (95%)': f"{self.calculate_var(0.95):.6f}",
            'CVaR (95%)': f"{self.calculate_cvar(0.95):.6f}",
            '─── DISTRIBUCIÓN ───': '─'*20,
            'Skewness': f"{self.skewness:.4f}",
            'Kurtosis': f"{self.kurtosis:.4f}",
            'Normality Test': self.test_normality()['interpretation']
        }
    
    def __repr__(self) -> str:
        """Representación en string del objeto"""
        return (f"TimeSeries(ticker='{self.ticker}', source='{self.source}', "
                f"periods={len(self.data)}, mean_return={self.mean_return:.6f}, "
                f"stdev={self.stdev_return:.6f})")