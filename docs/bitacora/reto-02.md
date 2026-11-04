# Bitácora del Reto 02 — Equipo GJJJ

## Octubre 30 del 2026
### Juan Manuel Adarve
* Se socializa propuestas para manejo de registros anomalas que afectarían las predicciones y entrenamiento del modelo.
* Entrega de propuestas aprobada para manejo de registros anomalas a `Data Stewart`

### Jorge Leithon
* Revisión y Aprobación de PR #13.** onfirmé que no tenía ningún CSV ni customer_id, y que el extracto en DVC es el original de Classroom
* Aprobación de PR #14.** Rutas CRM_EXTRACT y CLEAN_DATA en src/common.py, /clean.csv en data/processed/.gitignore, y validar_contrato.py restaurado sin cambios, como pide el reto.
* Comprobación de archivos `csv` del folder data/ esten ignorados
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

### Jorge Andrés Sanchez
* Creación de PR #16 y #17 para correción de calidad de código, además, para validar el RC-3

### Gloria Abbymeleth Ardila
* Registro de propuestas aprobadas de manejo de registros anormales en datos_gobernabza.md
* Creación de archivo de `clean.py` para tratamiento y limpieza de datos

### Jorge Leithon
* Creación de pruebas unitarias al RC-3 y RC-5

## Noviembre 1 del 2026
### Jorge Leithon
* PS-3 (PR #19, ya en main): pruebas de RC-3, RC-5 y descarte máximo en test_contract.py.
    ✅ 14 passed
    ❌ Con RC-3 comentada: 2 failed (las de RC-3). Restaurada: 14 passed.
    PS-5: a una copia del extracto con el 20 % de monthly_charges vacío le apliqué la limpieza y el contrato.

> 7042 → 5511 filas, 21,7 % descartado
* El contrato v2 pasa ✅ (por sí solo no detecta la pérdida)
discard_ok = False → 🛑 bloqueado (máximo 5 %)
El extracto real descarta 2,2 %, así que sí pasa.

## Noviembre 2 del 2026
### Jorge Andrés Sanchez
* Resultados de script de comprobación de contrato sobre el archivo crm_extracto.csv
```shell
uv run  python -m scripts.validar_contrato advertencias data/raw/crm_extracto.csv
```
```terminaloutput
[advertencias] data/raw/crm_extracto.csv: 742 filas * 13 columnas
    ❌ 2 reglas inclumplidas
    columna                                 regla                               filas afectadas
(entre columnas / esquemas)                fecha_alta vacia                            28
(entre columnas / esquemas)                fecha_alta posterior a fecha_corte          20
```
* aprobación de PRs #21 y #22
### Gloria Abbymeleth Ardila
* PS-2
> Entrada: 7.042 registros.
> Descartados: 156 registros (2,2 %).
> Resultado: 6.886 registros conservados.
> Se generaron data/processed/clean.csv y reports/cleaning.json, con los datos limpios y el resumen de tratamientos.
* aprobación de PRs #23 y #24

### Jorge Leithon
* aprobación de PRs #25 y #26

