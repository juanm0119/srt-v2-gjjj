# Bitácora del Reto 02 — Equipo GJJJ

## Octubre 30 del 2026
### Juan Manuel Adarve
* Se socializa propuestas para manejo de registros anómalos que afectarían las predicciones y entrenamiento del modelo.
* Entrega de propuestas aprobada para manejo de registros anómalos a Data Steward

### Jorge Eliecer Leighton
* **Revisión y aprobación del PR #13.** Confirmé que no tenía ningún CSV ni customer_id, y que el extracto en DVC es el original de Classroom
* **PR #14.** Rutas CRM_EXTRACT y CLEAN_DATA en src/common.py, /clean.csv en data/processed/.gitignore, y validar_contrato.py restaurado sin cambios, como pide el reto.
* Comprobación de archivos `csv` del folder data/ estén ignorados
```bash
git check-ignore -v data/raw/crm_extracto.csv data/processed/clean.csv
```
> data/raw/.gitignore:2:/crm_extracto.csv    data/raw/crm_extracto.csv
> data/processed/.gitignore:3:/clean.csv     data/processed/clean.csv

y solo existia el `roc_curve.csv` desde el commit inicial
```shell
git --no-pager log --all --stat -- "*.csv" | Select-Object -First 10
```
> commit bab53f05dea6c0d0cd0921a2ccd8139fced08d98
> Author: juanm0119
> Date:   Fri Oct 16 21:34:01 2026 -0500
>    Initial commit
> reports/roc_curve.csv | 425 +++++
> 1 file changed, 425 insertions(+)


## Octubre 31 del 2026
### Juan Manuel Adarve
* Aprobación de PRs #16, #17 y #18
* Registro de propuestas aprobadas por Sponsor en `decision_log.md`

### Jorge Andrés Sánchez
* Creación de PR #16 y #17 para corrección de calidad de código, además, para validar el RC-3

### Gloria Abimeleth Ardila
* Registro de propuestas aprobadas de manejo de registros anormales en datos_gobernanza.md
* Creación de archivo de `clean.py` para tratamiento y limpieza de datos

### Jorge Eliecer Leighton
* Creación de pruebas unitarias al RC-3 y RC-5

## Noviembre 1 del 2026
### Jorge Eliecer Leighton
* PS-3 (PR #19, ya en main): pruebas de RC-3, RC-5 y descarte máximo en test_contract.py.
    ✅ 14 passed
    ❌ Con RC-3 comentada: 2 failed (las de RC-3). Restaurada: 14 passed.
    PS-5: a una copia del extracto con el 20 % de monthly_charges vacío le apliqué la limpieza y el contrato.

> 7042 → 5511 filas, 21,7 % descartado
* El contrato v2 pasa ✅ (por sí solo no detecta la pérdida)
discard_ok = False → 🛑 bloqueado (máximo 5 %)
El extracto real descarta 2,2 %, así que sí pasa.

## Noviembre 2 del 2026
### Jorge Andrés Sánchez
* Resultados de script de comprobación de contrato sobre el archivo crm_extracto.csv
```shell
uv run  python -m scripts.validar_contrato advertencias data/raw/crm_extracto.csv
```
```terminaloutput
[advertencias] data/raw/crm_extracto.csv: 7042 filas · 13 columnas
    ❌ 2 reglas incumplidas
    columna                                 regla                               filas afectadas
(entre columnas / esquemas)                fecha_alta vacia                            28
(entre columnas / esquemas)                fecha_alta posterior a fecha_corte          20
```
* aprobación de PRs #21 y #22
### Gloria Abimeleth Ardila
* PS-2
> Entrada: 7.042 registros.
> Descartados: 156 registros (2,2 %).
> Resultado: 6.886 registros conservados.
> Se generaron data/processed/clean.csv y reports/cleaning.json, con los datos limpios y el resumen de tratamientos.
* aprobación de PRs #23 y #24

### Jorge Eliecer Leighton
* aprobación de PRs #25 y #26

---

## Pruebas del sistema (resumen de evidencias)

### PS-1 · El extracto no entra a Git (Jorge Eliecer Leighton)

```
git status --short data/
(sin salida)
git check-ignore -v data/raw/crm_extracto.csv data/processed/clean.csv
data/raw/.gitignore:2:/crm_extracto.csv       data/raw/crm_extracto.csv
data/processed/.gitignore:3:/clean.csv        data/processed/clean.csv
git --no-pager log --all --stat -- "*.csv" | Select-Object -First 10
bab53f0 Initial commit · reports/roc_curve.csv
```

El único CSV del historial es `reports/roc_curve.csv`, de la plantilla (columnas `fpr,tpr`, sin datos de clientes). El extracto nunca entró a Git: está bajo DVC (`data/raw/crm_extracto.csv.dvc`) e ignorado. En PowerShell no existe `head`; se usó `Select-Object -First 10`.

### PS-2 · El contrato v2 pasa sobre el limpio y falla sobre el crudo (Jorge Andrés Sánchez y Gloria Abimeleth Ardila)

| Validación | Resultado |
|---|---|
| `uv run python -m src.clean` | 7042 → 6886 filas, 156 descartadas (2,22 %) |
| `validar_contrato v2 data/processed/clean.csv` | ✅ sin fallas |
| `validar_contrato v2 data/raw/crm_extracto.csv` | ❌ 8 reglas incumplidas, entre ellas RC-3 (17 filas) y RC-5 (4 columnas no canónicas) |
| `validar_contrato advertencias data/raw/crm_extracto.csv` | ⚠️ 2 advertencias: `fecha_alta` vacía (28) y `fecha_alta` posterior a `fecha_corte` (20) |

Detalle en `docs/datos_gobernanza.md` §2.1 y §4.5.

### PS-3 · Las pruebas rechazan datos inválidos (Jorge Eliecer Leighton)

`tests/test_contract.py` conserva las pruebas de la plantilla y agrega RC-5 (las 4 columnas no canónicas), RC-3 (en `training_schema` y `features_schema`) y descarte máximo (`discard_ok`).

```
uv run pytest tests/test_contract.py -v      → 14 passed
(RC-3 comentada solo en local, sin commit)    → 2 failed, 12 passed: test_rc3_...[training] y [features] - DID NOT RAISE SchemaErrors
git restore contracts/churn_contract.py      → 14 passed · working tree clean
```

### PS-4 · La fuga, cuantificada (Jorge Andrés Sánchez)

| `oferta_retencion_aceptada` | Registros | Tasa de churn |
|---|---:|---:|
| 0 | 5.544 | 33,91 % |
| 1 | 1.498 | 3,47 % |

Línea de tiempo: corte → lote del lunes → campaña → registro de la oferta → etiqueta de churn a 30 días. El resultado de la oferta se registra después de la predicción del lunes; usarlo como predictor es fuga de información. La columna se excluye del modelo (contrato §2.3, RC-5). Detalle en `docs/datos_gobernanza.md` §3.3.

### PS-5 · La limpieza no esconde un lote corrupto (Jorge Eliecer Leighton)

Copia del extracto **fuera del repositorio** con el 20 % de `monthly_charges` vacío (1454 filas, semilla 42). Se le aplicó `clean()` y el contrato v2 sin escribir en el repositorio:

```
excluidas_monthly_charges_nulo: 1454 · filas: 7042 → 5511
Contrato v2 sobre el lote limpio: ✅ sin fallas
proporcion_descartada = 0.2174 (máximo permitido: 0.05)
discard_ok = False → 🛑 BLOQUEADO
```

El contrato por sí solo no detecta la pérdida del 21,7 % de las filas; la regla de descarte máximo sí. El extracto real descarta 2,22 % y pasa.

## Defectos que el contrato canónico no detectó

Al correr el contrato de la plantilla sobre el extracto crudo (7 reglas incumplidas), quedaron sin detectar como controles específicos (`datos_gobernanza.md` §2.2):

- **RC-3**: 17 clientes sin internet con cargo mayor a 60 → se agregó RC-3 bloqueante al contrato v2.
- **`fecha_alta` vacía** (28) y **`fecha_alta` posterior a `fecha_corte`** (20): el contrato solo rechaza esas columnas por no ser canónicas, sin revisar sus valores → advertencias en `contracts/crm_warnings.py`.
- **Copias exactas frente a registros discordantes**: el contrato detecta los `customer_id` repetidos (84 filas), pero no distingue las 22 copias exactas de los registros con datos distintos → lo resuelve la limpieza.
- **Pérdida masiva de filas al limpiar**: ningún esquema la detecta → regla `discard_ok` (PS-5).

## Decisiones técnicas

- **Excluir o imputar:** se excluyen las 57 filas con `monthly_charges` nulo (0,8 %), sin imputar. Imputar introduciría un cargo estimado en una variable predictora y podría crear casos que violen RC-3; el descarte total queda en 2,22 %.
- **Presupuesto de descarte:** `MAX_DISCARD_SHARE = 0.05`. El extracto real descarta 2,22 % (156 de 7.042); el 5 % permite hasta 352 descartes, con margen para variaciones sin aceptar pérdidas masivas. Un lote con 20 % de nulos queda bloqueado (PS-5).

Justificación completa y alternativas en `docs/decision_log.md` (sección Reto 02).

## Quién hizo qué

| Integrante | Aporte al Reto 02 |
|---|---|
| Juan Manuel Adarve Cifuentes (Líder / PO) | Ronda de negociación de tratamientos, registro inicial de decisiones, bitácora, aprobación de PR y tag `r02` |
| Jorge Eliecer Leighton Romero (MLOps) | Rutas `CRM_EXTRACT` y `CLEAN_DATA`, `clean.csv` fuera de Git, validador sin cambios y excepción de ruff (PR #14); pruebas RC-3, RC-5 y descarte (PR #19); PS-1, PS-3 y PS-5; revisión de PR; cierre de `decision_log.md`, `riesgos.md` (R-08) y esta bitácora |
| Jorge Andrés Sánchez Martínez (Data Scientist) | Registro del extracto con DVC, perfil de calidad, brecha con el contrato canónico, contrato v2 (RC-3 y `discard_ok`), `crm_warnings.py`, límite de descarte, PS-2 y PS-4 |
| Gloria Abimeleth Ardila Guerrero (Data Steward) | Ficha y gobernanza (`datos_gobernanza.md` §1–§5), `src/clean.py` con los tratamientos negociados, `reports/cleaning.json`, PS-2 |
