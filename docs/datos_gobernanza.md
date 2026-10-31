# Datos y gobernanza (Reto 02)

## 1. Dataset
### Ficha técnica del extracto CRM-RET

**Conecta Andina S.A. · Jefatura de CRM y Facturación**

**Ficha técnica del extracto CRM-RET · corte 2026-09-30**

| Atributo | Valor |
|---|---|
| Contenido | Clientes residenciales con servicio activo al inicio del periodo histórico, con su desenlace a 30 días |
| Granularidad | Una fila por cliente |
| Formato | CSV, UTF-8, separador coma, primera fila con encabezados |
| Volumen aproximado | 7 000 filas |
| Periodicidad | Corte mensual; el archivo se entrega el quinto día hábil del mes siguiente |
| Completitud | Ninguna columna admite valores vacíos |
| Dueño | Jefatura de CRM y Facturación (canal de soporte: mesa de datos CRM) |
| Uso autorizado | Exclusivamente el proyecto Sistema de Retención Temprana; prohibida la entrega a terceros. Los clientes autorizaron el tratamiento de sus datos para "gestión comercial, fidelización y análisis estadístico" (política de tratamiento de datos de Conecta Andina) |
| Seudonimización | El customer_id es un código interno; la tabla de correspondencia con el documento de identidad la custodia Facturación y no se entrega |

#### Diccionario de variables

| # | Columna | Tipo | Descripción | Dominio documentado |
|---|---|---|---|---|
| 1 | `customer_id` | texto | Código seudonimizado del cliente, formato CNNNN-NNNNNN | Único en el archivo |
| 2 | `tenure_months` | entero | Meses completos desde la activación del servicio hasta la fecha de corte | 0–72 (72 es el tope que registra el sistema) |
| 3 | `contract_type` | texto | Modalidad del contrato vigente | `month-to-month`, `one-year`, `two-year` (en minúscula, exactamente así) |
| 4 | `internet_service` | texto | Tecnología de internet contratada | `dsl`, `fiber`, `none` (`none` = solo telefonía) |
| 5 | `payment_method` | texto | Medio de pago registrado | `electronic_check`, `mailed_check`, `bank_transfer`, `credit_card` |
| 6 | `monthly_charges` | decimal | Cargo mensual facturado del plan, en miles de COP | 0–500. Tarifas vigentes: los planes de solo telefonía (`none`) cuestan hasta 60 |
| 7 | `support_tickets` | entero | Tickets de soporte abiertos por el cliente en los últimos 90 días | 0–50 |
| 8 | `senior_citizen` | entero | 1 si el titular tiene 65 años o más según la fecha de nacimiento registrada | 0, 1 |
| 9 | `churn` | entero | 1 si el cliente canceló el servicio en los 30 días siguientes a la fecha de corte | 0, 1 (históricamente entre 25 % y 30 % de los clientes) |
| 10 | `region` | texto | Departamento de la dirección de instalación | `Quindío`, `Risaralda`, `Caldas`, `Norte del Valle` |
| 11 | `fecha_alta` | fecha AAAA-MM-DD | Fecha de activación del servicio | Anterior o igual a `fecha_corte` |
| 12 | `fecha_corte` | fecha AAAA-MM-DD | Fecha de corte del extracto | `2026-09-30` en todo el archivo |
| 13 | `oferta_retencion_aceptada` | entero | Resultado de la última oferta de retención registrada en el CRM | 0, 1 |

#### Nota oficial de la ficha

Esta ficha es la documentación oficial del extracto. Se entrega junto con el archivo `crm_extracto_<equipo>.csv` y describe lo que el sistema de origen debería contener. Léala antes de abrir el CSV y consérvela tal como la recibió en `docs/datos_gobernanza.md` (sección 1). Las consultas sobre su contenido se dirigen al dueño del dato (mesa de datos CRM).

**Fuente:** Gerencia de Proyectos de Analítica de Datos · Maestría en Ingeniería · Énfasis en Analítica de Datos · Universidad del Quindío.

**Prof. Christian Andrés Candela Uribe · christiancandela@uniquindio.edu.co**

## 2. Diagnóstico de calidad

El diagnóstico inicial corresponde al extracto crudo, antes de aplicar los tratamientos de limpieza.

- **Tamaño del extracto:** 7042 filas y 13 columnas.
- **Fuente de los resultados:** perfil de calidad compartido por Jorge Andrés Sánchez.
- **Porcentajes:** calculados sobre las 7042 filas del extracto y presentados con un decimal, según el reporte recibido.

| Dimensión | Regla evaluada | Resultado | Acción pendiente |
| --- | --- | --- | --- |
| Completitud | Ninguna columna admite valores vacíos, según la ficha técnica. | `monthly_charges`: 57 filas con nulos (0,8 %). `fecha_alta`: 28 filas con nulos (0,4 %). Las otras 11 columnas presentan cero nulos. | Consultar con el dueño del dato el tratamiento autorizado para los faltantes de cada columna. |
| Validez | Los valores deben respetar los dominios y rangos establecidos en la ficha técnica. | `contract_type`: 192 filas con `Month-to-month` (2,7 %). `payment_method`: 82 filas con `tarjeta_debito` (1,2 %). `tenure_months`: 28 filas con −1 (0,4 %). `support_tickets`: 13 filas con 99 (0,2 %). | Confirmar el significado de los valores encontrados y registrar la normalización, corrección o exclusión autorizada para cada caso. |
| Unicidad | Cada cliente debe estar representado por una sola fila y `customer_id` debe ser único. | Se reportan 84 filas con `customer_id` repetido (1,2 %) y 22 copias exactas de otra fila. | Acordar el criterio para resolver las repeticiones y determinar qué registro conservar. |
| Consistencia | RC-3: cuando `internet_service` es `none`, `monthly_charges` debe ser menor o igual a 60. | Se identifican 17 filas que incumplen la regla (0,2 %). | Consultar con el dueño del dato cómo resolver estos casos y registrar el tratamiento autorizado. |
| Actualidad | Las fechas deben ser interpretables; `fecha_alta` debe ser menor o igual a `fecha_corte`, y `fecha_corte` debe corresponder a 2026-09-30. | `fecha_alta` reportada como inválida o no interpretable: 28 filas (0,4 %). `fecha_corte` inválida: 0 filas (0,0 %). `fecha_alta` posterior a `fecha_corte`: 20 filas (0,3 %). `fecha_corte` diferente de 2026-09-30: 0 filas (0,0 %). | Gestionar la corrección con el dueño del dato y registrar las inconsistencias como advertencias. Proponer conservar las filas cuyos campos canónicos sean válidos, considerando que `tenure_months` es confiable. Mantener las fechas fuera de la salida del modelo, según el esquema canónico. Tratamiento pendiente de acuerdo con el dueño. |

**Interpretación de los conteos:** una misma fila puede presentar varios defectos y aparecer en distintos indicadores. Por ello, los conteos y porcentajes no deben sumarse para obtener el total de filas afectadas. Los indicadores de identificadores repetidos y copias exactas también deben conservarse por separado.

**Interpretación de la coherencia temporal**

- No se detectaron fechas de corte inválidas ni diferentes de 2026-09-30. Un corte distinto al esperado podría indicar que el registro pertenece a otro extracto o que su fecha fue registrada incorrectamente.
- Se identificaron 20 filas con `fecha_alta` posterior a `fecha_corte`. Esto constituye una inconsistencia temporal: el cliente aparece dado de alta después de la fecha de referencia del extracto.
- Se reportaron 28 valores de `fecha_alta` sin una fecha interpretable (`NaT`). Es necesario distinguir si corresponden a valores vacíos o a errores de formato o captura.
- Los 28 casos de `fecha_alta` no interpretable podrían coincidir con los 28 faltantes ya registrados en completitud. Se debe verificar esa coincidencia antes de contabilizarlos como defectos adicionales.

**Estado de los tratamientos:** pendiente de confirmar los acuerdos con el dueño del dato y registrar sus respuestas. Los resultados anteriores describen los problemas detectados en el extracto crudo; la cantidad de filas descartadas se determinará después de aplicar los tratamientos acordados.

## 3. Hallazgos del EDA

### 3.1. Hallazgos iniciales del extracto

El extracto contiene 7042 filas y 13 columnas. El esquema canónico utilizado por el modelo contempla nueve columnas: el identificador del cliente, siete variables predictoras y la variable objetivo.

Las cuatro columnas adicionales son `region`, `fecha_alta`, `fecha_corte` y `oferta_retencion_aceptada`. Sus motivos de exclusión de la salida limpia se documentan en `COLUMNAS_EXCLUIDAS`, dentro de `src/clean.py`.

El perfil inicial identifica faltantes, valores fuera de los dominios o rangos, identificadores repetidos e incumplimientos de RC-3. Los conteos detallados se presentan en la sección 2. Estos hallazgos requieren definir los tratamientos con el dueño del dato antes de implementar la limpieza final.

### 3.2. Disponibilidad temporal y posible fuga de información

Es necesario verificar qué información estaría disponible al momento de realizar la predicción del lote del lunes a las 06:00.

La columna `oferta_retencion_aceptada` requiere especial revisión: se debe establecer cuándo se registra su valor y si corresponde a información disponible antes de la predicción.

Su exclusión del esquema canónico está documentada. La conclusión sobre una posible fuga de información permanece pendiente del análisis de Jorge Andrés y de la aclaración temporal del dueño del dato.

Para completar este análisis se requieren:

- Cantidad de registros y tasa de `churn` para cada valor de `oferta_retencion_aceptada`.
- Comparación de las tasas entre los grupos.
- Secuencia temporal del corte del extracto, la predicción, la campaña, el registro de la oferta y el desenlace a 30 días.
- Conclusión sustentada sobre la disponibilidad de esta información al momento de predecir.

**Estado:** sección preliminar, pendiente de incorporar la cuantificación y la conclusión del análisis de fuga.

## 4. Contrato de datos
Implementado en `contracts/churn_contract.py` y verificado en la etapa `validate` de `dvc.yaml`.

### 4.1 Negociación de tratamientos

Las siguientes respuestas corresponden a las indicaciones del dueño del dato, presentadas con redacción normalizada.

Los conteos corresponden al diagnóstico del extracto crudo de 7042 filas. Los descartes efectivos se determinarán al ejecutar la limpieza.

| Defecto | Filas afectadas | Respuesta del dueño | Tratamiento de limpieza | Severidad en v2 |
| --- | --- | --- | --- | --- |
| `monthly_charges` nulo | 57 filas (0,8 %) | El dueño autoriza excluir los registros sin cargo mensual, previa revisión de los grupos de clientes afectados. | Excluir únicamente las filas con `monthly_charges` nulo y registrar el descarte efectivo. | Bloqueante (RC-2): el conjunto limpio debe conservar esta variable sin nulos. |
| `tenure_months = -1` | 28 filas (0,4 %) | El dueño indica excluir los registros con antigüedad igual a −1, porque están fuera del rango permitido de 0 a 72 meses. | Excluir únicamente las filas con `tenure_months = -1`. | Bloqueante (RC-2): el conjunto limpio debe cumplir el rango canónico. |
| `contract_type = Month-to-month` | 192 filas (2,7 %) | El dueño indica normalizar la etiqueta observada para ajustarla al valor canónico `month-to-month`. | Recodificar exclusivamente `Month-to-month` a `month-to-month`, conservar las filas y registrar el número de recodificaciones. | Bloqueante (RC-2): después de la limpieza no deben persistir categorías fuera del dominio. |
| `payment_method = tarjeta_debito` | 82 filas (1,2 %) | El dueño autoriza recodificar `tarjeta_debito` a `credit_card`, considerando el cambio descrito en los medios de pago, y registrar una advertencia documental sobre la recodificación. | Recodificar exclusivamente `tarjeta_debito` a `credit_card`. Documentar la indicación del dueño, el criterio aplicado al extracto histórico y el número de casos recodificados. | Bloqueante (RC-2). La advertencia documental sobre la recodificación no sustituye la validación del dominio. |
| `support_tickets = 99` | 13 filas (0,2 %) | El dueño indica excluir los registros con 99 tickets, porque superan el rango permitido de 0 a 50. | Excluir únicamente las filas con `support_tickets = 99` y registrar el descarte efectivo. | Bloqueante (RC-2): el conjunto limpio debe cumplir el rango canónico. |
| `customer_id` repetido y copias exactas | 84 filas con identificador repetido (1,2 %) y 22 copias exactas reportadas | El dueño autoriza conservar una fila por grupo completamente idéntico. Para los registros discordantes del mismo cliente, indica conservar el registro con mayor `monthly_charges` y eliminar el de menor cargo. | Retirar las copias exactas. Para los identificadores que continúen repetidos, conservar el registro con mayor `monthly_charges` y descartar los restantes con menor cargo. Registrar los descartes efectivos. | Bloqueante (RC-1): cada `customer_id` debe aparecer una sola vez en el conjunto limpio. |
| `internet_service = none` y `monthly_charges > 60` | 17 filas (0,2 %) | El dueño indica excluir los registros que incumplen la regla de consistencia RC-3. | Excluir las filas que cumplan simultáneamente ambas condiciones y registrar su descarte efectivo. | Bloqueante (RC-3): esta combinación no debe persistir en el conjunto limpio. |
| `fecha_alta` posterior a `fecha_corte` | 20 filas (0,3 %) | El dueño indica conservar las filas cuando cumplan las reglas canónicas, considerando que `tenure_months` es confiable en estos casos. También indica registrar la inconsistencia y solicitar al CRM la revisión de la fecha. | Conservar el `tenure_months` confiable, registrar las inconsistencias como advertencias y mantener `fecha_alta` fuera de `clean.csv`. Esta condición temporal no descarta filas por sí misma. | Advertencia de coherencia temporal sobre una columna no canónica. |
| `fecha_alta` vacía | 28 filas (0,4 %) | El dueño indica registrar una advertencia para que se revise el dato en origen. Autoriza conservar las filas que cumplan las reglas canónicas, dado que `fecha_alta` se excluye de la entrada del modelo. | Registrar los faltantes como advertencias y mantener `fecha_alta` fuera de `clean.csv`. No descartar filas por la ausencia de esta fecha; las demás reglas continúan aplicándose. | Advertencia de completitud sobre una columna no canónica. |

### 4.2 Criterio de severidad

Las reglas canónicas RC-1 a RC-5 conservan su carácter bloqueante. Si el conjunto limpio incumple alguna de ellas, su validación debe fallar y no debe utilizarse para entrenar o predecir.

Las advertencias sobre columnas no canónicas se registran y se reportan al dueño del dato. Una advertencia documental asociada a una recodificación no reemplaza la validación bloqueante del dominio correspondiente.

### 4.3 Control de los tratamientos

Los tratamientos se aplicarán sobre los valores concretos acordados, conservando el extracto crudo para trazabilidad.

Cada fila descartada se contará una sola vez, aunque presente varios defectos. Por tanto, los conteos del diagnóstico no deben sumarse directamente para estimar el descarte total.

Los conteos finales y la proporción total de descarte se obtendrán al ejecutar `src/clean.py` y se registrarán en `reports/cleaning.json`. El equipo deberá justificar el límite máximo de descarte utilizado.

La salida `clean.csv` conservará únicamente las nueve columnas canónicas. Excluir una columna no equivale a descartar filas.

El criterio de mayor `monthly_charges` permite elegir entre registros con cargos diferentes. Si se detectan registros discordantes del mismo cliente con cargos exactamente iguales, se reportará el caso al dueño para definir un criterio adicional. Mientras persistan identificadores repetidos, RC-1 impedirá aprobar el conjunto limpio.

### 4.4 Seguimiento de las advertencias de fechas

Se registrarán y comunicarán al dueño del dato:

- Los 20 casos con `fecha_alta` posterior a `fecha_corte`.
- Los 28 casos con `fecha_alta` vacía.

Estas condiciones no producirán descarte de filas por sí mismas. Los registros se conservarán cuando sus campos canónicos cumplan las demás reglas.

La columna `fecha_alta` se excluirá de `clean.csv`, conforme al esquema canónico. Las inconsistencias permanecerán documentadas para que el dueño revise y corrija el proceso de origen.

### 4.5 Estado de implementación

Los tratamientos están documentados. Su implementación, ejecución y verificación permanecen pendientes.

El documento se actualizará con los resultados reales de la limpieza y la validación del contrato v2.

## 5. Plan de gobernanza

Estado: borrador del Reto 02. Se documentan los responsables asignados,
la minimización prevista y una clasificación preliminar de los datos.
La política de acceso al remoto y el alcance de la autorización
requieren confirmación antes del cierre del reto.

| Elemento | Decisión |
|---|---|
| Propietario y custodio del dato | Dueño del dato: Jefatura de CRM y Facturación de Conecta Andina; el docente representa este rol en el ejercicio. Custodia técnica asignada en el proyecto: Jorge Eliecer Leighton Romero, MLOps. Gloria Ardila realiza el seguimiento documental como Data Steward. |
| Política de acceso al remoto | Propuesta pendiente de acuerdo: lectura para los cuatro roles autorizados del equipo GJJJ y escritura al remoto para MLOps. Se propone un remoto DVC privado con acceso autenticado. Su ubicación y los permisos concretos deben definirse con MLOps; se implementarán en el Reto 03. El extracto y el archivo limpio no se publican en Git. |
| Datos personales, sensibles y campo protegido | El extracto se trata como información personal seudonimizada: customer_id puede vincularse con la identidad mediante la correspondencia que conserva Facturación. La clasificación preliminar por columna aparece en el apartado 5.1. senior_citizen es el atributo protegido para evaluar equidad en el SRT. |
| Finalidad autorizada | Posición preliminar: depende del alcance de la autorización. La fidelización y el análisis estadístico descritos en la ficha son coherentes con el propósito del SRT. Debe consultarse al responsable de protección de datos, a través del dueño del dato, si la autorización cubre el entrenamiento del modelo y la priorización de llamadas, y qué información adicional debe darse a los titulares. |
| Minimización | La limpieza prevé conservar las nueve columnas canónicas. Se excluyen region, fecha_alta, fecha_corte y oferta_retencion_aceptada, con los motivos del apartado 5.2, que coinciden con COLUMNAS_EXCLUIDAS en src/clean.py. Queda pendiente verificar la salida de la ejecución y su reporte. |
| Versionamiento (DVC y remoto) | pendiente (versión lite) |
| Linaje (crudo → validado → train/test → modelo) | pendiente (versión lite) |
| Retención | pendiente (versión lite) |
| Seudonimización | pendiente (versión lite) |

### 5.1. Clasificación preliminar de las columnas

La clasificación considera los campos dentro de un registro asociado
a un cliente. Debe revisarse con el responsable de protección de datos
si el tratamiento produce nuevas inferencias o riesgos de discriminación.

| Columna | Dato personal | Dato sensible identificado por su contenido* | Atributo protegido del SRT | Razón |
|---|---|---|---|---|
| customer_id | Sí | No identificado | No | Identificador seudonimizado con correspondencia custodiada por Facturación. |
| tenure_months | Sí | No identificado | No | Antigüedad del servicio de un cliente. |
| contract_type | Sí | No identificado | No | Característica de su relación contractual. |
| internet_service | Sí | No identificado | No | Servicio contratado por el cliente. |
| payment_method | Sí | No identificado | No | Información de su medio de pago. |
| monthly_charges | Sí | No identificado | No | Información del cargo individual facturado. |
| support_tickets | Sí | No identificado | No | Historial de solicitudes de soporte. |
| senior_citizen | Sí | No identificado | Sí | Informa si el titular tiene 65 años o más; se utiliza para evaluar equidad. |
| churn | Sí | No identificado | No | Resultado de la cancelación del servicio de un cliente. |
| region | Sí | No identificado | No | Localización asociada a la instalación del cliente. |
| fecha_alta | Sí | No identificado | No | Fecha de inicio de su relación de servicio. |
| fecha_corte | No por sí sola | No identificado | No | Metadato común que señala la fecha de referencia del extracto. |
| oferta_retencion_aceptada | Sí | No identificado | No | Resultado de una oferta comercial asociada al cliente. |

*“No identificado” es una valoración preliminar a partir del diccionario
de variables, no una conclusión jurídica definitiva. Ser un atributo
protegido para evaluar equidad y ser un dato sensible son clasificaciones
distintas. El conjunto completo mantiene tratamiento restringido.

### 5.2. Columnas excluidas del archivo limpio

| Columna | Motivo registrado en COLUMNAS_EXCLUIDAS |
|---|---|
| region | No pertenece al esquema canónico del modelo definido en el contrato. |
| fecha_alta | No pertenece al esquema canónico; se utiliza para revisar la coherencia temporal del extracto. |
| fecha_corte | No pertenece al esquema canónico; proporciona la referencia temporal del extracto. |
| oferta_retencion_aceptada | No pertenece al esquema canónico; se analiza su disponibilidad temporal por posible fuga de información. |

La exclusión se refiere al archivo limpio destinado al modelo.
El extracto original conserva estas columnas para las revisiones
de calidad, trazabilidad y fuga de información.

### 5.3. Confirmaciones pendientes

- Con MLOps y el equipo: ubicación del remoto de datos y permisos
  concretos de lectura y escritura.
- Con el dueño del dato y el responsable de protección de datos:
  alcance de la autorización para entrenar el SRT y priorizar llamadas.
- Con las evidencias de ejecución: correspondencia entre la
  minimización documentada, clean.csv y reports/cleaning.json.

Referencia normativa:
[Ley 1581 de 2012, artículos 3, 4 y 5](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981).
