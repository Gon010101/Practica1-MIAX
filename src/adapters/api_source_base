from abc import ABC, abstractmethod
import pandas as pd


class APISourceBase(ABC):
    """
    Clase base abstracta que define el contrato para todos los adaptadores.
    Garantiza que cualquier fuente de datos devuelva información estandarizada.
    """
    
    STANDARD_COLUMNS = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    
    @abstractmethod
    def fetch_data(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Extrae datos históricos de un ticker y los devuelve en formato estandarizado.
        
        Args:
            ticker: Símbolo del activo (ej. 'AAPL', 'MSFT')
            start_date: Fecha inicio en formato 'YYYY-MM-DD'
            end_date: Fecha fin en formato 'YYYY-MM-DD'
            
        Returns:
            DataFrame con columnas: Date, Open, High, Low, Close, Volume
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """Retorna el nombre identificador de la fuente de datos"""
        pass
    
    def validate_output(self, df: pd.DataFrame) -> bool:
        """
        Valida que el DataFrame de salida cumpla con el formato estándar.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            True si el formato es correcto, False en caso contrario
        """
        if df is None or df.empty:
            return False
        
        # Verificar columnas requeridas
        required_cols = set(self.STANDARD_COLUMNS)
        actual_cols = set(df.columns)
        
        return required_cols.issubset(actual_cols)