import yfinance as yf
import pandas as pd
from .api_source_base import APISourceBase


class YahooAdapter(APISourceBase):
    """
    Adaptador para Yahoo Finance (yfinance).
    Mapea las columnas de Yahoo Finance al formato estándar.
    """
    
    def fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Extrae datos históricos desde Yahoo Finance y los estandariza.
        
        Mapeo de columnas:
        - Adj Close → Close (usamos el precio ajustado como precio de cierre)
        - Fecha (índice) → Date (columna)
        """
        try:
            # Descargar datos usando yfinance
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if data.empty:
                raise ValueError(f"No se encontraron datos para {ticker}")
            
            # Manejar MultiIndex columns (cuando se descarga un solo ticker, a veces viene con MultiIndex)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
            
            # Verificar si existe 'Adj Close', si no usar 'Close'
            close_column = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
            
            # Crear DataFrame estandarizado
            standardized_df = pd.DataFrame({
                'Date': data.index,
                'Open': data['Open'].values,
                'High': data['High'].values,
                'Low': data['Low'].values,
                'Close': data[close_column].values,  # Usamos Adj Close si existe
                'Volume': data['Volume'].values
            })
            
            # Resetear índice para que Date sea una columna
            standardized_df.reset_index(drop=True, inplace=True)
            
            # Validar salida
            if not self.validate_output(standardized_df):
                raise ValueError(f"Error en validación de formato para {ticker}")
            
            return standardized_df
            
        except Exception as e:
            raise RuntimeError(f"Error extrayendo datos de Yahoo Finance para {ticker}: {str(e)}")
    
    def get_source_name(self) -> str:
        return "Yahoo Finance"