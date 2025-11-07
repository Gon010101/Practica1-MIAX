import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .api_source_base import APISourceBase 


class InvestingAdapter(APISourceBase):
    """
    Adaptador simulado para Investing.com.
    Genera datos sintéticos para demostración del patrón adaptador.
    """
    
    def fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Simula la extracción de datos de Investing.com.
        Genera datos sintéticos con columnas en español que luego mapea al estándar.
        
        Mapeo simulado:
        - Fecha → Date
        - Precio_Apertura → Open
        - Precio_Maximo → High
        - Precio_Minimo → Low
        - Precio_Cierre → Close
        - Volumen → Volume
        """
        try:
            # Convertir fechas
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Generar fechas (solo días laborables)
            dates = pd.bdate_range(start=start, end=end)
            n_days = len(dates)
            
            if n_days == 0:
                raise ValueError(f"No hay días válidos entre {start_date} y {end_date}")
            
            # Simular datos de precios (random walk con drift)
            np.random.seed(hash(ticker) % (2**32))  # Seed basado en ticker para reproducibilidad
            
            initial_price = 100.0
            returns = np.random.normal(0.0005, 0.02, n_days)  # Drift pequeño, volatilidad 2%
            prices = initial_price * np.exp(np.cumsum(returns))
            
            # Generar datos OHLC realistas
            daily_volatility = 0.01
            opens = prices * (1 + np.random.normal(0, daily_volatility, n_days))
            highs = np.maximum(opens, prices) * (1 + np.abs(np.random.normal(0, daily_volatility/2, n_days)))
            lows = np.minimum(opens, prices) * (1 - np.abs(np.random.normal(0, daily_volatility/2, n_days)))
            closes = prices
            volumes = np.random.randint(1000000, 10000000, n_days)
            
            # Crear DataFrame con columnas en español (simulando API de Investing)
            raw_data = pd.DataFrame({
                'Fecha': dates,
                'Precio_Apertura': opens,
                'Precio_Maximo': highs,
                'Precio_Minimo': lows,
                'Precio_Cierre': closes,
                'Volumen': volumes
            })
            
            # Mapear al formato estándar
            standardized_df = pd.DataFrame({
                'Date': raw_data['Fecha'],
                'Open': raw_data['Precio_Apertura'],
                'High': raw_data['Precio_Maximo'],
                'Low': raw_data['Precio_Minimo'],
                'Close': raw_data['Precio_Cierre'],
                'Volume': raw_data['Volumen']
            })
            
            standardized_df.reset_index(drop=True, inplace=True)
            
            # Validar salida
            if not self.validate_output(standardized_df):
                raise ValueError(f"Error en validación de formato para {ticker}")
            
            return standardized_df
            
        except Exception as e:
            raise RuntimeError(f"Error en simulación Investing para {ticker}: {str(e)}")
    
    def get_source_name(self) -> str:
        return "Investing.com (Simulado)"