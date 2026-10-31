"""Pruebas del contrato de datos: los datos válidos pasan y los inválidos se detectan."""

import pandera.errors
import pytest

from contracts.churn_contract import discard_ok, features_schema, training_schema
from src.synthetic import generate_customers


def test_valid_data_passes(sample_df):
    training_schema.validate(sample_df, lazy=True)


@pytest.mark.parametrize(
    "column, bad_value",
    [
        ("tenure_months", -3),
        ("contract_type", "weekly"),
        ("senior_citizen", 2),
        ("churn", 5),
    ],
)
def test_invalid_values_are_rejected(sample_df, column, bad_value):
    df = sample_df.copy()
    df[column] = df[column].astype(object)
    df.loc[df.index[0], column] = bad_value
    with pytest.raises(pandera.errors.SchemaErrors):
        training_schema.validate(df, lazy=True)


def test_duplicate_ids_are_rejected(sample_df):
    df = sample_df.copy()
    df.loc[df.index[1], "customer_id"] = df.loc[df.index[0], "customer_id"]
    with pytest.raises(pandera.errors.SchemaErrors):
        training_schema.validate(df, lazy=True)


def test_schema_change_scenario_breaks_contract():
    """El escenario 'esquema' del simulacro debe ser detectado por el contrato."""
    batch = generate_customers(n=300, seed=3, scenario="esquema")
    with pytest.raises(pandera.errors.SchemaErrors):
        features_schema.validate(batch, lazy=True)


@pytest.mark.parametrize(
    "columna",
    ["region", "fecha_alta", "fecha_corte", "oferta_retencion_aceptada"],  # contrato §2.3
)
def test_rc5_columna_no_canonica_se_rechaza(sample_df, columna):
    """RC-5: una tabla válida más una columna fuera de la §2.1 debe ser rechazada (esquema estricto)."""
    df = sample_df.copy()
    df[columna] = 0
    with pytest.raises(pandera.errors.SchemaErrors):
        training_schema.validate(df, lazy=True)


@pytest.mark.parametrize("schema", [training_schema, features_schema], ids=["training", "features"])
def test_rc3_sin_internet_con_cargo_alto_se_rechaza(sample_df, schema):
    """RC-3: un cliente sin internet (solo telefonía) con cargo mayor a 60 debe ser rechazado."""
    df = sample_df.copy()
    i = df.index[0]
    df.loc[i, "internet_service"] = "none"
    df.loc[i, "monthly_charges"] = 90.0
    with pytest.raises(pandera.errors.SchemaErrors):
        schema.validate(df, lazy=True)


def test_descarte_maximo():
    """Regla propia: una limpieza que descarta más de MAX_DISCARD_SHARE de las filas se bloquea."""
    assert not discard_ok({"proporcion_descartada": 0.20})
    assert discard_ok({"proporcion_descartada": 0.0})
