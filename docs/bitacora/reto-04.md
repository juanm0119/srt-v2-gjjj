# Bitácora del Reto 04 — Equipo GJJJ

## Martes 10 de noviembre

### Equipo

- Aprobación de los PR #38 y #40. El PR #39 (escenario 1, contrato relajado) se cerró sin fusionar.

### Jorge Eliecer Leighton Romero — MLOps Engineer

- Bloque 1 del Reto 04 terminado: pruebas de HU-03 y HU-07 (detalle en las secciones del 9 y 10 de noviembre). Se integró a `main` con el PR #38 (Approve de Juan, CI en verde).

---

## Miércoles 11 de noviembre

### Gloria Abimeleth Ardila — Data Steward

#### 1. PS-1: Detección de relajamiento del contrato por la CI

**Objetivo:** Demostrar que la integración continua (CI) detecta modificaciones no autorizadas del contrato de datos e
impide que cambios que incumplen los criterios de aceptación de HU-03 sean incorporados a la rama principal `main`.

##### Procedimiento

1. Se creó la rama `feat/r04-gloria-contrato-relajado` a partir de `main` actualizado con las pruebas automatizadas de
   HU-03 y HU-07 (incorporadas mediante el PR #38).
2. En `contracts/churn_contract.py` se modificó deliberadamente la regla **RC-3**, aumentando de 60 a 100 el límite de
   `monthly_charges` permitido para clientes con `internet_service = "none"`.
3. El cambio permitió que registros con cargos superiores al límite original fueran aceptados por el esquema,
   incumpliendo el contrato acordado con el dueño del dato.
4. Se conservaron intactas las pruebas existentes para verificar su capacidad de detectar el incumplimiento.

##### Validación local

Comando ejecutado:

```bash
uv run pytest tests/test_contract.py -v
```

| Resultado          | Cantidad |
|--------------------|---------:|
| Pruebas ejecutadas |       16 |
| Aprobadas          |       13 |
| Fallidas (RC-3)    |        3 |

Los tres fallos se produjeron porque el contrato relajado no generó la excepción `SchemaErrors` esperada ante registros
inválidos.

##### Validación en GitHub Actions

Se registró el cambio con el commit `a8423cf` y se creó el PR #39 hacia `main`.

| Resultado               | Cantidad |
|-------------------------|---------:|
| Pruebas aprobadas       |       23 |
| Pruebas fallidas        |        3 |
| Pruebas deseleccionadas |       12 |
| Código de salida        |        1 |

Pruebas fallidas:

- `test_rc3_sin_internet_con_cargo_alto_se_rechaza[training]`
- `test_rc3_sin_internet_con_cargo_alto_se_rechaza[features]`
- `test_hu03_sin_internet_con_cargo_de_fibra_falla_rc3`

En los tres casos se registró el mensaje `Failed: DID NOT RAISE SchemaErrors`, confirmando que la implementación
modificada aceptaba registros que debían rechazarse.


**Evidencia complementaria de CI — PS-1 (16/11/2026)**

- **Pull Request:** [PR #39](https://github.com/juanm0119/srt-v2-gjjj/pull/39), cerrado sin fusionar.
- **Ejecución de GitHub Actions:** #83.
- **Paso que presentó el fallo:** ejecución de las pruebas automatizadas del contrato en `tests/test_contract.py`.
- **Pruebas fallidas:** `test_rc3_sin_internet_con_cargo_alto_se_rechaza[training]`, `test_rc3_sin_internet_con_cargo_alto_se_rechaza[features]` y `test_hu03_sin_internet_con_cargo_de_fibra_falla_rc3`.
- **Causa:** las pruebas esperaban la excepción `SchemaErrors`, pero el contrato relajado aceptó los registros (`DID NOT RAISE SchemaErrors`).
- **Resultado:** 3 pruebas fallidas, 23 aprobadas y 12 deseleccionadas; código de salida 1.
- **Duración de las pruebas:** 5,72 segundos.
- **Duración total reportada de la ejecución CI #83:** 29 segundos. No equivale necesariamente al tiempo exacto hasta la detección del incumplimiento.

**Conclusión:** la CI detectó el incumplimiento deliberado de RC-3 y el PR #39 se cerró sin fusionarse, conservando el límite original de `monthly_charges <= 60` para clientes sin internet.

##### Resultado y decisión

La CI quedó en rojo por el incumplimiento deliberado de RC-3. El PR #39 se cerró sin fusionarse, conservando la
integridad de `main`. Posteriormente se verificó que `contracts/churn_contract.py` mantenía la condición original:

```python
| (df["monthly_charges"] <= 60)
```

**Estado:** PS-1 completada satisfactoriamente. El escenario demostró la capacidad de las pruebas automatizadas para
detectar el relajamiento indebido del contrato de datos.

---

#### 2. Decisión técnica 1: Privacidad de los datos utilizados en la CI

**Objetivo:** Proponer criterios para la selección y utilización segura de datos durante la ejecución de pruebas
automatizadas, garantizando la privacidad de la información y la reproducibilidad de los controles de calidad.

##### Procedimiento

- Se creó la rama independiente `docs/r04-gloria-privacidad-ci` para documentar la propuesta sin incorporar el cambio
  experimental de RC-3.
- En `docs/decision_log.md` se registró una propuesta técnica que diferencia los conjuntos de datos usados en las
  verificaciones funcionales de los requeridos para evaluar el desempeño predictivo del modelo.

##### Propuesta técnica

1. Utilizar datos sintéticos controlados para las pruebas funcionales y de validación del contrato, incluidas las reglas
   RC-2 y RC-3.
2. Utilizar registros sintéticos para comprobar los escenarios de comportamiento del modelo correspondientes a HU-07.
3. Utilizar conjuntos de evaluación representativos y autorizados, con acceso restringido, cuando sea necesario
   verificar métricas predictivas (ROC-AUC, recall, precision).
4. Evitar la publicación o exposición de información personal de los clientes del CRM en GitHub, artefactos o registros
   de ejecución de la CI.
5. Diferenciar las pruebas funcionales de las evaluaciones estadísticas, considerando que los datos sintéticos no
   sustituyen por sí solos la evaluación sobre datos representativos.

##### Alternativas consideradas

- Utilización de la base completa del CRM.
- Utilización de una muestra anonimizada de datos reales.
- Utilización exclusiva de conjuntos sintéticos.

Se propuso separar las pruebas según su finalidad para mantener los controles funcionales reproducibles, sin comprometer
la representatividad necesaria para evaluar el desempeño estadístico.

##### Integración de la documentación

- Commit `8ec7732`, presentado en el PR #40.
- GitHub Actions ejecutó satisfactoriamente las dos verificaciones:
    - CI / Imagen Docker y prueba de humo.
    - CI / Pruebas, pipeline y quality gate.
- El PR recibió la aprobación de Juan Manuel (Líder) y fue fusionado a `main`.
- La rama principal se actualizó en el entorno local, quedando sincronizada con `origin/main` en el commit `f916611`.

##### Resultado y decisión

La propuesta de privacidad quedó documentada e integrada al repositorio mediante el PR #40. Su incorporación documental
no constituye la aprobación definitiva de la política: conserva su estado pendiente de validación por los responsables
correspondientes, incluido el dueño del dato.

**Estado:** Contribución documental completada e integrada a `main`; validación de la decisión técnica pendiente.

---

#### 3. Conclusiones del aporte de Data Steward

Las actividades desarrolladas evidenciaron dos aspectos fundamentales de la gobernanza de datos en el Sistema de
Retención Temprana (SRT):

1. **Control de cambios:** la ejecución de PS-1 demostró que las pruebas automatizadas detectan una modificación
   incorrecta de la regla RC-3, generando un fallo verificable de CI antes de incorporar el cambio a `main`. El rechazo
   y cierre del PR #39, sin fusión, permitió preservar el contrato original.
2. **Privacidad:** se documentó una propuesta de uso seguro de datos para la CI, diferenciando las pruebas con datos
   sintéticos de la evaluación de métricas predictivas con datos representativos y autorizados.

Estos resultados fortalecen la trazabilidad, la reproducibilidad de las verificaciones y el control de modificaciones,
incorporando consideraciones de privacidad en el aseguramiento de calidad.

|                 |                                                                                            |
|-----------------|--------------------------------------------------------------------------------------------|
| **Responsable** | Gloria Ardila — Data Steward, equipo GJJJ                                                  |
| **Entregables** | PS-1 documentada (PR #39) y propuesta técnica de privacidad integrada (PR #40)             |
|  **Estado** | Aprobada formalmente el 2026-11-14 por el profesor Christian, PO académico, con condiciones de implementación. |


##### Aprobación formal y cierre de la propuesta — 14/11/2026

La propuesta formulada por Gloria Ardila, Data Steward, recibió aprobación interna de Juan Manuel Adarve, líder principal del equipo GJJJ, y aprobación formal del profesor Christian, PO académico, el 14 de noviembre de 2026.

**Condiciones aprobadas:**

1. Ejecutar en CI exclusivamente pruebas de contrato, comportamiento y pipeline con datos sintéticos controlados.
2. Realizar la evaluación de métricas sobre datos reales autorizados fuera de CI, en el equipo del MLOps Engineer.
3. Ejecutar localmente el Quality Gate contra `@champion` antes de cualquier promoción del modelo.
4. Conservar `reports/gate.json` como evidencia de la evaluación, evitando exponer información sensible.
5. Mantener el extracto real fuera de GitHub, incluidos secretos, registros y artefactos de CI.

**Gestión de riesgos:** se actualizaron R-03 (evaluación representativa), R-05 (equidad) y R-09 (privacidad), documentados en `docs/riesgos.md` mediante el PR #47.

**Trazabilidad:** propuesta inicial PR #40; decisiones de cierre PR #44; aprobación formal y riesgos PR #47.

**Estado de la decisión:** aprobada. La implementación de los controles técnicos y la mitigación de los riesgos continúan sujetas a verificación por los responsables correspondientes.

---

### Jorge Andrés Sánchez — Data Scientist

#### 1. Métricas del Champion

**Comando:** `uv run dvc metrics show`
**Archivo:** `metrics.json`

| Métrica                   |    Valor |
|---------------------------|---------:|
| customers_contacted       |      462 |
| f1                        |   0.6198 |
| net_savings_model         |  20010.0 |
| net_savings_random        |  4979.58 |
| net_savings_vs_random     | 15030.42 |
| pr_auc                    |   0.6389 |
| precision                 |   0.5628 |
| precision_at_eval         |   0.5268 |
| recall                    |   0.6897 |
| recall_at_eval            |    0.756 |
| recall_gap_senior_citizen |    0.116 |
| roc_auc                   |   0.8325 |

#### 2. Parámetros del quality gate

**Comando:** `Select-String -Path "params.yaml" -Pattern "^gate:" -Context 0,6`
**Archivo:** `params.yaml` (líneas 46-50)

```yaml
gate:
  eval_threshold: 0.30   # umbral fijo con el que se comparan todas las versiones
  min_roc_auc: 0.75
  min_recall: 0.70       # recall_at_eval (al eval_threshold)
  min_precision: 0.45    # precision_at_eval (al eval_threshold)
```

#### 3. Verificación del Champion contra el gate

| Parámetro       | Umbral | Métrica evaluada    | Valor obtenido | ¿Cumple? |
|-----------------|-------:|---------------------|---------------:|:--------:|
| `min_roc_auc`   |   0.75 | `roc_auc`           |         0.8325 |    ✅    |
| `min_recall`    |   0.70 | `recall_at_eval`    |          0.756 |    ✅    |
| `min_precision` |   0.45 | `precision_at_eval` |         0.5268 |    ✅    |

`eval_threshold = 0.30`: umbral fijo con el que se comparan todas las versiones.

## Lunes 9 de noviembre
### Jorge Eliecer Leighton Romero — MLOps Engineer (R del Reto 04)
**Rama:** `feat/pruebas-aceptacion`

##### Paso 1 · Partir de `main` en verde
- `git switch main` y `git pull`: `main` quedó en `280ec32` (cierre del Reto 03, tag `r03`).
- `uv sync --frozen`: 207 paquetes.
- `dvc pull`: "Everything is up to date."
- `dvc repro`: "Data and pipelines are up to date.", sin re-ejecutar ninguna etapa.
- `uv run pytest`: **36 passed**, sin failed ni skipped (incluye las pruebas del modelo).
- CI en GitHub: la última ejecución sobre `main` (#80, commit `280ec32`) pasó, con los dos jobs en verde:
  - Pruebas, pipeline y quality gate.
  - Imagen Docker y prueba de humo.

**Incidente:** Windows bloqueó el `python.exe` del entorno (os error 4551, Control de aplicaciones de Windows). Se resolvió borrando `.venv` y recreándolo con `uv sync --frozen`. Después, `uv run python --version` dio Python 3.12.15.

##### Paso 2 · Crear la rama de trabajo
- `git switch -c feat/pruebas-aceptacion`.
- Desde este reto, ningún cambio entra a `main` sin PR.

## Lunes 9 y martes 10 de noviembre
### Jorge Eliecer Leighton Romero — MLOps Engineer (R del Reto 04)

##### Paso 3 · HU-03: pruebas que nombran la regla

Se agregaron al final de `tests/test_contract.py` (líneas 74 a 93):

| Prueba | Escenario de HU-03 | Qué verifica |
|---|---|---|
| `test_hu03_categoria_fuera_del_dominio_falla_rc2` | Lote con `contract_type = "Month-to-month"` | Que la falla sea exactamente de RC-2 (regla `isin` sobre `contract_type`), con `features_schema` |
| `test_hu03_sin_internet_con_cargo_de_fibra_falla_rc3` | Cliente con `internet_service = "none"` y `monthly_charges = 90` | Que en las fallas aparezca "RC-3", con `training_schema` |

Las dos pruebas verifican la regla que falla, no solo que "algo falle". Si desaparece la regla, la prueba se pone en rojo aunque falle otra.

**Verificación 1: las pruebas pasan**

```text
uv run pytest tests/test_contract.py -v -k hu03
test_hu03_categoria_fuera_del_dominio_falla_rc2 PASSED
test_hu03_sin_internet_con_cargo_de_fibra_falla_rc3 PASSED
2 passed, 14 deselected
```

**Verificación 2: la prueba puede fallar**

Se cambió temporalmente RC-3 de `<= 60` a `<= 100` en `contracts/churn_contract.py` (línea 31):

```text
test_hu03_categoria_fuera_del_dominio_falla_rc2 PASSED
test_hu03_sin_internet_con_cargo_de_fibra_falla_rc3 FAILED
Failed: DID NOT RAISE SchemaErrors
1 failed, 1 passed, 14 deselected
```

Con el contrato relajado, el cliente sin internet con cargo de 90 ya no se detecta y la prueba lo señala, lo que demuestra que no es decorativa. Después se restauró el contrato con `git restore contracts/churn_contract.py`, por lo que el contrato no se modificó.

Commit `b03ea0c`.

##### Paso 4 · HU-07: escenarios citados y umbrales leídos de `params.yaml`

Cambios en `tests/test_model_behavior.py`:

- `test_direction_contract` y `test_direction_support_tickets` citan ahora su escenario de HU-07 en el docstring; el cuerpo de las pruebas no cambió.
- `test_metrics_meet_minimum_thresholds` verifica las **tres** métricas del gate (`roc_auc`, `recall_at_eval` y `precision_at_eval`) contra `gate.*` de `params.yaml`, los mismos valores que aplica `scripts/quality_gate.py`. Antes solo verificaba `roc_auc`.

**Verificación 1: las pruebas pasan**

```text
uv run pytest tests/test_model_behavior.py -v
test_probabilities_are_valid PASSED
test_direction_contract PASSED
test_direction_support_tickets PASSED
test_invariance_to_customer_id PASSED
test_metrics_meet_minimum_thresholds PASSED
5 passed
```

**Verificación 2: la prueba de umbrales puede fallar**

Se cambió temporalmente `gate.min_recall` a 0.99 en `params.yaml` (línea 49):

```text
test_metrics_meet_minimum_thresholds FAILED
AssertionError: recall_at_eval=0.756 < gate.min_recall=0.99
1 failed, 4 passed
```

La prueba lee los valores del gate desde `params.yaml`: cuando el gate cambie, la prueba usará los mismos valores sin que nadie la toque. Se restauró con `git restore params.yaml`. Commit `bc84be4`.

##### Paso 5 · Tabla de trazabilidad

Incluye las pruebas del bloque 3 (inferencia batch, 13 de noviembre).

| HU · escenario | Archivo · prueba | Marcador | ¿Pasa? |
|---|---|---|:---:|
| HU-03 · categoría fuera del dominio (RC-2) | `tests/test_contract.py::test_hu03_categoria_fuera_del_dominio_falla_rc2` | — | ✅ PASSED |
| HU-03 · … y no se genera `reports/predictions/` | `tests/test_predict_batch.py::test_hu03_lote_invalido_no_genera_predicciones` | `model` | ✅ PASSED |
| HU-03 · sin internet con cargo de fibra (RC-3) | `tests/test_contract.py::test_hu03_sin_internet_con_cargo_de_fibra_falla_rc3` | — | ✅ PASSED |
| HU-07 · direccionalidad del contrato | `tests/test_model_behavior.py::test_direction_contract` | `model` | ✅ PASSED |
| HU-07 · direccionalidad de los tickets | `tests/test_model_behavior.py::test_direction_support_tickets` | `model` | ✅ PASSED |
| HU-07 · invariancia al identificador | `tests/test_model_behavior.py::test_invariance_to_customer_id` | `model` | ✅ PASSED |
| HU-07 · umbrales mínimos | `tests/test_model_behavior.py::test_metrics_meet_minimum_thresholds` | `model` | ✅ PASSED |
| HU-08 · la lista respeta la capacidad | `tests/test_predict_batch.py::test_hu08_lista_respeta_capacidad_orden_y_version` | `model` | ✅ PASSED |
| HU-08 · versión en cada fila | `tests/test_predict_batch.py::test_hu08_cada_fila_de_la_lista_indica_la_version` | `model` | ✅ PASSED |

Todas corren en la CI: las de contrato en el paso de pruebas unitarias y las de marcador `model` después de `dvc repro`.

##### Paso 6 · PR, revisión y merge

- PR #38 de `feat/pruebas-aceptacion` a `main`, con 2 archivos: `tests/test_contract.py` y `tests/test_model_behavior.py`.
- CI del PR en verde (2 checks), Approve de Juan y merge `55f9175` (11 de noviembre).
- Al abrir el PR, GitHub mostró *"Merging is blocked: at least 1 approving review is required"*: la protección de `main` ya estaba activa.

## Jueves 12 de noviembre
### Juan Manuel Adarve — Lider
* Registro de bítacora

## Viernes 13 de noviembre
### Jorge Eliecer Leighton Romero — MLOps Engineer

**Rama:** `feat/inferencia-batch`

##### Paso 1 · Rama y lectura de la base
- `git switch main` y `git pull`: `main` quedó en `f916611` (merge del PR #40).
- `git switch -c feat/inferencia-batch`.
- `Select-String -Path src/predict_batch.py -Pattern "TODO"`: 3 pendientes, en `prioritize` (línea 46), en el registro del rechazo (línea 61) y en la lista del lunes (línea 75).
- `git check-ignore -v`: `reports/predictions/` y `reports/rejected/` están ignoradas (`.gitignore`, líneas 23 y 24), así que las salidas del batch nunca llegan a GitHub.
- Lote de prueba: `make_production_batch --scenario normal` → 1500 filas.
- La base actual da:

```text
[predict] 1500 clientes · 478 en riesgo · modelo v1 → reports\predictions\batch_normal_scored.csv
```

- `git status --short` salió vacío.

##### Paso 2 · La capacidad: `prioritize` (commit `d9490bd`)

En `src/predict_batch.py`, `prioritize` (HU-08) hace cuatro cosas:

1. Filtra los clientes en riesgo (`churn_pred == 1`).
2. Los ordena de mayor a menor probabilidad.
3. Recorta a la capacidad.
4. Devuelve solo 4 columnas: `prioridad`, `customer_id`, `churn_probability` y `model_version` (minimización, Ley 1581).

##### Paso 3 · La lista del lunes y `--capacity` (commit `5739720`)

El script escribe `reports/predictions/<lote>_lista.csv` con la capacidad de V2 (`business.weekly_capacity = 900`). El argumento `--capacity` permite cambiarla en las pruebas.

```text
uv run python -m src.predict_batch data/production/batch_normal.csv
[predict] 1500 clientes · 478 en riesgo · lista 478/900 · modelo v1

uv run python -m src.predict_batch data/production/batch_normal.csv --capacity 250
[predict] 1500 clientes · 478 en riesgo · lista 250/250 · modelo v1
```

- Con capacidad de 900 entran los 478 en riesgo.
- Con 250 se recorta la lista, no el riesgo: siguen siendo 478 en riesgo y los 228 restantes no caben esta semana.
- La lista tiene encabezado `prioridad,customer_id,churn_probability,model_version` y probabilidades descendentes (0,9426 → 0,913 → 0,91 en las 3 primeras filas).

##### Paso 4 · El registro del rechazo (commit `b115747`)

- Nueva función `reglas_violadas`: resume las fallas por regla, solo con conteos y sin valores ni identificadores (contrato §7.4).
- Si el lote viola el contrato, el script escribe `reports/rejected/<lote>.json` con el nivel `CRÍTICO-CONTRATO`, no escribe predicciones y termina con código 2.
- **Ajuste frente a la guía:** la línea del `return` de `reglas_violadas` se partió en 3 para cumplir el límite de 110 caracteres de ruff. El comportamiento es el mismo.

**Verificación con el lote `esquema`:**

```text
uv run python -m src.predict_batch data/production/batch_esquema.csv; echo "código: $LASTEXITCODE"
[predict] 🛑 CRÍTICO-CONTRATO: el lote viola el contrato (227 fallas): no se predice → reports\rejected\batch_esquema.json
código: 2
```

```json
{
  "nivel": "CRÍTICO-CONTRATO",
  "lote": "batch_esquema.csv",
  "fecha": "2026-11-13T20:18:34+00:00",
  "filas_del_lote": 1500,
  "reglas_violadas": {
    "(tabla) · RC-3: sin internet con cargo mayor a 60": 1,
    "internet_service · isin(['dsl', 'fiber', 'none'])": 225,
    "monthly_charges · column_in_dataframe": 1
  }
}
```

El registro no contiene ningún `customer_id`.

##### Paso 5 · Las pruebas del batch (commit `7b22e09`)

Archivo nuevo `tests/test_predict_batch.py`, con el marcador `model` y una carpeta temporal (`tmp_path`) para no tocar `reports/`:

| Prueba | Qué verifica |
|---|---|
| `test_hu08_lista_respeta_capacidad_orden_y_version` | Con capacidad 50: exactamente 50, orden descendente y con versión |
| `test_hu08_cada_fila_de_la_lista_indica_la_version` | El script completo escribe la lista con solo las 4 columnas y versión en cada fila |
| `test_hu03_lote_invalido_no_genera_predicciones` | Con `"Month-to-month"`: código 2, ningún archivo de predicciones y registro sin el `customer_id` |

Las pruebas pasan: **3 passed**.

**La prueba de orden puede fallar.** Con `ascending=True` temporalmente en `prioritize`:

```text
test_hu08_lista_respeta_capacidad_orden_y_version FAILED
assert lista["churn_probability"].is_monotonic_decreasing  → assert False
1 failed, 2 passed
```

Se restauró con `git restore src/predict_batch.py` y volvió a dar 3 passed.

##### Paso 6 · PR, revisión y merge
- Antes del PR:
  - `uv run ruff check .` → "All checks passed!"
  - `uv run pytest` → **41 passed**
  - `git status --short` vacío, sin ningún `.csv` ni `.json` de `reports/`.
- PR #42 de `feat/inferencia-batch` a `main`, con 2 archivos: `src/predict_batch.py` y `tests/test_predict_batch.py`.
- CI del PR en verde (2 checks), Approve de Juan y merge `ec15534` (16 de noviembre).

Las tres pruebas del batch quedaron en la tabla de trazabilidad (bloque 1, paso 5).

### Juan Manuel Adarve — Lider
* Se envia propuesta de metricas del modelo a PO
* PO aprueba propuesta con modificaciones. max_drop_vs_champion = 0.035 teniendo en cuenta que con el extracto de V2 solo cambiar la semilla de partición mueve el ROC-AUC más de 0.03. Con 0.01, casi cualquier reentrenamiento legítimo sería rechazado por ruido; su ejemplo del Random Forest, rechazado por 0.0004, lo muestra. El escenario 2 lo sigue deteniendo min_recall.

## Sábado 14 de noviembre
### Juan Manuel Adarve — Lider
* Aprobación de PRs #42, #43, #44 y #45 y #47
### Gloria Abbymeleth Ardila — Data Steward
* Aprobación y registro en **datos_gobernanda.md** privacidad en integración continua (CI). PR #44
### Jorge Andrés Sánchez — Data Scientist
* Ajustes de valores de métricas y reejecución de metricas, pruebas y validaciones
**Comando:** `uv run ruff check`
**Resultado:** ✅ Todas las verificaciones pasaron.

```terminaloutput
All checks passed!
```

```terminaloutput
PS C:\Andres\Maestria\Gerencia_Proyectos\Proyecto\srt-jjjg> uv run pytest
=========================================================== test session starts ===========================================================
platform win32 -- Python 3.12.15, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Andres\Maestria\Gerencia_Proyectos\Proyecto\srt-jjjg
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.15.1, Faker-40.43.0, hydra-core-1.3.7, platformdirs-4.13.0, typeguard-4.6.0
collected 38 items

tests\test_api.py .....                                                                                                             [ 13%]
tests\test_contract.py ................                                                                                             [ 55%]
tests\test_llm_assistant.py ........                                                                                                [ 76%]
tests\test_model_behavior.py .....                                                                                                  [ 89%]
tests\test_pipeline.py ....                                                                                                         [100%]

============================================================ 38 passed in 7.40s ============================================================
```

```terminaloutput
PS C:\Andres\Maestria\Gerencia_Proyectos\Proyecto\srt-jjjg> uv run dvc metrics diff main
Path          Metric                     main      workspace    Change
metrics.json  customers_contacted        462       252          -210
metrics.json  f1                         0.6198    0.5183       -0.1015
metrics.json  net_savings_model          20010.0   13297.5      -6712.5
metrics.json  net_savings_random         4979.58   2716.13      -2263.45
metrics.json  net_savings_vs_random      15030.42  10581.37     -4449.05
metrics.json  pr_auc                     0.6389    0.6106       -0.0283
metrics.json  precision                  0.5628    0.6468       0.084
metrics.json  precision_at_eval          0.5268    0.5253       -0.0015
metrics.json  recall                     0.6897    0.4324       -0.2573
metrics.json  recall_at_eval             0.756     0.6897       -0.0663
metrics.json  recall_gap_senior_citizen  0.116     0.0709       -0.0451
metrics.json  roc_auc                    0.8325    0.8087       -0.0238
```

#### Escenario 2 · Un modelo "igual de bueno" según el AUC (PS-2)

- **Cambio:** rama `exp/regularizacion-fuerte`, commit `a298069`, con `model.logistic_regression.C` de 1.0 a **0.0005** en `params.yaml`.
- **Resultado local con datos reales** (`dvc metrics diff main`, arriba): `roc_auc` baja solo 0,0238 (de 0,8325 a 0,8087), pero `recall_at_eval` cae a **0,6897**, por debajo de `gate.min_recall = 0,70`, y `recall` a 0,4324. El modelo deja de encontrar desertores aunque el AUC parezca similar.
- **PR #46** hacia `main`: la CI (ejecución #93) **falló en el paso Quality gate**; **tiempo hasta detectar: 44 s**. En la CI corre el extracto sintético (sin acceso al remoto), donde el profesor reporta `recall_at_eval = 0,6953`, también por debajo de 0,70.
- **Decisión:** PR #46 cerrado sin fusionar (17 de noviembre). El modelo regularizado no entró a `main` (`C` sigue en 1.0) y la rama se eliminó.
- **Lección:** con `git add -A` se incluyó en el commit del experimento el CSV sintético `data/raw/churn.csv`, que quedaba sin ignorar desde que se retiró la etapa `ingest` en el Reto 03. No contiene datos personales y no llegó a `main`; el PR #45 lo agregó a `.gitignore`.

## Lunes 16 de noviembre
### Jorge Eliecer Leighton Romero — MLOps Engineer
#### Verificación del gate negociado contra el `@champion` (bloque 2, paso 2)

**Dónde:** computador del MLOps, contra el `@champion` local (condiciones 2 a 4 de la decisión de privacidad) · **Base:** `main` (`a2e0566`, después del merge del PR #45)

- **Cambio aplicado por el PR #45:** `max_drop_vs_champion` de 0.01 a 0.035, por decisión del profesor.
- **Valores que se mantienen:** `eval_threshold` 0.30, `min_roc_auc` 0.75, `min_recall` 0.70 y `min_precision` 0.45.
- No fue necesario re-ejecutar el pipeline: `evaluate` solo depende de `gate.eval_threshold`, que no cambió.

```text
uv run python -m scripts.quality_gate; echo "código: $LASTEXITCODE"
  ✅ roc_auc >= 0.75  (valor: 0.8325)
  ✅ recall_at_eval >= 0.7 (umbral 0.3)  (valor: 0.756)
  ✅ precision_at_eval >= 0.45 (umbral 0.3)  (valor: 0.5268)
  ✅ roc_auc >= champion v1 (0.8325) - 0.035  (valor: 0.8325)
[gate] ✅ challenger v1 aprobado
código: 0
```

- `reports/gate.json`: `challenger_version: "1"`, `"passed": true`, con las 4 reglas en `true`. Se conserva localmente como evidencia y no se sube a Git.
- **Resultado:** el modelo vigente pasa el gate acordado. Con la nueva tolerancia, el mínimo admisible de `roc_auc` frente al champion es 0,7975, lo que cubre la variación por semilla observada (la semilla 2031 dio 0,8007).

---

#### PS-4 · La lista del lunes respeta la capacidad

**Base:** `main` (`ec15534`, después del merge del PR #42)

```text
uv run python -m monitoring.make_production_batch --scenario normal
[batch] 1500 filas, escenario 'normal' → data\production\batch_normal.csv

uv run python -m src.predict_batch data/production/batch_normal.csv --capacity 250
[predict] 1500 clientes · 478 en riesgo · lista 250/250 · modelo v1 → reports\predictions
```

- Se recorta la lista, no el riesgo: siguen 478 clientes en riesgo y solo 250 caben en la capacidad indicada. Con la capacidad de V2 (900), la lista tiene los 478.
- La lista tiene solo 4 columnas (`prioridad,customer_id,churn_probability,model_version`).
- Las probabilidades van de mayor a menor (0,9426 → 0,913 → 0,91) y cada fila indica `model_version = 1`.

---

#### PS-5 · Un lote inválido no produce predicciones

**Base:** `main` (`ec15534`)

```text
uv run python -m monitoring.make_production_batch --scenario esquema
[batch] 1500 filas, escenario 'esquema' → data\production\batch_esquema.csv

uv run python -m src.predict_batch data/production/batch_esquema.csv; echo "código: $LASTEXITCODE"
[predict] 🛑 CRÍTICO-CONTRATO: el lote viola el contrato (227 fallas): no se predice → reports\rejected\batch_esquema.json
código: 2
```

Predicciones de `batch_esquema` en `reports/predictions`: sin predicciones para `batch_esquema` ✅

```json
{
  "nivel": "CRÍTICO-CONTRATO",
  "lote": "batch_esquema.csv",
  "fecha": "2026-11-16T19:22:17+00:00",
  "filas_del_lote": 1500,
  "reglas_violadas": {
    "(tabla) · RC-3: sin internet con cargo mayor a 60": 1,
    "internet_service · isin(['dsl', 'fiber', 'none'])": 225,
    "monthly_charges · column_in_dataframe": 1
  }
}
```

El lote se rechazó antes de puntuar: código 2, ninguna predicción escrita, y el registro para el dueño del dato tiene solo conteos por regla, sin ningún `customer_id`.

---

#### Evidencia de `min_recall` y de la tolerancia de no regresión con distintas semillas de partición

Responde a la decisión 3 de la retroalimentación docente (`docs/decision_log.md`): *"Conservar evidencia del comportamiento del criterio `min_recall` ante las semillas 42, 7, 123 y 2031"*.

**Dónde:** computador del MLOps, con el extracto real (condición 2 de la decisión de privacidad) · **Base:** `main` (`9b717bb`)

**Procedimiento:** se cambió solo `split.seed` con `uv run python -m dvc exp run -S split.seed=<semilla> -n semilla-<semilla>`. El modelo (Regresión Logística, C = 1.0), los datos y el resto de `params.yaml` no cambiaron. Sin commit. Al final se restauró con `git restore .` y `dvc checkout`, y `dvc status` dio "Data and pipelines are up to date.". El `@champion` (v1) no cambió; cada corrida quedó como `@challenger` en el registro local.

| Semilla | roc_auc | Diferencia vs. `@champion` (0,8325) | recall_at_eval | precision_at_eval | recall_gap_senior_citizen |
|---|---:|---:|---:|---:|---:|
| 42 (baseline, `@champion` v1) | 0,8325 | — | 0,7560 | 0,5268 | 0,116 |
| 7 | 0,8403 | +0,0078 | 0,7719 | 0,5369 | 0,0279 |
| 123 | 0,8332 | +0,0007 | 0,7427 | 0,5395 | 0,0214 |
| 2031 | 0,8007 | −0,0318 | 0,7003 | 0,5087 | 0,0676 |

**Resultados:**

1. **El ruido de la partición es grande:** solo con cambiar la semilla, `roc_auc` varía entre 0,8007 y 0,8403 (rango de 0,0396), lo que confirma lo señalado por el profesor.
2. **Tolerancia de no regresión:** con `max_drop_vs_champion = 0,01`, la semilla 2031 (caída de 0,0318) se habría rechazado aunque es un re-entrenamiento legítimo. Con 0,035 (PR #45) pasan las 4 semillas, lo que respalda el cambio.
3. **`min_recall = 0,70`:** las 4 semillas lo cumplen, pero la 2031 queda en 0,7003, solo 0,0003 por encima del límite: el umbral está en el borde de la variación por ruido. No se modifica sin autorización expresa del profesor.
4. **Equidad:** la brecha de `senior_citizen` también depende de la partición (entre 0,0214 y 0,116); solo la semilla 42 supera el límite de 0,10. Se registra para el seguimiento del riesgo de equidad del Reto 06.

### Juan Manuel Adarve — Lider
* aprobación del PR #48

## Martes 17 de noviembre
### Jorge Eliecer Leighton Romero — MLOps Engineer

#### PS-2 · El gate rechaza un modelo con AUC parecido

**Dónde:** computador del MLOps, con el extracto real y contra el `@champion` local (condiciones 2 a 4 de la decisión de privacidad) · **Base:** `main` (`1405e2a`, con el gate de 0.035)

**Procedimiento:** se corrió el modelo regularizado del escenario 2 como experimento, sin commit: `uv run python -m dvc exp run -S model.logistic_regression.C=0.0005 -n regularizacion-fuerte`. Dio las mismas métricas que obtuvo Jorge Andrés en su rama (`roc_auc` 0,8087 y `recall_at_eval` 0,6897).

```text
uv run python -m dvc metrics diff main
Path          Metric                     main      workspace    Change
metrics.json  customers_contacted        462       252          -210
metrics.json  f1                         0.6198    0.5183       -0.1015
metrics.json  net_savings_model          20010.0   13297.5      -6712.5
metrics.json  net_savings_random         4979.58   2716.13      -2263.45
metrics.json  net_savings_vs_random      15030.42  10581.37     -4449.05
metrics.json  pr_auc                     0.6389    0.6106       -0.0283
metrics.json  precision                  0.5628    0.6468       0.084
metrics.json  precision_at_eval          0.5268    0.5253       -0.0015
metrics.json  recall                     0.6897    0.4324       -0.2573
metrics.json  recall_at_eval             0.756     0.6897       -0.0663
metrics.json  recall_gap_senior_citizen  0.116     0.0709       -0.0451
metrics.json  roc_auc                    0.8325    0.8087       -0.0238

uv run python -m scripts.quality_gate; echo "código: $LASTEXITCODE"
  ✅ roc_auc >= 0.75  (valor: 0.8087)
  ❌ recall_at_eval >= 0.7 (umbral 0.3)  (valor: 0.6897)
  ✅ precision_at_eval >= 0.45 (umbral 0.3)  (valor: 0.5253)
  ✅ roc_auc >= champion v1 (0.8325) - 0.035  (valor: 0.8087)
[gate] ❌ challenger v5 rechazado
código: 1
```

```json
{
  "challenger_version": "5",
  "passed": false,
  "checks": [
    {"rule": "roc_auc >= 0.75", "value": 0.8087, "passed": true},
    {"rule": "recall_at_eval >= 0.7 (umbral 0.3)", "value": 0.6897, "passed": false},
    {"rule": "precision_at_eval >= 0.45 (umbral 0.3)", "value": 0.5253, "passed": true},
    {"rule": "roc_auc >= champion v1 (0.8325) - 0.035", "value": 0.8087, "passed": true}
  ]
}
```

- `roc_auc` casi igual (−0,0238): pasa el mínimo de 0,75 y la regla de no regresión con la tolerancia de 0,035.
- `recall_at_eval` = 0,6897 queda por debajo de `gate.min_recall` = 0,70: es la única regla que falla. El gate detiene un modelo que deja de encontrar desertores aunque su AUC parezca similar.
- Se restauró con `git restore .` y `dvc checkout`; `dvc status` dio "Data and pipelines are up to date.". El `@champion` (v1) no cambió.

#### PR rechazados por la CI

| Escenario | Enlace al PR | Paso que falló | Tiempo hasta detectar | Decisión |
|---|---|---|---|---|
| 1 · contrato relajado (RC-3 de 60 a 100) | [PR #39](https://github.com/juanm0119/srt-v2-gjjj/pull/39) | Pruebas unitarias y de contrato de datos (3 pruebas de RC-3 fallidas) | 29 s (duración de la ejecución #83) | Cerrado sin fusionar |
| 2 · modelo regularizado (C = 0.0005) | [PR #46](https://github.com/juanm0119/srt-v2-gjjj/pull/46) | Quality gate (`recall_at_eval` bajo `gate.min_recall`) | 44 s (duración de la ejecución #93) | Cerrado sin fusionar |

## Lunes 16 de noviembre
### Juan Manuel Adarve — Lider
* PR #46 (escenario 2, modelo regularizado): cerrado sin fusionar; la CI lo rechazó en el paso Quality gate, como se esperaba.
