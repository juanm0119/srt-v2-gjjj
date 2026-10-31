"""Limpieza del extracto CRM con los tratamientos negociados en el Reto 02.

Lee data/raw/crm_extracto.csv y escribe:
  data/processed/clean.csv: las nueve columnas canonicas.
  reports/cleaning.json: conteos por tratamiento, sin identificadores.

Ejecutar: uv run python -m src.clean
"""

import json

import pandas as pd

from src.common import CLEAN_DATA, CRM_EXTRACT, FEATURES, ID_COL, REPORTS_DIR, TARGET

CANONICAS = [ID_COL, *FEATURES, TARGET]

COLUMNAS_EXCLUIDAS: dict[str, str] = {
    "region": "No pertenece al esquema canónico del modelo definido en el contrato.",
    "fecha_alta": (
        "No pertenece al esquema canónico; se utiliza para revisar "
        "la coherencia temporal del extracto."
    ),
    "fecha_corte": (
        "No pertenece al esquema canónico; proporciona la referencia "
        "temporal del extracto."
    ),
    "oferta_retencion_aceptada": (
        "No pertenece al esquema canónico; se analiza su disponibilidad "
        "temporal por posible fuga de información."
    ),
}


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Devuelve el conjunto limpio y los conteos de los tratamientos acordados."""
    n0 = len(df)
    if n0 == 0:
        raise ValueError("El extracto está vacío.")

    faltantes = set(CANONICAS) - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas canónicas: {sorted(faltantes)}")

    no_documentadas = set(df.columns) - set(CANONICAS) - set(COLUMNAS_EXCLUIDAS)
    if no_documentadas:
        raise ValueError(
            f"Hay columnas sin motivo de exclusión documentado: {sorted(no_documentadas)}"
        )

    if df[ID_COL].isna().any():
        raise ValueError("Hay identificadores nulos sin un tratamiento acordado.")

    df = df.copy().reset_index(drop=True)
    informe: dict = {"filas_entrada": n0, "tratamientos": {}}
    t = informe["tratamientos"]

    # 1. Recodificar exclusivamente los valores negociados.
    mascara = df["contract_type"].eq("Month-to-month").fillna(False)
    t["recodificado_contract_type"] = int(mascara.sum())
    df.loc[mascara, "contract_type"] = "month-to-month"

    mascara = df["payment_method"].eq("tarjeta_debito").fillna(False)
    t["recodificado_payment_method"] = int(mascara.sum())
    df.loc[mascara, "payment_method"] = "credit_card"

    # 2. Contar incidencias de fechas sin descartar filas por estas causas.
    # Estas cifras no sustituyen las reglas de contracts/crm_warnings.py.
    if "fecha_alta" in df.columns:
        t["advertencia_fecha_alta_vacia"] = int(df["fecha_alta"].isna().sum())

        if "fecha_corte" in df.columns:
            altas = pd.to_datetime(
                df["fecha_alta"], format="%Y-%m-%d", errors="coerce"
            )
            cortes = pd.to_datetime(
                df["fecha_corte"], format="%Y-%m-%d", errors="coerce"
            )
            t["advertencia_fecha_alta_posterior_corte"] = int(altas.gt(cortes).sum())

    # 3. Excluir los defectos concretos acordados, contando cada fila una vez.
    reglas_exclusion: dict[str, pd.Series] = {
        "monthly_charges_nulo": df["monthly_charges"].isna(),
        "tenure_months_menos_uno": df["tenure_months"].eq(-1),
        "support_tickets_99": df["support_tickets"].eq(99),
        "rc3": df["internet_service"].eq("none") & df["monthly_charges"].gt(60),
    }
    excluir = pd.Series(False, index=df.index)
    for nombre, mascara in reglas_exclusion.items():
        mascara = mascara.fillna(False)
        t[f"excluidas_{nombre}"] = int((mascara & ~excluir).sum())
        excluir |= mascara
    df = df.loc[~excluir].copy()

    # 4. Retirar copias exactas entre los registros que continúan.
    duplicadas = df.duplicated(keep="first")
    t["excluidas_duplicados_exactos"] = int(duplicadas.sum())
    df = df.loc[~duplicadas].copy()

    # 5. Comprobar si el mayor cargo permite elegir una única fila por cliente.
    maximos = df.groupby(ID_COL)["monthly_charges"].transform("max")
    candidatas = df.loc[df["monthly_charges"].eq(maximos)]
    empates = candidatas[ID_COL].duplicated(keep=False)
    if empates.any():
        cantidad = int(candidatas.loc[empates, ID_COL].nunique())
        raise ValueError(
            f"Hay {cantidad} identificadores con registros distintos y el mismo "
            "cargo máximo. El dueño debe definir un criterio de desempate."
        )

    # El criterio de mayor cargo se aplica entre las filas no excluidas.
    df = df.sort_values("monthly_charges", ascending=False, kind="mergesort")
    menor_cargo = df[ID_COL].duplicated(keep="first")
    t["excluidas_duplicados_menor_cargo"] = int(menor_cargo.sum())
    df = df.loc[~menor_cargo].copy()

    informe["columnas_excluidas"] = {
        columna: motivo
        for columna, motivo in COLUMNAS_EXCLUIDAS.items()
        if columna in df.columns
    }
    informe["filas_salida"] = len(df)
    informe["proporcion_descartada"] = round(1 - len(df) / n0, 4)

    df = df[CANONICAS].sort_values(ID_COL, kind="mergesort").reset_index(drop=True)
    return df, informe


def main() -> None:
    df, informe = clean(pd.read_csv(CRM_EXTRACT))

    CLEAN_DATA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_DATA, index=False, encoding="utf-8")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (REPORTS_DIR / "cleaning.json").write_text(
        json.dumps(informe, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"[clean] {informe['filas_entrada']} → {informe['filas_salida']} filas "
        f"({informe['proporcion_descartada']:.1%} descartado)"
    )


if __name__ == "__main__":
    main()
