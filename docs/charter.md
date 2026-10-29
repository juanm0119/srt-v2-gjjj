# Project Charter — Sistema de Retención Temprana (SRT)

> Se inicia en el **Reto 00** (secciones 1–5) y se completa en el **Reto 01** (secciones 6–8).
> Nombres, roles y decisiones según el *contrato del sistema* del curso (§6.1, §9, §11).

## 1. Identificación

- Proyecto: Sistema de Retención Temprana (SRT).
- Organización: Conecta Andina S.A.
- Variante asignada: V2.
- Segmento: Hogar Pereira y Dosquebradas.
- Equipo: GJJJ, conformado por cuatro integrantes.
- Repositorio: https://github.com/juanm0119/srt-v2-gjjj
- Fuente de los supuestos: Contrato del sistema del curso, §11.

### Supuestos de la variante V2

Los valores monetarios se expresan en miles de pesos colombianos.

| Supuesto | Valor V2 | Unidad o interpretación | Dónde se configura o registra |
|---|---|---|---|
| Valor estimado de conservar un cliente | 450 | Miles de COP por cliente retenido | `params.yaml`: `business.customer_value` |
| Costo de contacto | 20 | Miles de COP por cliente contactado | `params.yaml`: `business.contact_cost` |
| Éxito supuesto de la intervención de retención | 0.25 | Probabilidad: 25 % | `params.yaml`: `business.retention_success_rate` |
| Capacidad semanal del call center | 900 | Llamadas por semana | `params.yaml`: `business.weekly_capacity` |
| Brecha máxima inicial de recall entre grupos de `senior_citizen` | 0.10 | Diferencia absoluta máxima de 10 puntos porcentuales | `params.yaml`: `fairness.max_recall_gap_senior_citizen` |
| Semilla del extracto | 2027 | Número utilizado para reproducir el extracto asignado | Registrada en este charter como referencia para el extracto del Reto 02 |

Estos valores corresponden a las condiciones oficiales de V2. Su configuración en `params.yaml` se verificará durante el Reto 00.

### Integrantes y roles

| Integrante | Rol principal | Rol secundario |
|---|---|---|
| Juan Manuel Adarve Cifuentes | Líder de proyecto / Product Owner | MLOps Engineer |
| Jorge Eliecer Leighton Romero | MLOps Engineer | Data Steward |
| Jorge Andrés Sánchez Martínez | Data Scientist | Líder de proyecto / Product Owner |
| Gloria Abimeleth Ardila Guerrero | Data Steward | Data Scientist |

Las funciones de Data Scientist y Data Steward se distribuyen entre dos integrantes. Los roles secundarios se acordaron en el Reto 01; la RACI y las reglas de suplencia están en la §6.


## 2. Problema de negocio y línea base

### Problema y decisión de negocio

Conecta Andina necesita priorizar sus acciones de retención para el segmento Hogar Pereira y Dosquebradas. El call center tiene una capacidad máxima de 900 llamadas semanales.

La decisión que apoya el SRT es a qué clientes llamar cada semana y con qué argumento, utilizando su probabilidad de abandonar el servicio en los próximos 30 días.

La Gerencia Comercial, representada por el sponsor del curso, define el criterio de decisión. Los agentes del call center utilizan la lista priorizada y las explicaciones para realizar los contactos. La selección deberá considerar rentabilidad, capacidad y política de equidad.

### Situación actual

Según el caso del curso, la empresa utiliza tres reglas informales para priorizar contactos:

1. Clientes que se han quejado.
2. Clientes con contrato mes a mes.
3. Clientes que pagan más.

Estas reglas pueden concentrar llamadas en clientes que permanecerían y dejar por fuera a quienes abandonan el servicio sin presentar señales evidentes.

El SRT propone una priorización basada en el riesgo estimado y en las restricciones del negocio.

### Línea base de comparación

Para el Reto 00 se propone reportar al sponsor el beneficio neto estimado del modelo frente a contactar al azar al mismo número de clientes.

Esta comparación es calculable y reproducible con el pipeline disponible. Su limitación es que mide el desempeño frente a una selección aleatoria; la comparación con las tres reglas del proceso actual requerirá definirlas con criterios medibles y disponer de datos sobre sus resultados.

Con los supuestos de V2 y el umbral provisional de 0.35, se seleccionan 457 clientes del conjunto de prueba.

| Indicador | Resultado en miles de COP |
|---|---:|
| Beneficio neto estimado con el modelo | 21347.50 |
| Beneficio neto estimado con selección aleatoria | 4961.71 |
| Beneficio adicional estimado frente al azar | 16385.79 |

Fuente: `metrics.json`, actualizado mediante la verificación PS-3 registrada en `docs/bitacora/reto-00.md`.

Estos resultados corresponden a datos sintéticos de la plantilla y constituyen una línea base provisional. La actualización con el extracto CRM de la variante comenzará en el Reto 02.

### Costo estimado de no actuar

El lote de referencia contiene 1400 clientes y 384 deserciones simuladas, equivalentes aproximadamente al 27.43 %.

Para ilustrar el valor económico en riesgo, se supone que esas 384 deserciones ocurren sin una intervención de retención y que cada cliente representa el valor homogéneo de V2:

```text
Valor en riesgo = clientes que desertan × customer_value
Valor en riesgo = 384 × 450
Valor en riesgo = 172800 miles de COP = $172.800.000 COP
```

Esta cifra representa valor potencial en riesgo asociado a las deserciones simuladas del lote. El beneficio estimado de una campaña incorpora adicionalmente la probabilidad de éxito de retención del 25 % y el costo de cada contacto.

### Punto de equilibrio del contacto

Con los supuestos de V2, el valor esperado de contactar a un cliente con probabilidad de abandono `p` es:

```text
Valor esperado del contacto = p × retention_success_rate × customer_value − contact_cost
Valor esperado del contacto = p × 0.25 × 450 − 20

p* = contact_cost / (retention_success_rate × customer_value)
p* = 20 / (0.25 × 450)
p* = 0.177777... ≈ 17.78 %
```

En el punto de equilibrio, el valor esperado es cero. Por encima de ese riesgo, el contacto tiene un beneficio esperado positivo bajo los supuestos del caso.

### Comparación entre rentabilidad y capacidad

Se consultaron las probabilidades del modelo guardado en `models/model.joblib` sobre `data/processed/test.csv`, utilizando las mismas variables de entrada que `src/evaluate.py`.

Resultado de la consulta:

```text
Clientes del lote de referencia: 1400
Clientes con churn=1: 384
Punto de equilibrio (%): 17.7778
Clientes con riesgo superior al punto de equilibrio: 738
Capacidad semanal: 900
```

Entre los criterios económico y de capacidad, el económico limita la selección en este lote: los 738 clientes con beneficio esperado positivo caben dentro de las 900 llamadas disponibles. Queda un margen de 162 llamadas.

El análisis económico de los 738 clientes sirve como argumento para discutir el umbral. La configuración provisional continúa en `model.decision_threshold: 0.35`, que selecciona 457 clientes.

El umbral definitivo será aprobado por el sponsor en el Reto 06 con evidencia de rentabilidad, capacidad y equidad. La brecha de recall actual de 0.1444 supera el límite inicial de V2 de 0.10 y queda registrada para ese análisis.


## 3. ML Canvas (razonamiento de cada bloque)

La tabla describe el diseño objetivo del SRT. Los retos posteriores construirán y verificarán sus componentes. Las referencias de las justificaciones corresponden al Contrato del sistema del curso.

| Bloque | Canónico: resumen | Por qué está así | Qué se rompería si fuera distinto | Adaptación a la variante V2 |
|---|---|---|---|---|
| Propuesta de valor | Entregar al call center una lista priorizada y explicada para orientar las llamadas de retención. | §1: la decisión de negocio es a quién llamar cada semana y con qué argumento. La capacidad limitada obliga a priorizar los contactos. | Un reporte de probabilidades sin una lista utilizable dejaría a los agentes resolviendo la selección con las reglas informales actuales. | La priorización corresponde a Hogar Pereira y Dosquebradas, con capacidad máxima de 900 llamadas semanales (§11). |
| Tarea de predicción | Estimar la probabilidad de que un cliente activo cancele el servicio en los próximos 30 días. | §2.1 y §3: `churn` es una etiqueta binaria que se conoce al cerrar la ventana de 30 días. La predicción debe anticiparse a la cancelación para permitir intervenir. | Entrenar para otro horizonte temporal produciría probabilidades que no corresponden al resultado observado a los 30 días y dificultaría evaluar la campaña. | Se conserva el horizonte de 30 días porque la definición de `churn` es común a las variantes. Los supuestos económicos de V2 afectan la decisión posterior. |
| Decisiones | Contactar en orden descendente de riesgo a los clientes cuya probabilidad sea mayor o igual al umbral, sin superar la capacidad semanal del call center. | §3 y §5: la selección combina umbral y capacidad. §9.2: el sponsor aprueba el umbral de decisión; el comité define la brecha de equidad aceptable. | Sin límite, la lista del Reto 04 podría superar las llamadas disponibles. Cambiar el umbral sin aprobación modificaría la política de contacto sin la decisión del responsable de negocio. | Máximo de 900 llamadas semanales. El umbral provisional de 0.35 selecciona 457 clientes del conjunto de prueba; su aprobación definitiva corresponde al Reto 06. |
| Haciendo predicciones | Procesar el lote del lunes a las 06:00, entregar la lista a las 07:00 y permitir consultas mediante `/predict`, con latencia p95 menor de 300 ms. | §5: la lista debe estar disponible antes de iniciar la campaña y el servicio en línea debe atender las consultas de los agentes. | Una lista tardía retrasaría la campaña; una consulta lenta dificultaría usar la predicción durante la llamada, aunque el modelo tuviera buenas métricas. | Se mantienen los horarios comunes del contrato y se limita la lista de V2 a 900 contactos semanales. |
| Recolección de datos | Registrar los resultados de contacto en CRM y observar la etiqueta de deserción a los 30 días. | §3 y §5: el resultado todavía no existe el día del contacto. Además, la intervención puede cambiar si el cliente permanece o cancela. | Evaluar el desempeño el mismo lunes exigiría etiquetas aún desconocidas. Reentrenar sin identificar a los contactados mezclaría riesgo de abandono y efecto de la campaña. | Registrar los contactos y sus resultados para contrastar posteriormente el éxito supuesto de retención del 25 %. El análisis del sesgo se documentará en el Reto 06. |
| Fuentes de datos | Usar CRM, facturación y soporte, bajo la responsabilidad de la Jefatura de CRM y Facturación. | §1 y §2: se necesita un dueño que responda por el origen, significado y calidad de los datos. `customer_id` es un seudónimo y `senior_citizen` es un atributo protegido. | Sin origen y responsable definidos, en el Reto 02 sería difícil resolver inconsistencias o acordar tratamientos de calidad y uso de datos. | Actualmente se utiliza la plantilla sintética. En el Reto 02 se trabajará con el extracto asignado a V2 y su semilla 2027, manteniendo las reglas canónicas. |
| Simulación de impacto | Estimar el beneficio neto de retener desertores contactados y compararlo con contactar al azar al mismo número de clientes. | §7.3 y §11: una buena clasificación debe traducirse en valor económico considerando el valor del cliente, el éxito de retención y el costo del contacto. | Contar solo aciertos ignoraría el costo de llamar. Comparar campañas con diferente número de contactos confundiría el valor del modelo con el tamaño de la campaña. | Se utilizan 450 miles de COP por cliente retenido, 20 miles de COP por contacto y éxito supuesto de 0.25. El beneficio adicional provisional frente al azar es 16385.79 miles de COP. |
| Construyendo modelos | Reentrenar mensualmente o ante una alerta; registrar la nueva versión como `@challenger`, evaluarla antes de promoverla a `@champion` y conservar `@previous`. | §4 y §5: entrenar una versión nueva no garantiza que sea mejor. El gate verifica su calidad y la versión anterior permite recuperar el servicio ante problemas. | Reemplazar directamente el modelo activo podría introducir una versión peor en el Reto 03 y dejar al equipo sin una referencia clara para el rollback del Reto 05. | Se conserva el control de versiones y promoción. La evaluación del impacto económico de cada versión utilizará los supuestos de V2. |
| Features | Usar las siete entradas canónicas: `tenure_months`, `contract_type`, `internet_service`, `payment_method`, `monthly_charges`, `support_tickets` y `senior_citizen`. | §2.1 y §2.2: el contrato fija las entradas para mantener coherencia entre entrenamiento y predicción. `customer_id` identifica al cliente; `churn` es el resultado que se quiere anticipar. | Incluir `churn` u otra información del desenlace permitiría al modelo conocer la respuesta durante el entrenamiento. Cambiar las entradas también rompería la compatibilidad con la API. | Se mantiene el mismo conjunto de entradas. En el Reto 02 se excluirán las columnas no canónicas del extracto, como `region` y `oferta_retencion_aceptada`. |
| Monitoreo | Revisar contrato y cambios en los datos por lote; latencia y errores del servicio; desempeño con etiquetas a los 30 días; resultados de campaña y equidad. | §5 y §8: los problemas de datos y servicio pueden observarse inmediatamente; el desempeño predictivo requiere etiquetas. §7.3 exige distinguir métricas técnicas, económicas y de equidad. | Esperar las etiquetas para revisar todo dejaría un mes sin detectar fallas de datos o servicio. Revisar solo ROC-AUC dejaría sin seguimiento los costos y las diferencias entre grupos. | La capacidad de referencia es 900 y el límite inicial de brecha de recall es 0.10. La brecha provisional observada de 0.1444 supera ese límite y requiere análisis en el Reto 06. |

### Bloque peor justificado: Simulación de impacto

**Debilidad identificada**

La simulación aplica un mismo valor de cliente y una probabilidad de éxito de retención del 25 % a todo el segmento Hogar Pereira y Dosquebradas. Estos son los supuestos oficiales de V2, pero todavía no contamos con resultados de campañas que permitan comprobar ese éxito de retención.

La probabilidad de abandono que calcula el modelo y la probabilidad de que una llamada logre retener a un cliente representan fenómenos diferentes. Por eso, un buen ROC-AUC por sí solo no demuestra que se obtendrá el beneficio económico estimado.

El punto de equilibrio del 17.78 % y los 738 clientes con beneficio esperado positivo dependen de esos supuestos. Además, los resultados actuales proceden de datos sintéticos.

**Alternativa propuesta para revisión del equipo**

Conservar la estimación oficial con los parámetros de V2 y acompañarla con un análisis de sensibilidad: mostrar cómo cambia el beneficio esperado si la intervención logra retener una proporción menor o mayor de clientes.

Los escenarios se identificarán como hipótesis de análisis. La comparación oficial seguirá utilizando los valores de V2.

Posteriormente, se propone contrastar el supuesto con resultados de campañas y una comparación que permita distinguir el efecto de la llamada del comportamiento de clientes que habrían permanecido de todas formas. El diseño de esa validación se acordaría con el sponsor y el dueño del dato.

**Consecuencias para el proyecto**

- Reto 01: registrar en `docs/riesgos.md` el riesgo de sobreestimar el beneficio por utilizar una eficacia de retención todavía no comprobada.
- Reto 06: documentar en `docs/model_card.md` las limitaciones de la simulación y presentar al sponsor el análisis de sensibilidad como apoyo a la decisión del umbral.
- Registro de decisiones: documentar en `docs/decision_log.md` la alternativa que finalmente acuerde el equipo.
- Comunicación de resultados: presentar `net_savings_vs_random` como beneficio estimado bajo supuestos, junto con su fuente y limitaciones.

## 4. KPIs

Los indicadores permiten evaluar la calidad del modelo, el valor económico estimado, la operación y el cumplimiento de las entregas.

Las líneas base calculadas con datos sintéticos son provisionales y se actualizarán con el extracto CRM en los Retos 02–03. Las metas siguientes son la propuesta inicial del charter para revisión del equipo.

| Tipo | KPI | Línea base | Meta | Cómo se mide |
|---|---|---|---|---|
| Técnico | Capacidad de discriminación: `roc_auc` | 0.8404. Fuente: `metrics.json`, commit `14bf349`, modelo de referencia sobre datos sintéticos con configuración V2. | ≥ 0.75, mínimo configurado actualmente en `params.yaml`: `gate.min_roc_auc`. | Consultar `roc_auc` en `metrics.json` después de cada evaluación del pipeline. Comparar versiones sobre el mismo conjunto de prueba. |
| Técnico: equidad | Brecha de recall entre grupos de `senior_citizen` | 0.1444, equivalente a 14.44 puntos porcentuales, con umbral de decisión 0.35. Fuente: `metrics.json`, commit `14bf349`. | ≤ 0.10, límite inicial de V2 según el contrato §11, sujeto a ratificación del comité en el Reto 06. | Consultar `recall_gap_senior_citizen` después de cada evaluación y analizar la brecha al estudiar los umbrales de decisión en el Reto 06. |
| Negocio estimado | Beneficio neto adicional frente a contactar al azar: `net_savings_vs_random` | 16385.79 miles de COP por lote de referencia. Fuente: `metrics.json`, commit `14bf349`, con los supuestos de V2 y umbral 0.35. | > 0 miles de COP por lote, respetando la capacidad y la política de equidad aplicable. | Comparar `net_savings_model` y `net_savings_random` para el mismo número de contactos. Consultar su diferencia en `metrics.json` y actualizar el análisis en `reports/business/` en el Reto 06. |
| Operación | Latencia p95 del servicio `/predict` | Referencia de diseño: 300 ms, según el Reto 00 §2.2. La línea base medida en el entorno del equipo está pendiente del Reto 05. | p95 < 300 ms. | Realizar pruebas de carga en el Reto 05 y monitorear el servicio. Registrar p95, número de solicitudes y condiciones de la prueba para comparar resultados. |
| Operación | Tiempo de rollback: desde la decisión de revertir hasta que `/health` informa la versión de `@previous` | Sin procedimiento. Aún no existe un procedimiento de rollback; se construye en los Retos 03 y 05 (HU-11). | < 30 min (HU-11). | Cronometrar el ensayo de rollback del Reto 05: registrar la hora de la decisión del Líder / PO y la hora en que `/health` muestra la versión de `@previous`, y anotar el tiempo en `docs/decision_log.md`. |
| Gestión | Número de hitos de entrega publicados dentro del plazo | 0 de 9 hitos publicados. Fuente: consulta `git ls-remote --tags --refs origin` sin resultados, realizada el 2026-10-21. | 9 de 9 entregas dentro de sus plazos: `r00` a `r07` y `final`. | Verificar los tags en el repositorio remoto, registrar la fecha y evidencia de publicación en la bitácora de cada entrega y contrastarlas con el calendario del contrato §6.2. |

### Interpretación y seguimiento

- La línea base técnica de 0.8404 describe el resultado actual. La meta de 0.75 representa el mínimo de calidad configurado; mantener o mejorar la referencia actual será deseable.
- La brecha de equidad actual de 0.1444 supera la meta inicial de 0.10. Se mantiene como un hallazgo pendiente de análisis y decisión en el Reto 06.
- El beneficio económico es una estimación con datos sintéticos y supuestos de retención. Los resultados de campañas permitirán contrastar esos supuestos posteriormente.
- Los 300 ms son una referencia de diseño, no una medición realizada por el equipo. La primera medición de latencia se registrará en el Reto 05.
- El valor inicial de gestión corresponde a entregas etiquetadas. El avance mediante commits y documentos continúa antes de publicar cada tag.
- Las fechas concretas de entrega se tomarán del calendario oficial del curso, aplicando los plazos del contrato §6.2.

## 5. Alcance y nivel de madurez MLOps objetivo

Esta sección propone el alcance y la forma de operación que el equipo desarrollará durante el proyecto. El nivel descrito es un objetivo de trabajo, cuyo cumplimiento deberá demostrarse con evidencias.

### 5.1 Alcance

**Incluido**

- Retos 00–01: formulación del problema, KPIs, organización del equipo y planificación.
- Reto 02: gobierno de datos, validaciones y tratamiento del extracto CRM.
- Reto 03: pipeline reproducible, versionado de datos y modelos, registro de experimentos y promoción controlada.
- Reto 04: pruebas automatizadas, integración continua y generación de la lista semanal.
- Reto 05: servicio de predicción, monitoreo, alertas y procedimientos de operación en el runbook.
- Reto 06: análisis económico y de equidad, discusión del umbral y documentación del modelo.
- Reto 07: asistente de explicación para el agente, con evaluación y controles sobre la información utilizada.
- Proyecto Final: integración del sistema, demostración de operación y respuesta a incidentes con evidencias.

La lista de V2 respetará el máximo de 900 llamadas semanales y el umbral aprobado por el sponsor.

**Extensiones opcionales fuera del compromiso base**

Entrenamiento continuo disparado automáticamente, despliegues shadow y canary, y entrega continua automática. Su incorporación requeriría una decisión explícita de alcance y capacidad del equipo.

### 5.2 Nivel de madurez objetivo

**Escala de Google: nivel 0 con prácticas avanzadas**

Se adopta la denominación “nivel 0 avanzado” utilizada en el ejemplo del curso. Se desarrollarán pipelines reproducibles, pruebas, registro de experimentos, monitoreo y controles de promoción.

Una persona iniciará el reentrenamiento previsto en el calendario. El pipeline ejecutará las etapas correspondientes y registrará sus resultados. La promoción del modelo también tendrá intervención humana.

**Escala de Microsoft: aproximación a capacidades del nivel 2**

Se toma como referencia el entrenamiento repetible y trazable, el versionado de modelos y la publicación manual controlada.

La equivalencia es orientativa. El alcance propuesto cubre esas capacidades, mientras que la recepción inicial del extracto y el inicio del reentrenamiento seguirán siendo manuales. Las capacidades alcanzadas y pendientes se revisarán al cierre del proyecto.

### 5.3 Justificación con los cinco factores

| Factor | Situación de V2 | Consecuencia para el diseño |
|---|---|---|
| Número de modelos | Un modelo principal de churn activo, con versiones candidatas y anteriores. El Reto 07 incorpora un asistente de explicación como componente adicional. | Priorizar un registro claro y una promoción controlada, con una infraestructura que el equipo pueda operar. |
| Velocidad de cambio del entorno | Todavía no se ha medido la velocidad real de cambio del segmento. El contrato §5 establece reentrenamiento mensual y las etiquetas llegan a los 30 días. | Monitorear los cambios y revisar la disponibilidad de etiquetas antes de iniciar un reentrenamiento. Mantener su inicio bajo responsabilidad humana. |
| Criticidad de la decisión | La priorización afecta el gasto de campaña y qué clientes reciben una oportunidad de retención. La capacidad máxima es de 900 llamadas semanales. | Conservar responsables para el umbral, la promoción y la respuesta a incidentes. Analizar rentabilidad y equidad antes de modificar la política de contacto. |
| Regulación y uso responsable | La Ley 1581 enmarca la protección de datos personales y el CONPES 4144 orienta la política nacional de IA. El contrato protege el identificador y exige evaluar la equidad respecto de `senior_citizen`. | Aplicar los controles de datos, privacidad, trazabilidad y equidad definidos por el contrato. Registrar decisiones y responsables. |
| Frecuencia de predicción | Lote semanal: lunes a las 06:00 y lista a las 07:00. También existen consultas continuas mediante `/predict` (contrato §5). | Automatizar las tareas repetibles de predicción, validación y monitoreo, manteniendo control humano sobre los cambios del modelo y de la política. |

### 5.4 Tareas manuales y responsables propuestos

Esta distribución se formalizará en la RACI del Reto 01, respetando las autoridades del contrato §9.2.

| Tarea manual | Responsable propuesto | Justificación |
|---|---|---|
| Revisar la calidad del extracto y proponer tratamientos | Gloria, Data Steward, con apoyo de Jorge Andrés, Data Scientist. Los cambios del contrato de datos los decide su dueño. | Las inconsistencias requieren interpretar el significado del dato y acordar su tratamiento antes de automatizarlo. |
| Iniciar el reentrenamiento mensual o derivado del análisis de una alerta | Jorge Eliecer, MLOps Engineer, con la revisión de datos y etiquetas por Jorge Andrés. | Se debe comprobar que existen datos adecuados y etiquetas disponibles. Una alerta por sí sola no garantiza que reentrenar resuelva el problema. |
| Autorizar y ejecutar una promoción | Juan Manuel, Líder/PO, coordina la revisión; Jorge Eliecer ejecuta el procedimiento. | La versión debe contar con evidencia y superar el gate. Ninguna promoción puede omitir `reports/gate.json` con `"passed": true` (contrato §4). |
| Aprobar el umbral de decisión | Sponsor, representado por el docente, con evidencia preparada por Jorge Andrés. | El umbral expresa una decisión de negocio sobre rentabilidad, capacidad y equidad (contrato §9.2). |
| Ratificar la brecha de equidad aceptable | Comité presidido por el docente. | La aceptación de diferencias entre grupos requiere la autoridad definida por el contrato §9.2. |
| Decidir y ejecutar un rollback | Juan Manuel decide; Jorge Eliecer ejecuta y registra la recuperación. | La respuesta debe tener responsable, versión de destino y evidencia del incidente. |

### 5.5 Referencias

- Reto 00, §4: alcance y nivel de madurez.
- Contrato del sistema, §4, §5, §9.2, §11 y §12.
- Ejemplo de charter del curso, §5: denominación “nivel 0 avanzado”.
- [Google: MLOps y automatización de pipelines](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).
- [Microsoft: modelo de madurez MLOps](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model).
- [Ley 1581 de 2012](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981).
- [CONPES 4144](https://colaboracion.dnp.gov.co/CDT/Conpes/Econ%C3%B3micos/4144.pdf).

## 6. Roles, habilidades y RACI
(Las filas de umbral de decisión, umbrales del gate, brecha de equidad, rollback, cambio del contrato
de datos y envío de datos a un LLM externo tienen el **A** que fija el contrato §9.2.)

| Integrante | Rol principal | Rol secundario |
|---|---|---|
| Juan Manuel Adarve Cifuentes | Líder / PO | MLOps Engineer |
| Jorge Eliecer Leighton Romero | MLOps Engineer | Data Steward |
| Jorge Andrés Sánchez Martínez | Data Scientist | Líder / PO |
| Gloria Abimeleth Ardila Guerrero | Data Steward | Data Scientist |

Data Scientist y Data Steward se presentan en columnas separadas porque el equipo tiene cuatro integrantes con responsabilidades diferenciadas.

| Actividad | Sponsor | Líder / PO | Data Scientist | Data Steward | MLOps Engineer | Dueño del dato | Comité |
|---|---|---|---|---|---|---|---|
| Project Charter y ML Canvas | C | A | C | R | C | C | I |
| Backlog y priorización | C | A | R | R | R | I | I |
| Contrato de datos y sus cambios | I | C | C | R | C | A | I |
| Pipeline de datos y versionado | I | A | C | R | R | C | I |
| Experimentos y selección de modelo | I | C | A | C | R | C | I |
| Umbrales del quality gate (`gate.*`) [1] | C | A | R | C | R | C | C |
| Umbral de decisión del negocio (`model.decision_threshold`) | A | C | R | C | C | C | C |
| Brecha de equidad aceptable | C | C | R | R | C | C | A |
| Promoción a `@champion` | I | A | C | C | R | I | I |
| Despliegue y monitoreo | I | A | C | C | R | C | I |
| Rollback ante incidente | I | A | C | C | R | I | I |
| Envío de datos a un proveedor de LLM externo | A | C | C | C | R | C | C |
| Model card y comunicación de resultados | C | A | R | R | C | C | C |

**[1] Aprobación obligatoria del Comité para los umbrales del gate.** La A permanece en el Líder / PO. La C del Comité en esa fila incluye la aprobación previa exigida por el contrato; no se interpreta como una consulta opcional.

**Ejecución de experimentos.** Data Scientist conserva la A sobre el diseño del experimento y la selección técnica del modelo. MLOps asume la R de ejecutar las corridas reproducibles definidas, registrar las métricas y aportar la evidencia para su evaluación por Data Scientist.

**Identificación de los roles externos:**

- **Sponsor:** Gerencia Comercial de Conecta Andina, representada por el docente.
- **Dueño del dato:** Jefatura de CRM y Facturación; rol simulado por el docente o por el Líder del equipo en el Reto 02, según el contrato.
- **Comité:** docente que preside y resuelve, equipo revisor e invitados cuando corresponda según el contrato.

Si una persona representa más de un rol, se registra con qué autoridad actúa en cada decisión. Ejercer Data Steward no equivale a ser Dueño del dato.

## 7. Backlog estimado, Definición de Terminado y cronograma

### 7.1 Backlog estimado, capacidad y compromiso

El backlog de referencia contiene las 17 historias de usuario HU-01 a HU-17, registradas y estimadas en el tablero Trello del equipo. Se aplicaron las equivalencias S = 3 h, M = 6 h, L = 10 h y XL = 16 h. Las siete historias de operación (HU-07, HU-08, HU-09, HU-10, HU-11, HU-16 y HU-17) tienen además estimación PERT.

Tablero del backlog: [Trello — Retos - Gerencia de proyectos en analítica de datos](https://trello.com/b/szznOU9w/retos-gerencia-de-proyectos-en-analitica-de-datos)

| Id | Historia | Talla / horas | Reto | Responsable |
|---|---|---|---|---|
| HU-01 | Definir el valor del SRT | S · 3 h | 00 | Gloria Ardila (Data Steward) |
| HU-02 | Definir responsables y reglas de gobierno | M · 6 h | 01 | Gloria Ardila (Data Steward) |
| HU-03 | Detener el pipeline ante datos inválidos | L · 10 h | 02, 03 | Gloria Ardila (Data Steward) |
| HU-04 | Excluir la fuga de información antes de entrenar | M · 6 h | 02 | Gloria Ardila (Data Steward) |
| HU-05 | Reconstruir el modelo desde cualquier tag | L · 10 h | 03 | Jorge Eliecer Leighton (MLOps Engineer) |
| HU-06 | Comparar tres corridas del modelo | M · 6 h | 03 | Jorge Eliecer Leighton (MLOps Engineer) |
| HU-07 ⚙️ | Bloquear cambios que no superen pruebas y quality gate | L · 10 h (PERT Te = 10,33) | 04 | Jorge Eliecer Leighton (MLOps Engineer) |
| HU-08 ⚙️ | Generar la lista semanal de clientes en riesgo | L · 10 h (PERT Te = 10,33) | 04 | Jorge Eliecer Leighton (MLOps Engineer) |
| HU-09 ⚙️ | Consultar el riesgo de un cliente en menos de un segundo | M · 6 h (PERT Te = 6,17) | 05 | Jorge Eliecer Leighton (MLOps Engineer) |
| HU-10 ⚙️ | Generar un reporte de drift por cada lote | L · 10 h (PERT Te = 10,33) | 05 | Jorge Eliecer Leighton (MLOps Engineer) |
| HU-11 ⚙️ | Recuperar la versión anterior en menos de 30 minutos | XL · 16 h (PERT Te = 16,33) | 03, 05 | Jorge Eliecer Leighton (MLOps Engineer) |
| HU-12 | Estimar el ahorro frente a llamar al azar | L · 10 h | 06 | Jorge Andrés Sánchez (Data Scientist) |
| HU-13 | Medir la brecha de recall entre grupos | L · 10 h | 06 | Jorge Andrés Sánchez (Data Scientist) |
| HU-14 | Documentar el modelo y sus usos no previstos | M · 6 h | 06 | Jorge Andrés Sánchez (Data Scientist) |
| HU-15 | Explicar por qué un cliente está en riesgo | M · 6 h | 07 | Jorge Andrés Sánchez (Data Scientist) |
| HU-16 ⚙️ | Evaluar los cambios del prompt antes de publicarlos | L · 10 h (PERT Te = 10,33) | 07 | Jorge Andrés Sánchez (Data Scientist) |
| HU-17 ⚙️ | Comunicar los incidentes y documentar el post-mortem | L · 10 h (PERT Te = 10,33) | 05, S8 | Jorge Eliecer Leighton (MLOps Engineer) |
| Spike | ¿Ollama con qwen3:4b responde en menos de 20 s? | 3 h (tiempo máximo) | 01 (informa al 07) | Jorge Eliecer Leighton (MLOps Engineer) |
| | **Total HU-01 a HU-17** | **145 h** | | |
| | **Total con el spike** | **148 h** | | |

⚙️ Historia de operación (etiqueta OPERACIÓN en el tablero), estimada además con PERT: Te = (O + 4M + P) / 6. Los valores O, M y P de cada una están en su tarjeta.

El responsable de cada historia corresponde al R del reto donde se implementa según el cronograma (§7.4); HU-01 y HU-02 siguen la R de "Project Charter y ML Canvas" en la RACI (§6). El spike lo ejecuta el MLOps Engineer; el Data Scientist conserva la decisión sobre `llm.*` y `llm_gate.*` (contrato §7.1) con base en su resultado.

| Concepto | Cálculo | Horas |
|---|---:|---:|
| Esfuerzo estimado del backlog completo | Suma de HU-01 a HU-17 | 145,00 |
| Disponibilidad semanal declarada | 15 + 12 + 20 + 15 | 62,00 |
| Factor de enfoque | 62 × 0,60 | 37,20 h/semana |
| Periodo disponible hasta S8 | 2 semanas | — |
| Capacidad efectiva total | 37,20 × 2 | 74,40 |
| Reserva propuesta para reprocesos de datos | 74,40 × 0,10 | 7,44 |
| Capacidad comprometible | 74,40 − 7,44 | 66,96 |
| Déficit frente al backlog completo | 145,00 − 66,96 | 78,04 |

El factor de enfoque de 0,60 se eligió dentro del rango establecido para el Reto 01. La reserva propuesta del 10 % cubre reprocesos de datos, validaciones fallidas y ajustes derivados del contrato de datos; el factor de enfoque ya contempla interrupciones y coordinación general.

El backlog completo no cabe en la capacidad comprometible declarada. Las 17 historias permanecen en el tablero como backlog de referencia y no se eliminan. En la reunión del equipo se definió que no se dispone de horas adicionales para cubrir el déficit de 78,04 h, por lo que el déficit se acepta y se reporta como riesgo de gestión (R-07 en `docs/riesgos.md`). Con el spike (3 h) el backlog suma 148 h; al descontar HU-01 (3 h), entregada en el Reto 00 antes del periodo de capacidad, quedan 145 h pendientes, de modo que el déficit se mantiene en 78,04 h. Para que el déficit no recaiga al azar sobre cualquier historia, se trabajan primero las historias de prioridad Alta (*Historias y casos de uso*, §3). Las de prioridad Media (HU-06, HU-09, HU-14, HU-15 y HU-16, 34 h) se hacen en versión mínima o se aplazan si al cierre de cada reto no queda capacidad. El Líder / PO revisa el avance en la reunión semanal y registra en `docs/decision_log.md` qué se recortó en cada reto. La decisión está registrada en `docs/decision_log.md` (2026-10-29).

Según las estimaciones que asignamos a las 17 historias:

| Categoría | Historias | Total de horas |
|---|---|---:|
| Historias operativas | HU-07, HU-08, HU-09, HU-10, HU-11, HU-16, HU-17 | 72 h |
| Resto de historias | HU-01 a HU-06 y HU-12 a HU-15 | 73 h |
| Total general | 17 historias | 145 h |

### 7.2 Marco de gestión

El equipo adopta **Kanban**, combinado con **CRISP-ML(Q)**: CRISP-ML(Q) indica en qué fase del proyecto está cada historia (etiqueta de fase en el tablero) y Kanban organiza el trabajo de la semana. No se elige entre los dos: se combinan. El backlog y el estado de cada historia se visualizan en Trello.

| Aspecto | Cómo lo aplica el equipo |
|---|---|
| Iteración | Un reto: empieza con el fin de semana de clase y termina con la publicación de su tag (`r02` a `r07`), siete días después o al inicio de la S8 (contrato §6.2). |
| Eventos que se conservan | Una reunión semanal corta para priorizar, revisar la capacidad disponible, identificar bloqueos y acordar responsables; y una revisión de cierre antes de cada tag (evidencias, decisiones, riesgos y archivos requeridos). |
| Eventos que se descartan | La daily, porque cuatro integrantes a tiempo parcial, con 62 h semanales en total, no coinciden a diario; y la planeación de sprint y la retrospectiva formales de Scrum, porque las fechas de tag ya fijan el ritmo y la reunión semanal cubre la priorización y los ajustes. |
| Coordinación entre fines de semana | Cada integrante actualiza el estado de sus tarjetas en Trello y comunica los bloqueos al Líder / PO. |

**Por qué Kanban:** el equipo se ve cuatro fines de semana, trabaja a tiempo parcial, tiene fechas de tag fijas y un déficit de capacidad aceptado (§7.1). Kanban permite priorizar semana a semana dentro de cada reto sin sumar ceremonias que consuman las pocas horas disponibles.

### 7.3 Definición de Terminado

Una historia se considera terminada cuando cumple sus criterios de aceptación y los siguientes criterios generales:

| Criterio | Aplica desde | Evidencia |
|---|---|---|
| El cambio entra a `main` mediante un pull request revisado por otro integrante. | Reto 02 | Pull request aprobado y mergeado. |
| `dvc repro` reproduce el resultado y `dvc.lock` está actualizado. | Reto 03 | Salida de la ejecución y archivo `dvc.lock` versionado. |
| La integración continua está en verde. | Reto 04 | Ejecución exitosa de la CI en GitHub. |
| Si la historia implica una decisión, existe una entrada en `docs/decision_log.md`. | Reto 00 | Registro con fecha, alternativas, justificación, responsable y evidencia. |
| El registro de riesgos incorpora el aprendizaje o cambio de exposición identificado. | Reto 01 | Actualización de `docs/riesgos.md`. |

Estos criterios se aplican además de los criterios particulares de aceptación de cada historia. Ninguna historia se marca como terminada solo por tener código escrito: debe conservar evidencia reproducible, revisada y documentada.

### 7.4 Cronograma por fin de semana

| FDS | Reto o entrega | Responsable (R) | Tag | Fecha límite |
|---|---|---|---|---|
| 2 | Reto 02 - Gobierno y contrato de datos | Gloria Abimeleth Ardila Guerrero, Data Steward | `r02` | Siete días después del FDS 2 |
| 2 | Reto 03 - Reproducibilidad y versionado | Jorge Eliecer Leighton Romero, MLOps Engineer | `r03` | Siete días después del FDS 2 |
| 3 | Reto 04 - Pruebas e integración continua | Jorge Eliecer Leighton Romero, MLOps Engineer | `r04` | Siete días después del FDS 3 |
| 3 | Reto 05 - Despliegue, monitoreo y operación | Jorge Eliecer Leighton Romero, MLOps Engineer | `r05` | Siete días después del FDS 3 |
| 4 | Reto 06 - Impacto, equidad y gobernanza | Jorge Andrés Sánchez Martínez, Data Scientist | `r06` | Inicio de la S8 |
| 4 | Reto 07 - Asistente de explicación con LLM | Jorge Andrés Sánchez Martínez, Data Scientist | `r07` | Inicio de la S8 |
| 4 | Proyecto Final - Simulacro y defensa | Juan Manuel Adarve Cifuentes, Líder / PO | `final` | S8, antes de la primera defensa |

Cada responsable coordina la evidencia y el cierre del reto, pero el trabajo se distribuye entre los cuatro integrantes según la RACI, los roles secundarios y la capacidad disponible.
### 7.5 Historia peor estimada

**HU-11 — Recuperar la versión anterior en menos de 30 minutos** (XL · 16 h; PERT O = 10, M = 16, P = 24, Te = 16,33) es la historia que más probablemente se desborde:

- Tiene la mayor incertidumbre del backlog: su rango PERT (P − O = 14 h) es el más amplio, y es la única historia XL.
- Es una historia de operación ⚙️; *Historias y casos de uso* §3 advierte que estas son las que más se subestiman.
- Se reparte entre dos retos (03 y 05): lo que se construye en el Reto 03 no puede probarse completo hasta que exista el despliegue del Reto 05.
- Depende de piezas que todavía no existen: el alias `@previous`, el redespliegue, `/health` y el procedimiento del runbook.

**Acción: dividirla**, siguiendo la separación que ya hace el caso de uso CU-05 (*"03 (registro) · 05 (redespliegue cronometrado)"*):

| Parte | Reto | Alcance |
|---|---|---|
| HU-11a | 03 | Promoción con `@previous` registrado, de modo que exista una versión a la cual volver. |
| HU-11b | 05 | Redespliegue cronometrado hasta que `/health` informe la versión de `@previous` en menos de 30 minutos (KPI de rollback, §4). |

Si al cierre del Reto 03 HU-11a ya consumió más de la mitad de las 16 h estimadas, se escala en la reunión semanal según el riesgo R-07. La decisión está registrada en `docs/decision_log.md` (2026-10-29).

## 8. Riesgos principales
Los cinco riesgos de mayor exposición. El registro completo y vivo está en [`riesgos.md`](riesgos.md).
