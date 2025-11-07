"""
Financial Extractor Project - Demo Principal
Punto de entrada y demostración del sistema
"""

from src.extractor import Extractor
from datetime import datetime, timedelta


def demo_analisis_simple():
    """Ejemplo 1: Análisis rápido de un activo individual"""
    print("\n" + "="*70)
    print(" DEMO 1: Análisis Rápido de un Activo")
    print("="*70 + "\n")
    
    extractor = Extractor(default_source='yahoo')
    
    # Fechas: últimos 2 años
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    # Análisis rápido de Apple
    extractor.quick_analysis('AAPL', start_date, end_date)


def demo_portfolio_diversificado():
    """Ejemplo 2: Creación y análisis de portfolio diversificado"""
    print("\n" + "="*70)
    print(" DEMO 2: Portfolio Diversificado")
    print("="*70 + "\n")
    
    extractor = Extractor(default_source='yahoo')
    
    # Definir portfolio: Tech Giants
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    weights = {
        'AAPL': 0.30,
        'MSFT': 0.30,
        'GOOGL': 0.25,
        'AMZN': 0.15
    }
    
    # Fechas: últimos 3 años
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')
    
    # Crear portfolio
    portfolio = extractor.create_portfolio(tickers, weights, start_date, end_date)
    
    # Generar reporte Markdown
    print("📝 Generando reporte en Markdown...")
    report = portfolio.report(filename='portfolio_report.md', show_warnings=True)
    
    # Generar visualizaciones
    print("\n📊 Generando visualizaciones...")
    portfolio.plots_report(save_dir='plots', show_plots=False)
    
    print("\n✅ Demo completada. Archivos generados:")
    print("   - portfolio_report.md")
    print("   - plots/montecarlo_simulation.png")
    print("   - plots/returns_distribution.png")
    print("   - plots/portfolio_weights.png")


def demo_montecarlo_avanzado():
    """Ejemplo 3: Simulación Monte Carlo con diferentes escenarios"""
    print("\n" + "="*70)
    print(" DEMO 3: Simulación Monte Carlo Avanzada")
    print("="*70 + "\n")
    
    extractor = Extractor(default_source='yahoo')
    
    # Portfolio más agresivo
    tickers = ['TSLA', 'NVDA']
    weights = {
        'TSLA': 0.60,
        'NVDA': 0.40
    }
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    portfolio = extractor.create_portfolio(tickers, weights, start_date, end_date)
    
    # Simular diferentes horizontes temporales
    print("\n🎲 Simulación 1: 6 meses (126 días)")
    results_6m = portfolio.montecarlo_simulation(
        num_simulations=5000,
        time_horizon=126,
        confidence_level=0.95
    )
    
    print(f"   Valor inicial: ${results_6m['initial_value']:.2f}")
    print(f"   Valor esperado: ${results_6m['mean_final_value']:.2f}")
    print(f"   VaR 95%: ${results_6m['var']:.2f}")
    
    print("\n🎲 Simulación 2: 1 año (252 días)")
    results_1y = portfolio.montecarlo_simulation(
        num_simulations=5000,
        time_horizon=252,
        confidence_level=0.95
    )
    
    print(f"   Valor inicial: ${results_1y['initial_value']:.2f}")
    print(f"   Valor esperado: ${results_1y['mean_final_value']:.2f}")
    print(f"   VaR 95%: ${results_1y['var']:.2f}")
    
    # Plotear ambos
    portfolio.plot_montecarlo(results_6m, filename='plots/mc_6months.png', show_plot=False)
    portfolio.plot_montecarlo(results_1y, filename='plots/mc_1year.png', show_plot=False)
    
    print("\n✅ Simulaciones completadas y guardadas en plots/")


def demo_comparacion_fuentes():
    """Ejemplo 4: Comparar datos de diferentes fuentes"""
    print("\n" + "="*70)
    print(" DEMO 4: Comparación de Fuentes de Datos")
    print("="*70 + "\n")
    
    extractor = Extractor()
    
    ticker = 'AAPL'
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Extraer desde Yahoo
    print("📥 Extrayendo desde Yahoo Finance...")
    ts_yahoo = extractor.get_historical_data([ticker], start_date, end_date, source='yahoo')[0]
    
    # Extraer desde Investing (simulado)
    print("\n📥 Extrayendo desde Investing.com (simulado)...")
    ts_investing = extractor.get_historical_data([ticker], start_date, end_date, source='investing')[0]
    
    # Comparar métricas
    print("\n" + "="*60)
    print("  COMPARACIÓN DE MÉTRICAS")
    print("="*60)
    print(f"\n{'Métrica':<30} {'Yahoo':<15} {'Investing (Sim.)':<15}")
    print("-" * 60)
    
    metrics = [
        ('Puntos de datos', len(ts_yahoo.data), len(ts_investing.data)),
        ('Rendimiento diario medio', f"{ts_yahoo.mean_return:.6f}", f"{ts_investing.mean_return:.6f}"),
        ('Volatilidad diaria', f"{ts_yahoo.stdev_return:.6f}", f"{ts_investing.stdev_return:.6f}"),
        ('Sharpe Ratio', f"{ts_yahoo.calculate_sharpe_ratio():.4f}", f"{ts_investing.calculate_sharpe_ratio():.4f}"),
        ('CAGR', f"{ts_yahoo.calculate_cagr():.2%}", f"{ts_investing.calculate_cagr():.2%}")
    ]
    
    for metric, yahoo_val, investing_val in metrics:
        print(f"{metric:<30} {yahoo_val:<15} {investing_val:<15}")
    
    print("-" * 60 + "\n")


def menu_principal():
    """Menú interactivo para ejecutar las demos"""
    print("\n" + "="*70)
    print(" 📊 FINANCIAL EXTRACTOR PROJECT - Demo Menu")
    print("="*70)
    
    opciones = {
        '1': ('Análisis rápido de un activo', demo_analisis_simple),
        '2': ('Portfolio diversificado completo', demo_portfolio_diversificado),
        '3': ('Simulación Monte Carlo avanzada', demo_montecarlo_avanzado),
        '4': ('Comparación de fuentes de datos', demo_comparacion_fuentes),
        '5': ('Ejecutar todas las demos', lambda: ejecutar_todas_demos())
    }
    
    print("\nSeleccione una demo:")
    for key, (descripcion, _) in opciones.items():
        print(f"  {key}. {descripcion}")
    print("  0. Salir")
    
    return opciones


def ejecutar_todas_demos():
    """Ejecuta todas las demos en secuencia"""
    demo_analisis_simple()
    input("\n[Presione Enter para continuar a la siguiente demo...]")
    
    demo_portfolio_diversificado()
    input("\n[Presione Enter para continuar a la siguiente demo...]")
    
    demo_montecarlo_avanzado()
    input("\n[Presione Enter para continuar a la siguiente demo...]")
    
    demo_comparacion_fuentes()


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')  # Suprimir warnings de yfinance
    
    try:
        opciones = menu_principal()
        
        while True:
            seleccion = input("\n👉 Opción: ").strip()
            
            if seleccion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            
            if seleccion in opciones:
                _, funcion = opciones[seleccion]
                try:
                    funcion()
                except Exception as e:
                    print(f"\n❌ Error ejecutando demo: {str(e)}")
                
                if seleccion != '5':  # Si no es "ejecutar todas"
                    continuar = input("\n¿Ejecutar otra demo? (s/n): ").strip().lower()
                    if continuar != 's':
                        print("\n👋 ¡Hasta luego!")
                        break
                    opciones = menu_principal()
            else:
                print("❌ Opción inválida. Intente de nuevo.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")