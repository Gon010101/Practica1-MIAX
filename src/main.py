"""
Financial Extractor Project - Sistema Interactivo
Permite al usuario elegir tickers, periodo, columnas y crear carteras personalizadas
"""

from src.extractor import Extractor
from datetime import datetime
import sys


def obtener_fechas():
    """Solicita al usuario el periodo de tiempo para el análisis."""
    print("\n" + "="*70)
    print(" 📅 SELECCIÓN DE PERIODO")
    print("="*70)
    
    while True:
        print("\nFormato de fecha: YYYY-MM-DD (ejemplo: 2023-01-01)")
        
        try:
            start_date = input("📅 Fecha de inicio: ").strip()
            # Validar formato
            datetime.strptime(start_date, '%Y-%m-%d')
            
            end_date = input("📅 Fecha de fin: ").strip()
            datetime.strptime(end_date, '%Y-%m-%d')
            
            # Verificar que start < end
            if datetime.strptime(start_date, '%Y-%m-%d') >= datetime.strptime(end_date, '%Y-%m-%d'):
                print("❌ La fecha de inicio debe ser anterior a la fecha de fin")
                continue
            
            return start_date, end_date
            
        except ValueError as e:
            print(f"❌ Formato de fecha inválido. Use YYYY-MM-DD")
            continue


def obtener_tickers():
    """Solicita al usuario los tickers que desea analizar."""
    print("\n" + "="*70)
    print(" 📊 SELECCIÓN DE ACTIVOS")
    print("="*70)
    
    while True:
        print("\nIntroduce los tickers separados por comas")
        print("Ejemplo: AAPL, MSFT, GOOGL")
        
        tickers_input = input("\n📈 Tickers: ").strip()
        
        if not tickers_input:
            print("❌ Debes introducir al menos un ticker")
            continue
        
        # Limpiar y separar tickers
        tickers = [t.strip().upper() for t in tickers_input.split(',')]
        tickers = [t for t in tickers if t]  # Eliminar vacíos
        
        if not tickers:
            print("❌ No se detectaron tickers válidos")
            continue
        
        # Confirmar
        print(f"\n✅ Tickers seleccionados: {', '.join(tickers)}")
        confirmar = input("¿Es correcto? (s/n): ").strip().lower()
        
        if confirmar == 's':
            return tickers


def obtener_columnas_deseadas():
    """Solicita al usuario qué columnas de datos desea obtener."""
    print("\n" + "="*70)
    print(" 📋 SELECCIÓN DE DATOS")
    print("="*70)
    
    columnas_disponibles = {
        '1': ('Open', 'Precio de apertura'),
        '2': ('High', 'Precio máximo'),
        '3': ('Low', 'Precio mínimo'),
        '4': ('Close', 'Precio de cierre (ajustado)'),
        '5': ('Volume', 'Volumen de operaciones'),
        '6': ('TODAS', 'Todas las columnas anteriores')
    }
    
    print("\nColumnas disponibles:")
    for key, (nombre, descripcion) in columnas_disponibles.items():
        print(f"  {key}. {nombre:10} - {descripcion}")
    
    while True:
        seleccion = input("\n📊 Selecciona columnas (números separados por comas, o 6 para todas): ").strip()
        
        if not seleccion:
            print("❌ Debes seleccionar al menos una columna")
            continue
        
        # Procesar selección
        if '6' in seleccion:
            columnas = ['Open', 'High', 'Low', 'Close', 'Volume']
            print(f"\n✅ Seleccionadas: {', '.join(columnas)}")
            return columnas
        
        try:
            indices = [s.strip() for s in seleccion.split(',')]
            columnas = [columnas_disponibles[idx][0] for idx in indices if idx in columnas_disponibles and idx != '6']
            
            if not columnas:
                print("❌ No se seleccionaron columnas válidas")
                continue
            
            # Siempre incluir 'Close' para cálculos
            if 'Close' not in columnas:
                columnas.append('Close')
                print("ℹ️  Se añadió 'Close' automáticamente (necesario para cálculos)")
            
            print(f"\n✅ Seleccionadas: {', '.join(columnas)}")
            return columnas
            
        except (KeyError, ValueError):
            print("❌ Selección inválida. Usa números del 1 al 6")


def obtener_fuente_datos():
    """Solicita al usuario la fuente de datos a utilizar."""
    print("\n" + "="*70)
    print(" 🌐 SELECCIÓN DE FUENTE DE DATOS")
    print("="*70)
    
    fuentes = {
        '1': ('yahoo', 'Yahoo Finance'),
        '2': ('investing', 'Investing.com')
    }
    
    print("\nFuentes disponibles:")
    for key, (nombre, descripcion) in fuentes.items():
        print(f"  {key}. {descripcion}")
    
    while True:
        seleccion = input("\n🌐 Selecciona fuente (1 o 2): ").strip()
        
        if seleccion in fuentes:
            fuente, descripcion = fuentes[seleccion]
            print(f"✅ Fuente seleccionada: {descripcion}")
            return fuente
        
        print("❌ Selección inválida")


def obtener_cartera():
    """Solicita al usuario los componentes y pesos de su cartera."""
    print("\n" + "="*70)
    print(" 💼 CONFIGURACIÓN DE CARTERA")
    print("="*70)
    
    print("\n¿Qué activos tiene tu cartera?")
    tickers = obtener_tickers()
    
    print("\n" + "="*70)
    print(" ⚖️  ASIGNACIÓN DE PESOS")
    print("="*70)
    print("\nIntroduce el porcentaje (peso) de cada ticker")
    print("Los pesos pueden ser decimales (0.2, 0.3, etc.) o porcentajes (20%, 30%, etc.)")
    print("La suma total debe ser aproximadamente 1.0 (100%)")
    
    weights = {}
    
    for ticker in tickers:
        while True:
            try:
                peso_input = input(f"\n💰 Peso de {ticker}: ").strip()
                
                # Manejar porcentajes
                if '%' in peso_input:
                    peso = float(peso_input.replace('%', '')) / 100
                else:
                    peso = float(peso_input)
                
                if peso <= 0 or peso > 1:
                    print("❌ El peso debe estar entre 0 y 1 (o 0% y 100%)")
                    continue
                
                weights[ticker] = peso
                break
                
            except ValueError:
                print("❌ Formato inválido. Introduce un número (ej: 0.3 o 30%)")
    
    # Verificar suma de pesos
    total = sum(weights.values())
    print(f"\n📊 Suma total de pesos: {total:.4f}")
    
    if not (0.95 <= total <= 1.05):
        print(f"⚠️  Los pesos suman {total:.4f}, se normalizarán a 1.0")
        confirmar = input("¿Continuar con normalización? (s/n): ").strip().lower()
        if confirmar != 's':
            print("❌ Operación cancelada")
            return None, None
    
    # Mostrar resumen
    print("\n" + "="*70)
    print(" 📋 RESUMEN DE CARTERA")
    print("="*70)
    for ticker, peso in weights.items():
        print(f"  {ticker:10} : {peso:6.2%}")
    print(f"  {'TOTAL':10} : {sum(weights.values()):6.2%}")
    print("="*70)
    
    return tickers, weights


def menu_principal():
    """Menú principal del sistema."""
    print("\n" + "="*70)
    print(" 📊 FINANCIAL EXTRACTOR - Sistema de Análisis Financiero")
    print("="*70)
    
    print("\n¿Qué deseas hacer?")
    print("  1. Análisis de activos individuales")
    print("  2. Análisis de cartera (portfolio)")
    print("  0. Salir")
    
    while True:
        opcion = input("\n👉 Opción: ").strip()
        
        if opcion in ['0', '1', '2']:
            return opcion
        
        print("❌ Opción inválida")


def analisis_individual():
    """Flujo para análisis de activos individuales."""
    print("\n" + "="*70)
    print(" 📈 ANÁLISIS DE ACTIVOS INDIVIDUALES")
    print("="*70)
    
    # Obtener parámetros
    tickers = obtener_tickers()
    start_date, end_date = obtener_fechas()
    columnas = obtener_columnas_deseadas()
    fuente = obtener_fuente_datos()
    
    # Confirmar
    print("\n" + "="*70)
    print(" 📋 RESUMEN DE CONFIGURACIÓN")
    print("="*70)
    print(f"  Tickers:     {', '.join(tickers)}")
    print(f"  Periodo:     {start_date} a {end_date}")
    print(f"  Columnas:    {', '.join(columnas)}")
    print(f"  Fuente:      {fuente}")
    print("="*70)
    
    confirmar = input("\n¿Proceder con la extracción? (s/n): ").strip().lower()
    if confirmar != 's':
        print("❌ Operación cancelada")
        return
    
    # Extraer datos
    try:
        extractor = Extractor(default_source=fuente)
        timeseries_list = extractor.get_historical_data(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            columns=columnas
        )
        
        # NUEVO: Preguntar qué tipo de salida desea el usuario
        print("\n" + "="*70)
        print(" 📊 TIPO DE SALIDA")
        print("="*70)
        print("  1. Ver datos tabulares (tabla con fechas y valores)")
        print("  2. Ver resumen estadístico (métricas calculadas)")
        print("  3. Ver ambos")
        
        tipo_salida = input("\n👉 Opción (default: 1): ").strip() or "1"
        
        # Mostrar resultados según elección
        if tipo_salida in ['1', '3']:
            mostrar_datos_tabulares(timeseries_list, columnas)
        
        if tipo_salida in ['2', '3']:
            mostrar_resumen_estadistico(timeseries_list)
        
        # Preguntar si desea guardar
        guardar = input("\n¿Deseas guardar los datos en CSV? (s/n): ").strip().lower()
        if guardar == 's':
            for ts in timeseries_list:
                filename = f"{ts.ticker}_{start_date}_{end_date}.csv"
                ts.data.to_csv(filename, index=False)
                print(f"✅ Guardado: {filename}")
        
        print("\n✅ Análisis completado")
        
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {str(e)}")


def mostrar_datos_tabulares(timeseries_list, columnas):
    """
    Muestra los datos en formato tabular (fechas x valores).
    
    Args:
        timeseries_list: Lista de objetos TimeSeries
        columnas: Lista de columnas seleccionadas por el usuario
    """
    print("\n" + "="*70)
    print(" 📊 DATOS TABULARES")
    print("="*70)
    
    for ts in timeseries_list:
        print(f"\n{'─'*70}")
        print(f" Ticker: {ts.ticker} | Fuente: {ts.source}")
        print(f"{'─'*70}")
        
        # Seleccionar columnas a mostrar (siempre incluir Date)
        columnas_mostrar = ['Date'] + [col for col in columnas if col in ts.data.columns and col != 'Date']
        
        # Crear DataFrame solo con columnas seleccionadas
        df_display = ts.data[columnas_mostrar].copy()
        
        # Formatear la fecha para mejor visualización
        df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')
        
        # Determinar cuántas filas mostrar
        num_filas = len(df_display)
        
        if num_filas <= 20:
            # Si son pocas filas, mostrar todas
            print(f"\n{df_display.to_string(index=False)}")
        else:
            # Si son muchas, mostrar primeras 10 y últimas 10
            print(f"\nPrimeras 10 observaciones:")
            print(df_display.head(10).to_string(index=False))
            print("\n   ... ({} filas intermedias) ...".format(num_filas - 20))
            print(f"\nÚltimas 10 observaciones:")
            print(df_display.tail(10).to_string(index=False))
        
        print(f"\nTotal de observaciones: {num_filas}")
        
        # Estadísticas rápidas de las columnas numéricas
        print(f"\n📊 Estadísticas descriptivas:")
        for col in columnas_mostrar:
            if col != 'Date' and col in df_display.columns:
                valores = ts.data[col]
                print(f"  {col:12} - Min: {valores.min():>10.2f}  |  Max: {valores.max():>10.2f}  |  Media: {valores.mean():>10.2f}")


def mostrar_resumen_estadistico(timeseries_list):
    """
    Muestra el resumen estadístico tradicional.
    
    Args:
        timeseries_list: Lista de objetos TimeSeries
    """
    print("\n" + "="*70)
    print(" 📊 RESUMEN ESTADÍSTICO")
    print("="*70)
    
    for ts in timeseries_list:
        print(f"\n{'─'*70}")
        print(f" Ticker: {ts.ticker}")
        print(f"{'─'*70}")
        
        summary = ts.get_summary()
        for key, value in summary.items():
            print(f"  {key:.<35} {value}")


def analisis_cartera():
    """Flujo para análisis de cartera."""
    print("\n" + "="*70)
    print(" 💼 ANÁLISIS DE CARTERA")
    print("="*70)
    
    # Obtener parámetros
    tickers, weights = obtener_cartera()
    if not tickers:
        return
    
    start_date, end_date = obtener_fechas()
    fuente = obtener_fuente_datos()
    
    # Confirmar
    print("\n" + "="*70)
    print(" 📋 RESUMEN DE CONFIGURACIÓN")
    print("="*70)
    print(f"  Cartera:     {len(tickers)} activos")
    print(f"  Periodo:     {start_date} a {end_date}")
    print(f"  Fuente:      {fuente}")
    print("="*70)
    
    confirmar = input("\n¿Proceder con el análisis? (s/n): ").strip().lower()
    if confirmar != 's':
        print("❌ Operación cancelada")
        return
    
    # Crear cartera
    try:
        extractor = Extractor(default_source=fuente)
        portfolio = extractor.create_portfolio(
            tickers=tickers,
            weights=weights,
            start_date=start_date,
            end_date=end_date
        )
        
        # Menú de análisis
        while True:
            print("\n" + "="*70)
            print(" 📊 OPCIONES DE ANÁLISIS")
            print("="*70)
            print("  1. Ver métricas de la cartera")
            print("  2. Generar simulación Monte Carlo")
            print("  3. Generar reporte completo (Markdown)")
            print("  4. Generar todas las visualizaciones")
            print("  0. Volver al menú principal")
            
            opcion = input("\n👉 Opción: ").strip()
            
            if opcion == '0':
                break
            elif opcion == '1':
                mostrar_metricas_cartera(portfolio)
            elif opcion == '2':
                generar_simulacion_montecarlo(portfolio)
            elif opcion == '3':
                generar_reporte_markdown(portfolio)
            elif opcion == '4':
                generar_visualizaciones(portfolio)
            else:
                print("❌ Opción inválida")
        
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {str(e)}")


def mostrar_metricas_cartera(portfolio):
    """Muestra las métricas principales de la cartera."""
    print("\n" + "="*70)
    print(" 📊 MÉTRICAS DE LA CARTERA")
    print("="*70)
    
    annual_return = portfolio.portfolio_return * 252
    annual_volatility = portfolio.portfolio_volatility * (252 ** 0.5)
    sharpe = portfolio.calculate_sharpe_ratio()
    
    print(f"\n  Rendimiento anualizado:     {annual_return:>10.2%}")
    print(f"  Volatilidad anualizada:     {annual_volatility:>10.2%}")
    print(f"  Ratio de Sharpe:            {sharpe:>10.4f}")
    print(f"  Número de activos:          {len(portfolio.components):>10}")
    
    print("\n  Métricas por activo:")
    print(f"  {'Ticker':<10} {'Peso':<8} {'Rend. Anual':<12} {'Volatilidad':<12} {'Sharpe':<8}")
    print("  " + "─"*60)
    
    for ts in portfolio.components:
        annual_ret = ts.mean_return * 252
        annual_vol = ts.stdev_return * (252 ** 0.5)
        sharpe_ind = ts.calculate_sharpe_ratio()
        peso = portfolio.weights[ts.ticker]
        
        print(f"  {ts.ticker:<10} {peso:<8.2%} {annual_ret:<12.2%} {annual_vol:<12.2%} {sharpe_ind:<8.4f}")
    
    input("\n[Presiona Enter para continuar...]")


def generar_simulacion_montecarlo(portfolio):
    """Genera y visualiza una simulación Monte Carlo."""
    print("\n" + "="*70)
    print(" 🎲 SIMULACIÓN MONTE CARLO")
    print("="*70)
    
    try:
        num_sim = int(input("\n🔢 Número de simulaciones (default: 1000): ").strip() or "1000")
        horizonte = int(input("📅 Horizonte temporal en días (default: 252): ").strip() or "252")
        
        print(f"\n⏳ Ejecutando {num_sim} simulaciones a {horizonte} días...")
        
        results = portfolio.montecarlo_simulation(
            num_simulations=num_sim,
            time_horizon=horizonte
        )
        
        print("\n✅ Simulación completada")
        print(f"\n  Valor inicial:              ${results['initial_value']:>12.2f}")
        print(f"  Valor esperado (media):     ${results['mean_final_value']:>12.2f}")
        print(f"  Percentil 5% (pesimista):   ${results['percentile_5']:>12.2f}")
        print(f"  Percentil 95% (optimista):  ${results['percentile_95']:>12.2f}")
        print(f"  VaR (95%):                  ${results['var']:>12.2f}")
        print(f"  Pérdida potencial:          ${results['var_loss']:>12.2f}")
        
        guardar = input("\n¿Guardar visualización? (s/n): ").strip().lower()
        if guardar == 's':
            filename = input("📁 Nombre de archivo (default: montecarlo.png): ").strip() or "montecarlo.png"
            portfolio.plot_montecarlo(results, filename=filename, show_plot=False)
            print(f"✅ Guardado: {filename}")
    
    except ValueError:
        print("❌ Valor inválido")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def generar_reporte_markdown(portfolio):
    """Genera un reporte completo en Markdown."""
    print("\n📄 Generando reporte en Markdown...")
    
    filename = input("📁 Nombre de archivo (default: portfolio_report.md): ").strip() or "portfolio_report.md"
    
    report = portfolio.report(filename=filename)
    print(f"\n✅ Reporte guardado: {filename}")


def generar_visualizaciones(portfolio):
    """Genera todas las visualizaciones de la cartera."""
    print("\n📊 Generando visualizaciones...")
    
    directorio = input("📁 Directorio destino (default: plots): ").strip() or "plots"
    
    portfolio.plots_report(save_dir=directorio, show_plots=False)
    print(f"\n✅ Visualizaciones guardadas en: {directorio}/")


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')
    
    try:
        while True:
            opcion = menu_principal()
            
            if opcion == '0':
                print("\n👋 ¡Hasta luego!")
                break
            elif opcion == '1':
                analisis_individual()
            elif opcion == '2':
                analisis_cartera()
            
            input("\n[Presiona Enter para volver al menú principal...]")
    
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        sys.exit(1)