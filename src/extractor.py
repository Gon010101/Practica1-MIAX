from typing import List, Dict, Optional
from src.adapters import APISourceBase
from src.adapters.yahoo_adapter import YahooAdapter
from src.adapters.investing_adapter import InvestingAdapter
from src.models.timeseries import TimeSeries
from src.models.portfolio import Portfolio
from src.processing import preprocess_financial_data
import numpy as np


class Extractor:
    """
    Clase principal para extraer y gestionar datos financieros.
    Coordina los adaptadores y la creación de objetos TimeSeries y Portfolio.
    """
    
    def __init__(self, default_source: str = 'yahoo'):
        """
        Inicializa el extractor con una fuente por defecto.
        
        Args:
            default_source: Fuente de datos por defecto ('yahoo' o 'investing')
        """
        self.adapters = {
            'yahoo': YahooAdapter(),
            'investing': InvestingAdapter()
        }
        
        if default_source not in self.adapters:
            raise ValueError(f"Fuente '{default_source}' no disponible. Use: {list(self.adapters.keys())}")
        
        self.default_source = default_source
        self.current_adapter = self.adapters[default_source]
    
    def set_source(self, source: str):
        """
        Cambia la fuente de datos activa.
        
        Args:
            source: Nombre de la fuente ('yahoo' o 'investing')
        """
        if source not in self.adapters:
            raise ValueError(f"Fuente '{source}' no disponible. Use: {list(self.adapters.keys())}")
        
        self.default_source = source
        self.current_adapter = self.adapters[source]
        print(f"✅ Fuente cambiada a: {self.current_adapter.get_source_name()}")
    
    def get_historical_data(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        source: str = None,
        columns: Optional[List[str]] = None
    ) -> List[TimeSeries]:
        """
        Extrae datos históricos para una lista de tickers.
        
        Args:
            tickers: Lista de símbolos de activos (ej. ['AAPL', 'MSFT'])
            start_date: Fecha inicio 'YYYY-MM-DD'
            end_date: Fecha fin 'YYYY-MM-DD'
            source: Fuente específica a usar (opcional, usa default si no se especifica)
            columns: Lista de columnas a incluir (opcional). 
                     Si None, incluye todas: ['Open', 'High', 'Low', 'Close', 'Volume']
            
        Returns:
            Lista de objetos TimeSeries, uno por cada ticker
        """
        # Seleccionar adaptador
        adapter = self.adapters[source] if source else self.current_adapter
        
        # Si no se especifican columnas, usar todas
        if columns is None:
            columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Asegurar que 'Close' esté incluido (necesario para cálculos)
        if 'Close' not in columns:
            columns.append('Close')
        
        timeseries_list = []
        
        for ticker in tickers:
            try:
                print(f"📥 Extrayendo datos de {ticker} desde {adapter.get_source_name()}...")
                
                # Extraer datos crudos mediante el adaptador
                raw_data = adapter.fetch_data(ticker, start_date, end_date)
                
                # Filtrar solo las columnas solicitadas (más Date)
                columnas_a_mantener = ['Date'] + [col for col in columns if col in raw_data.columns]
                raw_data = raw_data[columnas_a_mantener]
                
                # Preprocesar datos
                processed_data, warnings = preprocess_financial_data(raw_data)
                
                # Mostrar advertencias si las hay
                for warning in warnings:
                    if not warning.startswith("✅"):
                        print(f"  ⚠️  {warning}")
                
                # Crear objeto TimeSeries
                period = f"{start_date} to {end_date}"
                ts = TimeSeries(
                    ticker=ticker,
                    data=processed_data,
                    source=adapter.get_source_name(),
                    period=period
                )
                
                timeseries_list.append(ts)
                print(f"  ✅ {ticker}: {len(processed_data)} datos extraídos")
                
            except Exception as e:
                print(f"  ❌ Error con {ticker}: {str(e)}")
                continue
        
        if not timeseries_list:
            raise RuntimeError("No se pudo extraer datos de ningún ticker")
        
        print(f"\n✅ Extracción completada: {len(timeseries_list)}/{len(tickers)} activos exitosos\n")
        return timeseries_list
    
    def create_portfolio(
        self,
        tickers: List[str],
        weights: Dict[str, float],
        start_date: str,
        end_date: str,
        source: str = None
    ) -> Portfolio:
        """
        Crea un objeto Portfolio extrayendo los datos y asignando pesos.
        
        Args:
            tickers: Lista de símbolos de activos
            weights: Diccionario con pesos por ticker {ticker: peso}
            start_date: Fecha inicio 'YYYY-MM-DD'
            end_date: Fecha fin 'YYYY-MM-DD'
            source: Fuente de datos (opcional)
            
        Returns:
            Objeto Portfolio configurado
        """
        # Validar que todos los tickers tengan peso asignado
        if set(tickers) != set(weights.keys()):
            raise ValueError("Los tickers y los pesos no coinciden")
        
        # Extraer datos (todas las columnas para portfolio)
        timeseries_list = self.get_historical_data(
            tickers, 
            start_date, 
            end_date, 
            source,
            columns=['Open', 'High', 'Low', 'Close', 'Volume']
        )
        
        # Crear portfolio
        portfolio = Portfolio(components=timeseries_list, weights=weights)
        
        print(f"📊 Portfolio creado con {len(portfolio.components)} activos")
        print(f"   Rendimiento esperado: {portfolio.portfolio_return * 252:.2%} anual")
        print(f"   Volatilidad: {portfolio.portfolio_volatility * np.sqrt(252):.2%} anual")
        print(f"   Sharpe Ratio: {portfolio.calculate_sharpe_ratio():.4f}\n")
        
        return portfolio
    
    def quick_analysis(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        source: str = None
    ):
        """
        Realiza un análisis rápido de un solo activo y muestra las métricas.
        
        Args:
            ticker: Símbolo del activo
            start_date: Fecha inicio
            end_date: Fecha fin
            source: Fuente de datos (opcional)
        """
        timeseries_list = self.get_historical_data([ticker], start_date, end_date, source)
        
        if not timeseries_list:
            print("❌ No se pudo realizar el análisis")
            return
        
        ts = timeseries_list[0]
        summary = ts.get_summary()
        
        print(f"\n{'='*60}")
        print(f"  ANÁLISIS RÁPIDO: {ticker}")
        print(f"{'='*60}")
        
        for key, value in summary.items():
            print(f"  {key:.<30} {value}")
        
        print(f"{'='*60}\n")