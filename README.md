# 📊 Financial Extractor - Sistema de Análisis Financiero

Sistema interactivo de análisis financiero que extrae datos históricos de múltiples fuentes, calcula métricas estadísticas avanzadas y realiza simulaciones Monte Carlo para análisis de riesgo.

## 🚀 Inicio Rápido

### 1. Instalación y ejecución

```bash
# Entrar al directorio del proyecto
cd PRACTICA1

# Crear entorno virtual (recomendado)
python -m venv env

# Activar entorno virtual
# Windows:
env\Scripts\activate
# Linux/Mac:
source env/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Ejecutar

```bash
python -m src.main
```

¡Eso es todo! El programa te guiará con menús interactivos.

---

## 📁 Estructura del Proyecto

```
PRACTICA1/
├── src/
│   ├── adapters/           # Extracción de datos de diferentes fuentes
│   │   ├── api_source_base.py
│   │   ├── yahoo_adapter.py
│   │   └── investing_adapter.py
│   ├── models/            # Modelos de datos
│   │   ├── timeseries.py  # Métricas de activos individuales
│   │   └── portfolio.py   # Análisis de carteras
│   ├── extractor.py       # Coordinador principal
│   ├── processing.py      # Limpieza y preprocesado
│   └── main.py           # Interfaz interactiva
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🎯 ¿Qué Puedes Hacer?

### 1️⃣ Analizar Activos Individuales

Extrae y analiza datos históricos de acciones:

```
📊 FINANCIAL EXTRACTOR
  1. Información de activos        ← Elige esto
  2. Análisis de cartera
  0. Salir
```

**El sistema te preguntará:**
- ¿Qué activos? (Ej: `AAPL, MSFT, GOOGL`)
- ¿Qué periodo? (Ej: `2022-01-01` a `2024-01-01`)
- ¿Qué datos? (Precio, volumen, etc.)
- ¿Qué fuente? (Yahoo Finance o simulado)

**Obtendrás:**
- Datos históricos en tabla
- Estadísticas completas (Sharpe Ratio, VaR, CAGR, etc.)
- Opción de guardar en CSV

### 2️⃣ Crear y Analizar Carteras

Analiza portfolios con múltiples activos:

```
📊 FINANCIAL EXTRACTOR
  1. Información de activos
  2. Análisis de cartera           ← Elige esto
  0. Salir
```

**Configurarás:**
- Activos de tu cartera (Ej: `AAPL, MSFT`)
- Pesos de cada activo (Ej: `60%, 40%`)
- Periodo de análisis

**Podrás:**
1. Ver métricas de la cartera (rendimiento, volatilidad, Sharpe)
2. **Simulación Monte Carlo** (predicción probabilística)
3. Generar reporte completo en Markdown
4. Crear visualizaciones (gráficos de riesgo, distribuciones)

---

## 🎲 Simulación Monte Carlo

La funcionalidad estrella del sistema. Proyecta miles de escenarios futuros:

```
🎲 SIMULACIÓN MONTE CARLO
🔢 Número de simulaciones: 5000
📅 Horizonte temporal: 252  (días = 1 año)

✅ Simulación completada

  Valor inicial:              $    10000.00
  Valor esperado (media):     $    10850.23
  Percentil 5% (pesimista):   $     8234.56
  Percentil 95% (optimista):  $    13892.11
  VaR (95%):                  $     8500.00
  Pérdida potencial:          $     1500.00
```

**Genera un gráfico mostrando:**
- Todas las trayectorias simuladas
- Escenario pesimista (línea roja)
- Escenario esperado (línea azul)
- Escenario optimista (línea verde)

---

## 📈 Métricas Calculadas

### Para Activos Individuales (TimeSeries)

| Métrica | Descripción |
|---------|-------------|
| **Sharpe Ratio** | Rendimiento ajustado por riesgo (>1 bueno, >2 excelente) |
| **Sortino Ratio** | Como Sharpe pero solo penaliza volatilidad negativa |
| **CAGR** | Tasa de crecimiento anual compuesta |
| **Max Drawdown** | Mayor pérdida desde un pico histórico |
| **VaR (95%)** | Pérdida máxima esperada con 95% confianza |
| **CVaR** | Pérdida esperada en el peor 5% de casos |
| **Skewness** | Asimetría de la distribución de retornos |
| **Kurtosis** | "Colas pesadas" (probabilidad de eventos extremos) |

### Para Carteras (Portfolio)

- **Rendimiento de la cartera** (ponderado por pesos)
- **Volatilidad de la cartera** (considera correlaciones)
- **Matriz de covarianza** (correlaciones entre activos)
- **Simulación Monte Carlo** con VaR del portfolio

---

## 💡 Casos de Uso

### Ejemplo 1: Comparar Dos Acciones

```bash
python -m src.main
# 1. Información de activos
# Tickers: AAPL, TSLA
# Periodo: 2023-01-01 a 2024-01-01
# Ver resumen estadístico
```

Compara Sharpe Ratios, volatilidades y CAGR para decidir cuál es mejor inversión.

### Ejemplo 2: Evaluar Riesgo de tu Portfolio

```bash
python -m src.main
# 2. Análisis de cartera
# Tickers: AAPL, MSFT, GOOGL
# Pesos: 50%, 30%, 20%
# Opción 2: Simulación Monte Carlo
```

Descubre cuál es tu pérdida máxima probable (VaR) y los escenarios optimista/pesimista.

### Ejemplo 3: Generar Reporte para Cliente

```bash
python -m src.main
# 2. Análisis de cartera
# [Configura tu cartera]
# Opción 3: Generar reporte completo
# Archivo: informe_cliente.md
```

Crea un documento profesional con todas las métricas y recomendaciones.

---

## 🔧 Arquitectura Técnica

### 1. Patrón Adaptador

Estandariza datos de diferentes fuentes:

```python
APISourceBase (abstracta)
    ├── YahooAdapter      # Yahoo Finance (real)
    └── InvestingAdapter  # Simulado (demo)
```

**Todas las fuentes devuelven:**
```
Date | Open | High | Low | Close | Volume
```

### 2. DataClasses con Cálculo Automático

```python
@dataclass
class TimeSeries:
    ticker: str
    data: pd.DataFrame
    
    # Se calculan automáticamente al crear el objeto:
    mean_return: float      # ✅ Auto
    stdev_return: float     # ✅ Auto
    sharpe_ratio()          # Método
    
@dataclass  
class Portfolio:
    components: List[TimeSeries]
    weights: Dict[str, float]
    
    # Se calculan automáticamente:
    portfolio_return: float     # ✅ Auto
    portfolio_volatility: float # ✅ Auto
    montecarlo_simulation()     # Método
```

### 3. Simulación Monte Carlo (GBM)

Implementa **Movimiento Browniano Geométrico**:

$$S_t = S_{t-1} \cdot \exp\left[(\mu - \frac{\sigma^2}{2})\Delta t + \sigma\sqrt{\Delta t} \cdot Z\right]$$

Donde:
- $S_t$: Precio en tiempo t
- $\mu$: Rendimiento medio (drift)
- $\sigma$: Volatilidad
- $Z \sim N(0,1)$: Variable aleatoria normal

---

## 📊 Salidas del Sistema

### 1. Datos Tabulares (CSV)

```
Date,Open,High,Low,Close,Volume
2023-01-03,125.07,125.42,124.17,125.07,112117500
2023-01-04,126.89,128.66,125.08,126.36,89113600
...
```

### 2. Reportes Markdown

```markdown
# 📊 Reporte de Análisis de Cartera

## 📈 Resumen Ejecutivo
- Rendimiento Anualizado: 15.24%
- Volatilidad Anualizada: 22.31%
- Ratio de Sharpe: 0.6832

## 🎯 Métricas Clave
- Value at Risk (VaR 95%): $8,234.56
...
```

### 3. Visualizaciones PNG

- `montecarlo_simulation.png`: Gráfico de trayectorias
- `returns_distribution.png`: Histograma de retornos
- `portfolio_weights.png`: Distribución de pesos

---

## 🛠️ Personalización

### Añadir Nueva Fuente de Datos

1. Crea `src/adapters/tu_adapter.py`:

```python
from .api_source_base import APISourceBase

class TuAdapter(APISourceBase):
    def fetch_data(self, ticker, start_date, end_date):
        # Tu lógica de extracción
        return pd.DataFrame({
            'Date': ...,
            'Open': ...,
            'High': ...,
            'Low': ...,
            'Close': ...,
            'Volume': ...
        })
    
    def get_source_name(self):
        return "Tu Fuente"
```

2. Registra en `src/extractor.py`:

```python
self.adapters = {
    'yahoo': YahooAdapter(),
    'investing': InvestingAdapter(),
    'tu_fuente': TuAdapter()  # ← Añade aquí
}
```

### Cambiar Parámetros de Monte Carlo

En `portfolio.py`, método `montecarlo_simulation()`:

```python
# Cambiar defaults:
def montecarlo_simulation(
    self,
    num_simulations: int = 5000,    # Antes: 1000
    time_horizon: int = 504,        # Antes: 252 (2 años en vez de 1)
    confidence_level: float = 0.99  # Antes: 0.95
):
```

---

## ❓ Preguntas Frecuentes

### ¿Qué fuentes de datos usa?

- **Yahoo Finance** (real): Datos reales de mercado vía `yfinance`
- **Investing (simulado)**: Generador sintético para demos

### ¿Puedo analizar criptomonedas?

Sí, usa Yahoo Finance con símbolos como `BTC-USD`, `ETH-USD`.

### ¿Cómo interpreto el Sharpe Ratio?

- **< 1**: Retorno insuficiente por el riesgo asumido
- **1-2**: Bueno
- **2-3**: Muy bueno
- **> 3**: Excelente

### ¿Qué es el VaR?

**Value at Risk**: Con 95% confianza, no perderás más de X.

Ejemplo: VaR = $8,500 significa que en el 95% de los casos, tu portfolio valdrá al menos $8,500.

### ¿Cuántas simulaciones Monte Carlo debo hacer?

- **1,000**: Rápido, suficiente para estimaciones
- **5,000**: Balance tiempo/precisión (recomendado)
- **10,000+**: Máxima precisión, tarda más

---

## 🐛 Solución de Problemas

### Error: "No se encontraron datos para XXXXX"

**Causa**: Ticker inexistente o sin datos en el periodo.

**Solución**: Verifica el símbolo en Yahoo Finance.

### Error: "Datos insuficientes"

**Causa**: Menos de 30 días de datos.

**Solución**: Amplía el rango de fechas.

### Caracteres raros en la salida

**Causa**: Problema de encoding UTF-8.

**Solución**: 
```bash
# Windows PowerShell:
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
python -m src.main
```

---

## 📚 Fundamentos Matemáticos

### Rendimientos Logarítmicos

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

**Ventajas**: Aditivos, simétricos, aproximadamente normales.

### Sharpe Ratio

$$\text{Sharpe} = \frac{E[R_p] - R_f}{\sigma_p}$$

Mide el **exceso de retorno por unidad de riesgo**.

### Volatilidad del Portfolio

$$\sigma_p = \sqrt{w^T \Sigma w}$$

Considera las **correlaciones** entre activos (matriz $\Sigma$).

---


## 📄 Licencia

MIT License - Uso libre para fines educativos y comerciales.

---

## 🎓 Recursos Adicionales

### Aprender Más

- **Finanzas Cuantitativas**: "Quantitative Finance" - Paul Wilmott
- **Portfolio Theory**: "Modern Portfolio Theory" - Harry Markowitz
- **Python Finance**: "Python for Finance" - Yves Hilpisch

### APIs Alternativas

- **Alpha Vantage**: Datos gratuitos con API key
- **Polygon.io**: Datos en tiempo real
- **IEX Cloud**: Mercados US








































