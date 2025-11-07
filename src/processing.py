import pandas as pd
import numpy as np
from typing import Tuple


def clean_nans(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia valores faltantes (NA/NaN) en el DataFrame.
    Usa forward fill (ffill) que es apropiado para series de tiempo.
    
    Args:
        df: DataFrame con posibles valores faltantes
        
    Returns:
        DataFrame limpio
    """
    df_clean = df.copy()
    
    # Forward fill para valores faltantes (rellena con valor anterior)
    df_clean = df_clean.ffill()
    
    # Si aún quedan NaN al inicio (no hay valor previo), usar backward fill
    df_clean = df_clean.bfill()
    
    # Eliminar filas que aún tengan NaN (casos extremos)
    initial_rows = len(df_clean)
    df_clean = df_clean.dropna()
    
    rows_removed = initial_rows - len(df_clean)
    if rows_removed > 0:
        print(f"⚠️  Se eliminaron {rows_removed} filas con valores faltantes ")
    
    return df_clean


def check_consistency(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """
    Verifica y corrige inconsistencias en las fechas:
    - Duplicados
    - Orden incorrecto
    
    Args:
        df: DataFrame con columna 'Date'
        
    Returns:
        Tupla con (DataFrame corregido, lista de advertencias)
    """
    warnings = []
    df_clean = df.copy()
    
    # Asegurar que Date sea datetime
    if not pd.api.types.is_datetime64_any_dtype(df_clean['Date']):
        df_clean['Date'] = pd.to_datetime(df_clean['Date'])
    
    # Detectar duplicados
    duplicates = df_clean['Date'].duplicated().sum()
    if duplicates > 0:
        warnings.append(f"Se encontraron {duplicates} fechas duplicadas. Se mantiene la primera ocurrencia.")
        df_clean = df_clean.drop_duplicates(subset=['Date'], keep='first')
    
    # Ordenar por fecha
    if not df_clean['Date'].is_monotonic_increasing:
        warnings.append("Las fechas no estaban ordenadas. Se ordenaron automáticamente.")
        df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    # Detectar saltos grandes en fechas (más de 30 días entre días consecutivos de trading)
    date_diffs = df_clean['Date'].diff()
    large_gaps = date_diffs[date_diffs > pd.Timedelta(days=30)]
    if len(large_gaps) > 0:
        warnings.append(f"Se detectaron {len(large_gaps)} saltos grandes en las fechas (>30 días).")
    
    return df_clean, warnings


def calculate_log_returns(df: pd.DataFrame, price_column: str = 'Close') -> pd.DataFrame:
    """
    Calcula los rendimientos logarítmicos de una serie de precios.
    Los log returns son más apropiados para análisis estadístico y son aditivos.
    
    Formula: r_t = ln(P_t / P_{t-1})
    
    Args:
        df: DataFrame con columna de precios
        price_column: Nombre de la columna de precios (default: 'Close')
        
    Returns:
        DataFrame con columna adicional 'Log_Returns'
    """
    df_with_returns = df.copy()
    
    if price_column not in df_with_returns.columns:
        raise ValueError(f"Columna '{price_column}' no encontrada. Columnas disponibles: {list(df_with_returns.columns)}")
    
    # Calcular log returns
    df_with_returns['Log_Returns'] = np.log(
        df_with_returns[price_column] / df_with_returns[price_column].shift(1)
    )
    
    # El primer valor será NaN (no hay valor anterior) - esto es esperado y correcto
    
    return df_with_returns


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, list]:
    """
    Valida que el DataFrame cumpla los requisitos mínimos para análisis financiero.
    
    Args:
        df: DataFrame a validar
        
    Returns:
        Tupla (es_valido, lista_de_errores)
    """
    errors = []
    
    # Verificar que no esté vacío
    if df is None or df.empty:
        errors.append("El DataFrame está vacío")
        return False, errors
    
    # Verificar que tenga columna Date
    if 'Date' not in df.columns:
        errors.append("No se encontró columna 'Date'")
    else:
        # Verificar que Date sea datetime
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
            try:
                pd.to_datetime(df['Date'])
            except Exception:
                errors.append("La columna 'Date' no contiene fechas válidas")
    
    # Verificar que tenga al menos la columna Close (necesaria para retornos)
    if 'Close' not in df.columns:
        errors.append("No se encontró la columna 'Close' (obligatoria para cálculos)")
    
    # Verificar que tenga suficientes datos (al menos 30 días)
    if len(df) < 30:
        errors.append(f"Datos insuficientes: {len(df)} filas (mínimo recomendado: 30)")
    
    return len(errors) == 0, errors


def preprocess_financial_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
    """
    Pipeline completo de preprocesamiento para datos financieros.
    
    Args:
        df: DataFrame crudo con datos financieros
        
    Returns:
        Tupla con (DataFrame procesado, lista de advertencias)
    """
    all_warnings = []
    
    # 1. Validar formato básico
    is_valid, errors = validate_dataframe(df)
    if not is_valid:
        raise ValueError(f"DataFrame inválido: {'; '.join(errors)}")
    
    # 2. Limpiar NaNs
    df_processed = clean_nans(df)
    
    # 3. Verificar consistencia de fechas
    df_processed, warnings = check_consistency(df_processed)
    all_warnings.extend(warnings)
    
    # 4. Calcular log returns (siempre usa 'Close')
    df_processed = calculate_log_returns(df_processed, price_column='Close')
    
    # 5. Validación final
    is_valid, errors = validate_dataframe(df_processed)
    if not is_valid:
        raise ValueError(f"Error en validación final: {'; '.join(errors)}")
    
    if len(all_warnings) == 0:
        all_warnings.append("✅ Datos procesados sin advertencias")
    
    return df_processed, all_warnings