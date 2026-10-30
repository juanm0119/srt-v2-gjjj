"""Perfil de calidad del extracto: cifras por dimensión, sin identificadores."""
import pandas as pd
from src.common import CATEGORIES
df = pd.read_csv("data/raw/crm_extracto.csv")
n = len(df)

def cifra(k) -> str:
    return f"{int(k)} filas ({k / n:.1%})"

def fuera_de_dominio(col: str, fuera: pd.Series) -> None:
    """Imprime cuántas filas fallan y hasta 5 ejemplos del VALOR (nunca del cliente)."""
    ejemplos = df.loc[fuera, col].value_counts().head(5).to_dict()
    print(f" {col}: {cifra(fuera.sum())} {ejemplos}")

print(f"Extracto: {n} filas · {len(df.columns)} columnas")
# 1. Completitud: la ficha dice que ninguna columna admite vacíos.
print("\n[Completitud] nulos por columna")
for col, k in df.isna().sum().items():
    print(f" {col}: {cifra(k)}")
# 2. Validez: dominios (CATEGORIES de src/common.py) y rangos de la ficha.
print("\n[Validez] valores fuera del dominio o del rango")
for col, dominio in CATEGORIES.items():
    fuera_de_dominio(col, df[col].notna() & ~df[col].isin(dominio))
for col in ["senior_citizen", "churn"]: # columnas 0/1
    fuera_de_dominio(col, df[col].notna() & ~df[col].isin([0, 1]))
RANGOS = {"tenure_months": (0, 72), "monthly_charges": (0, 500),
    "support_tickets": (0, 50)}
for col, (minimo, maximo) in RANGOS.items():
    x = pd.to_numeric(df[col], errors="coerce") # el texto queda como NaN
    fuera_de_dominio(col, df[col].notna() & ~x.between(minimo, maximo))
# 3. Unicidad: una fila por cliente.
repetidas = df["customer_id"].duplicated(keep=False)
print(f"\n[Unicidad] filas con customer_id repetido: {cifra(repetidas.sum())}")
print(f" copias exactas de otra fila: {df.duplicated().sum()}")
# 4. Consistencia entre columnas: RC-3 (sin internet → cargo mensual ≤ 60).
cargo = pd.to_numeric(df["monthly_charges"], errors="coerce")
rc3 = (df["internet_service"] == "none") & (cargo > 60)
print(f"\n[Consistencia] sin internet con cargo > 60 (RC-3): {cifra(rc3.sum())}")