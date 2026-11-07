# Bitácora del Reto 03 — Equipo GJJJ
## Noviembre 6 del 2026
### Jorge Eliecer Leighton
* PR #30 `(clean → validate → prepare)` creación de flujo de pipeline y retiro de la etapa sintetica
* PR #31 correción del paso `validate` en el pipeline
* Reinicio de mlflow.db. Se borró el registro local de MLflow antes del baseline, porque el @champion anterior se entrenó con datos sintéticos (Reto 00) y el gate habría comparado el baseline con un modelo de datos distintos. No afecta el pipeline ni DVC
* Ejecución el baseline con el pipeline nuevo (registro MLflow reiniciado):
roc_auc 0,8325 · recall_at_eval 0,756 · precision_at_eval 0,5268 · ahorro neto vs. aleatorio 15 030.
__brecha de recall senior_citizen 0,116 (límite V2 ≤ 0,10)__
* Aprobación de PR #33
### Juan Manuel Adarve Cifuentes
* Aprobación de PRs #30, #31 y #32
* Se prueba promover la v1 como @champion
* Agregado el codigo de reproducible en el REAME.md
### Gloria Abimeleth Ardila
* Prueba experimental de Random Forest
```terminaloutput
Running stage 'evaluate':                                                                           
> python -m src.evaluate
[evaluate] roc_auc=0.8221, pr_auc=0.627, precision=0.5592, recall=0.6764, f1=0.6122, recall_at_eval=0.7613, precision_at_eval=0.5098, recall_gap_senior_citizen=0.034, customers_contacted=456, net_savings_model=19567.5, net_savings_random=4914.91, net_savings_vs_random=14652.59
Updating lock file 'dvc.lock'                                                                       
 
Ran experiment(s): loony-nuke
Experiment results have been applied to your workspace.
```
* Prueba experimental de Gradient Boosting
```terminaloutput
> python -m src.evaluate
[evaluate] roc_auc=0.8295, pr_auc=0.636, precision=0.575, recall=0.6711, f1=0.6193, recall_at_eval=0.7401, precision_at_eval=0.5254, recall_gap_senior_citizen=0.1186, customers_contacted=440, net_savings_model=19662.5, net_savings_random=4742.45, net_savings_vs_random=14920.05
Updating lock file 'dvc.lock'                                                                       
 
Ran experiment(s): liked-dado
Experiment results have been applied to your workspace.
```
* PS-3
```shell
uv run dvc exp show --only-changed --md
```
```terminaloutput
| ├── a524f8d [liked-dado]   | 08:55 PM  | 0.8295    | 0.636    | 0.575       | 0.6711   | 0.6193 | 0.7401           | 0.5254              | 0.1186                      | 440                   | 19662               | 4742.4               | 14920                   | gradient_boosting   | 04235193d817dd036316168c1308c5ac | 9a0a193f6dc8dd45902075f06fa1bee9 |
| └── a2c83a0 [loony-nuke]   | 08:53 PM  | 0.8221    | 0.627    | 0.5592      | 0.6764   | 0.6122 | 0.7613           | 0.5098              | 0.034                       | 456                   | 19568               | 4914.9               | 14653                   | random_forest       | 9774688afce89c88654351b794326a6e | db081a60385cce4658449e31ccf7632e |
```
```shell
uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5050
```
| Corrida (run_id)                 | Modelo              | roc_auc | recall | precision | recall_gap_senior_citizen | customers_contacted | net_savings_vs_random | ¿Pasa el gate? |
|----------------------------------|---------------------|--------:|-------:|----------:|--------------------------:|--------------------:|----------------------:|----------------|
| e5c21dd8e19e44519e014f60c8a9c37f | Random Forest       |  0.8221 | 0.6764 |    0.5592 |                     0.034 |                 456 |              14652.59 | No cumple      |
| d8a14e612e0c4266b55a8fd1cb6fc6d3 | Gradient Boosting   |  0.8295 | 0.6711 |     0.575 |                    0.1186 |                 440 |              14920.05 | No cumple      |
| d517cab9a3ee4a2a83cedf963ffd00ae | Regresión Logística |  0.8325 | 0.6897 |    0.5628 |                     0.116 |                 462 |              15030.42 | Cumple         |
## Noviembre 7 del 2026
### Gloria Abimeleth Ardila
* Actualizado los datos de gobernanza en `datos_gobernanza.md`
### Jorge Eliecer Leighton
* Aprobación e integración del PR #34

