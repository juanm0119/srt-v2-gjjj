# Bitácora del Reto 04 — Equipo GJJJ

## Martes 10 de noviembre

### Equipo

- Aprobación de los PR #38, #39 y #40.

### Jorge Leigthon

- Bloque 1 del Reto 04 terminado, indicado en el PR #38.

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
- El PR recibió la aprobación de Juan Manuel (Líder/PO) y fue fusionado a `main`.
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

### Jorge Sanchez — MLOps Engineer

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

## Jueves 12 de noviembre
### Juan Manuel Adarve — Lider
* Registro de bítacora