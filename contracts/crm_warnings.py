"""Contrato v2 · ADVERTENCIAS sobre el extracto crudo (Reto 02).

Reglas que NO detienen el pipeline: se registran y se reportan al dueño del dato.
Se aplican al extracto crudo (data/raw/crm_extracto.csv), por eso pueden usar
columnas no canónicas.

Validar:
uv run python -m scripts.validar_contrato advertencias data/raw/crm_extracto.csv
"""

import pandera.pandas as pa

warnings_schema = pa.DataFrameSchema(
    columns={
        "fecha_alta": pa.Column(str, nullable=True),
        "fecha_corte": pa.Column(str),
    },
    checks=[
        # Advertencia W-1:
        # fecha_alta posterior a fecha_corte.
        pa.Check(
            lambda df: (
                df["fecha_alta"].isna()
                | (df["fecha_alta"] <= df["fecha_corte"])
            ),
            error="fecha_alta posterior a fecha_corte",
        ),

        # Advertencia W-2:
        # fecha_alta faltante.
        pa.Check(
            lambda df: df["fecha_alta"].notna(),
            error="fecha_alta vacia",
        ),
    ],
    strict=False,  # el extracto trae más columnas
    coerce=True,
    name="crm_warnings",
)
