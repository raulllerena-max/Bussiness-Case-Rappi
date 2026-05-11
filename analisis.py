import pandas as pd
import numpy as np

# =========================================================
# CONFIGURACIÓN
# =========================================================
COMPETITORS_PATH = "competidores/COMPETITORS_INPUT_METRICS.csv"
RAPPI_PATH = "base_de_datos/RAW_INPUT_METRICS.csv"

OUTPUT_FILE = "matriz_confiabilidad.csv"

# =========================================================
# FUNCIÓN PARA CLASIFICAR TENDENCIA
# =========================================================
def clasificar_tendencia(delta, l4w):
    """
    Clasifica la tendencia usando una tolerancia de ruido del 1%.

    Reglas:
    - Delta > 1% de L4W  -> Sube 📈
    - Delta < -1% de L4W -> Baja 📉
    - Dentro del margen  -> Estable ➖
    """

    if pd.isna(delta) or pd.isna(l4w):
        return np.nan

    # Evitar división por cero
    if l4w == 0:
        return "Estable ➖"

    threshold = abs(l4w) * 0.01

    if delta > threshold:
        return "Sube 📈"

    elif delta < -threshold:
        return "Baja 📉"

    else:
        return "Estable ➖"


# =========================================================
# FUNCIÓN PARA CALCULAR NIVEL DE CONFIABILIDAD
# =========================================================
def calcular_confiabilidad(row):
    """
    Evalúa la consistencia de tendencias entre competidores.
    """

    tendencias = [
        row.get("Rappi"),
        row.get("Uber Eats"),
        row.get("DiDi Food")
    ]

    # Si falta algún dato
    if any(pd.isna(x) for x in tendencias):
        return "Data Incompleta ⚠️"

    # Contar tendencias únicas
    tendencias_unicas = len(set(tendencias))

    # Los 3 iguales
    if tendencias_unicas == 1:
        return "Confiable ✅"

    # 2 iguales y 1 diferente
    elif tendencias_unicas == 2:
        return "Moderadamente Confiable 🟡"

    # Los 3 diferentes
    else:
        return "Poco Confiable ❌"


# =========================================================
# MAIN
# =========================================================
try:

    print("\n=================================================")
    print("CARGANDO ARCHIVOS")
    print("=================================================")

    # -----------------------------------------------------
    # Cargar archivos
    # -----------------------------------------------------
    competitors_df = pd.read_csv(COMPETITORS_PATH)
    rappi_df = pd.read_csv(RAPPI_PATH)

    # -----------------------------------------------------
    # Estandarizar nombres de columnas
    # -----------------------------------------------------
    competitors_df.columns = competitors_df.columns.str.upper().str.strip()
    rappi_df.columns = rappi_df.columns.str.upper().str.strip()

    # -----------------------------------------------------
    # Agregar columna COMPETITOR a Rappi
    # -----------------------------------------------------
    rappi_df["COMPETITOR"] = "Rappi"

    # -----------------------------------------------------
    # Unir datasets
    # -----------------------------------------------------
    df = pd.concat(
        [competitors_df, rappi_df],
        ignore_index=True
    )

    print(f"Total registros: {len(df):,}")

    # =====================================================
    # DETECTAR COLUMNAS DINÁMICAMENTE
    # =====================================================
    # Busca columnas que contengan:
    # - L0W
    # - L4W
    # Ejemplos válidos:
    #   L0W
    #   L0W_FINAL
    #   L0W_VALUE
    # =====================================================

    l0w_cols = df.columns[df.columns.str.contains("L0W", case=False)]
    l4w_cols = df.columns[df.columns.str.contains("L4W", case=False)]

    if len(l0w_cols) == 0:
        raise ValueError("No se encontró columna L0W")

    if len(l4w_cols) == 0:
        raise ValueError("No se encontró columna L4W")

    # Tomar primera coincidencia
    L0W_FINAL = l0w_cols[0]
    L4W_FINAL = l4w_cols[0]

    print(f"\nColumna detectada L0W: {L0W_FINAL}")
    print(f"Columna detectada L4W: {L4W_FINAL}")

    # =====================================================
    # LIMPIEZA NUMÉRICA
    # =====================================================
    df[L0W_FINAL] = pd.to_numeric(df[L0W_FINAL], errors="coerce")
    df[L4W_FINAL] = pd.to_numeric(df[L4W_FINAL], errors="coerce")

    # =====================================================
    # AGRUPACIÓN MACRO
    # =====================================================
    # IMPORTANTE:
    # No usar ZONE por inconsistencias geográficas.
    #
    # Ejemplo:
    # Competidor -> Polanco
    # Rappi      -> Roma-Polanco
    #
    # Por eso agregamos a nivel:
    # COUNTRY + METRIC + COMPETITOR
    # =====================================================

    grouped_df = (
        df
        .groupby(
            ["COUNTRY", "METRIC", "COMPETITOR"],
            as_index=False
        )
        .agg({
            L4W_FINAL: "mean",
            L0W_FINAL: "mean"
        })
    )

    # =====================================================
    # CÁLCULO DE DELTA
    # =====================================================
    grouped_df["DELTA"] = (
        grouped_df[L0W_FINAL] - grouped_df[L4W_FINAL]
    )

    # =====================================================
    # CLASIFICACIÓN DE TENDENCIA
    # =====================================================
    grouped_df["TENDENCIA"] = grouped_df.apply(
        lambda row: clasificar_tendencia(
            row["DELTA"],
            row[L4W_FINAL]
        ),
        axis=1
    )

    # =====================================================
    # PIVOT TABLE
    # =====================================================
    pivot_df = grouped_df.pivot_table(
        index=["COUNTRY", "METRIC"],
        columns="COMPETITOR",
        values="TENDENCIA",
        aggfunc="first"
    ).reset_index()

    # =====================================================
    # NIVEL DE CONFIABILIDAD
    # =====================================================
    pivot_df["NIVEL_CONFIABILIDAD"] = pivot_df.apply(
        calcular_confiabilidad,
        axis=1
    )

    # =====================================================
    # ORDENAR RESULTADOS
    # =====================================================
    pivot_df = pivot_df.sort_values(
        by=["COUNTRY", "METRIC"]
    )

    # =====================================================
    # IMPRIMIR RESULTADOS
    # =====================================================
    print("\n=================================================")
    print("MATRIZ DE CONFIABILIDAD")
    print("=================================================\n")

    print(pivot_df.to_string(index=False))

    # =====================================================
    # EXPORTAR CSV
    # =====================================================
    pivot_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n=================================================")
    print("ARCHIVO EXPORTADO CORRECTAMENTE")
    print("=================================================")
    print(f"Archivo generado: {OUTPUT_FILE}")

except FileNotFoundError as e:
    print("\n[ERROR] Archivo no encontrado")
    print(e)

except pd.errors.EmptyDataError:
    print("\n[ERROR] Uno de los archivos CSV está vacío")

except Exception as e:
    print("\n[ERROR INESPERADO]")
    print(e)