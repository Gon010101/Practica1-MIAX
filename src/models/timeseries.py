from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from typing import Optional


@dataclass
class TimeSeries:
    """
    DataClass que encapsula una serie de precios históricos de un activo.
    Calcula automáticamente métricas estadísticas clave.
    """
    
    ticker: str
    data: pd.DataFrame
    source: str
    period: str
    
    # Métricas calculadas automáticamente
    mean_return: float = field(init=False)
    stdev_return: float = field(init=False)
    
    def __post_init__(self):
        """
        Calcula automáticamente las métricas estadísticas al inicializar el objeto.
        Se ejecuta después de __init__.
        """
        if 'Log_Returns' not in self.data.columns:
            raise ValueError("El DataFrame debe contener columna 'Log_Returns'")
        
        # Calcular media y desviación típica de los rendimientos
        # Excluimos NaN (el primer valor)
        returns = self.data['Log_Returns'].dropna()
        
        self.mean_return = returns.mean()
        self.stdev_return = returns.std()
        
        # Validar que tenemos datos suficientes
        if len(returns) < 2:
            raise ValueError(f"Datos insuficientes para {self.ticker}: solo {len(returns)} retornos válidos")
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.02, periods_per_year: int = 252) -> float:
        """
        Calcula el Ratio de Sharpe del activo.
        
        Sharpe Ratio = (Rendimiento - Tasa Libre de Riesgo) / Volatilidad
        
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
    
    def get_summary(self) -> dict:
        """
        Retorna un diccionario con las métricas principales del activo.
        
        Returns:
            Diccionario con métricas clave
        """
        return {
            'Ticker': self.ticker,
            'Source': self.source,
            'Period': self.period,
            'Data Points': len(self.data),
            'Start Date': self.data['Date'].iloc[0].strftime('%Y-%m-%d'),
            'End Date': self.data['Date'].iloc[-1].strftime('%Y-%m-%d'),
            'Mean Daily Return': f"{self.mean_return:.6f}",
            'Daily Volatility': f"{self.stdev_return:.6f}",
            'Annualized Return': f"{self.mean_return * 252:.4f}",
            'Annualized Volatility': f"{self.stdev_return * np.sqrt(252):.4f}",
            'Sharpe Ratio': f"{self.calculate_sharpe_ratio():.4f}",
            'CAGR': f"{self.calculate_cagr():.4f}"
        }
    
    def __repr__(self) -> str:
        """Representación en string del objeto"""
        return (f"TimeSeries(ticker='{self.ticker}', source='{self.source}', "
                f"periods={len(self.data)}, mean_return={self.mean_return:.6f}, "
                f"stdev={self.stdev_return:.6f})")