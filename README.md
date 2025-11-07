# 📊 Financial Extractor Project

Sistema modular de análisis financiero que extrae datos históricos de múltiples fuentes, calcula métricas estadísticas avanzadas, simula escenarios mediante Monte Carlo y genera reportes automatizados.

## 🎯 Características Principales

- *Extracción Multi-Fuente*: Adaptadores para Yahoo Finance y otras APIs (patrón Adapter)
- *Análisis Estadístico*: Cálculo automático de métricas (Sharpe Ratio, CAGR, volatilidad)
- *Simulación Monte Carlo*: Proyecciones usando Movimiento Browniano Geométrico (GBM)
- *Gestión de Portfolios*: Análisis de carteras diversificadas con matriz de covarianza
- *Reportes Automatizados*: Generación de documentos Markdown y visualizaciones
- *Preprocesamiento Robusto*: Limpieza de datos, detección de inconsistencias

## 📁 Estructura del Proyecto


Financial_Extractor_Project/
├── src/
│   ├── adapters/              # Módulo 1: Adaptadores de APIs
│   │   ├── __init__.py        # Clase base abstracta APISourceBase
│   │   ├── yahoo_adapter.py   # Adaptador para yfinance
│   │   └── investing_adapter.py # Adaptador simulado para Investing.com
│   ├── models/                # Módulo 2: Estructuras de datos
│   │   ├── __init__.py
│   │   ├── timeseries.py      # DataClass para series de precios
│   │   └── portfolio.py       # DataClass para carteras
│   ├── extractor.py           # Módulo 3: Clase principal Extractor
│   └── processing.py          # Módulo 4: Funciones de preprocesado
├── main.py                    # Punto de entrada con demos
├── requirements.txt           # Dependencias
├── .gitignore
└── README.md


## 🚀 Instalación

### 1. Clonar el repositorio

bash
git clone <repository-url>
cd Financial_Extractor_Project


### 2. Crear entorno virtual (recomendado)

bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate


### 3. Instalar dependencias

bash
pip install -r requirements.txt


## 📖 Uso Rápido

### Ejecutar demos interactivas

bash
python main.py


Esto mostrará un menú con 4 demos predefinidas:

1. *Análisis Rápido*: Análisis estadístico de un solo activo
2. *Portfolio Diversificado*: Creación y análisis completo de cartera
3. *Monte Carlo Avanzado*: Simulaciones con diferentes horizontes temporales
4. *Comparación de Fuentes*: Validación de datos entre fuentes

### Ejemplo de código básico

python
from src.extractor import Extractor

# Inicializar extractor
extractor = Extractor(default_source='yahoo')

# Análisis rápido de un activo
extractor.quick_analysis('AAPL', '2022-01-01', '2024-01-01')

# Crear portfolio
tickers = ['AAPL', 'MSFT', 'GOOGL']
weights = {'AAPL': 0.4, 'MSFT': 0.3, 'GOOGL': 0.3}

portfolio = extractor.create_portfolio(
    tickers, weights,
    start_date='2022-01-01',
    end_date='2024-01-01'
)

# Generar reporte
portfolio.report(filename='mi_portfolio.md')

# Simulación Monte Carlo
results = portfolio.montecarlo_simulation(
    num_simulations=1000,
    time_horizon=252
)

# Visualizar
portfolio.plot_montecarlo(results, filename='simulacion.png')


## 🏗 Arquitectura del Sistema

### 1. Patrón Adaptador (Módulo adapters/)

Estandariza datos de diferentes APIs al formato común:

| Columna | Descripción |
|---------|-------------|
| Date | Fecha del registro |
| Open | Precio de apertura |
| High | Precio máximo |
| Low | Precio mínimo |
| Close | Precio de cierre |
| Volume | Volumen negociado |

*Clase Base*: APISourceBase  
*Implementaciones*: YahooAdapter, InvestingAdapter

### 2. DataClasses (Módulo models/)

#### TimeSeries

Encapsula una serie temporal de precios con cálculo automático de:

- *Media de rendimientos* (mean_return)
- *Volatilidad* (stdev_return)
- *Sharpe Ratio*: (Rendimiento - Tasa Libre Riesgo) / Volatilidad
- *CAGR*: Tasa de crecimiento anual compuesta

#### Portfolio

Gestiona carteras de inversión:

- *Pesos normalizados*: Suma = 1
- *Matriz de covarianza*: Correlación entre activos
- *Métricas agregadas*: Rendimiento y volatilidad de la cartera
- *Simulación Monte Carlo*: Proyecciones probabilísticas

### 3. Simulación Monte Carlo

Implementa *Movimiento Browniano Geométrico (GBM)*:

$$S_t = S_{t-1} \cdot e^{(\mu - \frac{1}{2}\sigma^2)\Delta t + \sigma \sqrt{\Delta t} Z}$$

Donde:
- $S_t$: Precio futuro
- $\mu$: Media de rendimientos (drift)
- $\sigma$: Volatilidad
- $Z$: Variable aleatoria normal estándar

*Parámetros configurables*:
- num_simulations: Número de trayectorias (default: 1000)
- time_horizon: Períodos a simular (default: 252 días)
- confidence_level: Nivel de confianza para VaR (default: 0.95)

### 4. Preprocesamiento (Módulo processing.py)

Pipeline automático:

1. *clean_nans()*: Relleno/eliminación de valores faltantes
2. *check_consistency()*: Validación de fechas (duplicados, orden)
3. *calculate_log_returns()*: Cálculo de rendimientos logarítmicos
4. *validate_dataframe()*: Verificación de requisitos mínimos

## 📊 Reportes y Visualizaciones

### Reporte Markdown

El método Portfolio.report() genera un documento con:

- *Resumen Ejecutivo*: Métricas clave de la cartera
- *Análisis por Activo*: Tabla comparativa de componentes
- *Resultados Monte Carlo*: Escenarios optimista/esperado/pesimista
- *Advertencias*: Detección automática de riesgos

### Visualizaciones

El método Portfolio.plots_report() genera:

1. *Simulación Monte Carlo*: 
   - Todas las trayectorias
   - Percentiles 5% y 95%
   - Trayectoria media

2. *Distribución de Rendimientos*:
   - Histograma de frecuencias
   - Curva normal teórica

3. *Composición del Portfolio*:
   - Gráfico de pastel (pie chart)
   - Gráfico de barras

## 🧪 Casos de Uso

### 1. Comparar estrategias de inversión

python
# Estrategia conservadora
portfolio_conservador = extractor.create_portfolio(
    ['SPY', 'BND', 'GLD'],  # Acciones, Bonos, Oro
    {'SPY': 0.5, 'BND': 0.3, 'GLD': 0.2},
    start_date, end_date
)

# Estrategia agresiva
portfolio_agresivo = extractor.create_portfolio(
    ['TSLA', 'NVDA', 'ARKK'],  # Tech de alto crecimiento
    {'TSLA': 0.4, 'NVDA': 0.4, 'ARKK': 0.2},
    start_date, end_date
)

# Comparar Sharpe Ratios
print(f"Conservador: {portfolio_conservador.calculate_sharpe_ratio():.4f}")
print(f"Agresivo: {portfolio_agresivo.calculate_sharpe_ratio():.4f}")


### 2. Análisis de riesgo (VaR)

python
results = portfolio.montecarlo_simulation(
    num_simulations=10000,
    time_horizon=252,
    confidence_level=0.99  # VaR 99%
)

print(f"Con 99% confianza, pérdida máxima: ${results['var_loss']:.2f}")


### 3. Backtesting de pesos

python
# Probar diferentes asignaciones
weights_scenarios = [
    {'AAPL': 0.5, 'MSFT': 0.5},
    {'AAPL': 0.7, 'MSFT': 0.3},
    {'AAPL': 0.3, 'MSFT': 0.7}
]

for weights in weights_scenarios:
    pf = Portfolio(components, weights)
    print(f"{weights} -> Sharpe: {pf.calculate_sharpe_ratio():.4f}")


## ⚙ Configuración Avanzada

### Cambiar fuente de datos

python
extractor = Extractor(default_source='yahoo')
extractor.set_source('investing')  # Cambiar a Investing.com


### Tasa libre de riesgo personalizada

python
sharpe = portfolio.calculate_sharpe_ratio(risk_free_rate=0.04)  # 4%


### Períodos de trading personalizados

python
# Para datos semanales (52 semanas/año)
sharpe = timeseries.calculate_sharpe_ratio(periods_per_year=52)


## 🔧 Extensibilidad

### Añadir un nuevo adaptador

1. Crear clase en src/adapters/:

python
from src.adapters import APISourceBase

class NuevoAdapter(APISourceBase):
    def fetch_data(self, ticker, start_date, end_date):
        # Implementar extracción
        raw_data = tu_api.obtener_datos(ticker)
        
        # Mapear a formato estándar
        return pd.DataFrame({
            'Date': raw_data['fecha'],
            'Open': raw_data['apertura'],
            # ... resto de columnas
        })
    
    def get_source_name(self):
        return "Mi Nueva Fuente"


2. Registrar en Extractor:

python
self.adapters['mi_fuente'] = NuevoAdapter()


## 📚 Fundamentos Matemáticos

### Rendimientos Logarítmicos

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

*Ventajas*:
- Aditivos: $r_{total} = \sum r_i$
- Simétricos: pérdida de 50% ≠ ganancia de 50%
- Distribución aproximadamente normal

### Ratio de Sharpe

$$\text{Sharpe} = \frac{E[R_p] - R_f}{\sigma_p}$$

*Interpretación*:
- < 1: Rendimiento insuficiente por riesgo
- 1-2: Bueno
- 2-3: Muy bueno
- \> 3: Excelente

### Volatilidad del Portfolio

$$\sigma_p = \sqrt{w^T \Sigma w}$$

Donde:
- $w$: Vector de pesos
- $\Sigma$: Matriz de covarianza

## 🐛 Troubleshooting

### Error: "No data found for this date range"

*Solución*: El ticker no existe o las fechas son inválidas. Verificar:
python
import yfinance as yf
yf.Ticker('SIMBOLO').info  # Comprobar si existe


### Advertencia: "Datos insuficientes (<30 días)"

*Solución*: Ampliar rango de fechas o usar activos con más historia.

### Error: "Los pesos no suman 1"

*Solución*: El sistema normaliza automáticamente, pero verificar:
python
assert sum(weights.values()) > 0.99


## 🤝 Contribuciones

Este proyecto es un framework educativo. Para contribuir:

1. Fork el repositorio
2. Crear branch de feature (git checkout -b feature/nueva-funcionalidad)
3. Commit cambios (git commit -m 'Añadir nueva funcionalidad')
4. Push al branch (git push origin feature/nueva-funcionalidad)
5. Abrir Pull Request

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

## 📧 Contacto

Para preguntas o sugerencias, abrir un issue en GitHub.


