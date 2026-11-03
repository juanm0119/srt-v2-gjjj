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

### 2.1 Validación del contrato canónico sobre el extracto crudo

Jorge Andrés Sánchez compartió la siguiente salida de validación:

- Archivo evaluado: `data/raw/crm_extracto.csv`.
- Tamaño: 7042 filas y 13 columnas.
- Resultado informado: 7 reglas incumplidas.
- Indicador impreso en la salida recibida: `False`.

| Campo o esquema | Incumplimiento detectado | Cantidad afectada |
| --- | --- | --- |
| `contract_type` | Valor `Month-to-month` fuera del dominio canónico. | 192 filas |
| `customer_id` | Identificador repetido. | 84 filas |
| `payment_method` | Valor `tarjeta_debito` fuera del dominio canónico. | 82 filas |
| `monthly_charges` | Valores nulos en una columna que no admite vacíos. | 57 filas |
| `tenure_months` | Valor −1 fuera del rango de 0 a 72 meses. | 28 filas |
| `support_tickets` | Valor 99 fuera del rango de 0 a 50. | 13 filas |
| Esquema de columnas | Presencia de `region`, `fecha_alta`, `fecha_corte` y `oferta_retencion_aceptada`, que no pertenecen a las nueve columnas canónicas. | 4 columnas |

La cantidad de cuatro columnas adicionales corresponde a un incumplimiento estructural; no representa cuatro filas defectuosas.

Los conteos no se suman para obtener un total de filas afectadas, porque una misma fila puede incumplir varias reglas.

**Trazabilidad de la ejecución:** para utilizar esta salida como evidencia del contrato canónico original, debe corresponder a una ejecución anterior a la modificación de `contracts/churn_contract.py`. La etiqueta `[v2]` de la salida no demuestra, por sí sola, que las nuevas reglas ya estuvieran implementadas.

### 2.2 Brecha entre el perfil de calidad y el contrato canónico

La comparación identifica los siguientes hallazgos del perfil que no aparecen como controles específicos en la salida recibida:

| Hallazgo del perfil | Filas afectadas | Resultado de la comparación | Control previsto |
| --- | --- | --- | --- |
| `internet_service = none` y `monthly_charges > 60` | 17 filas (0,2 %) | La salida no reporta el incumplimiento de esta relación entre columnas. | Incorporar RC-3 como regla bloqueante en los esquemas correspondientes. |
| `fecha_alta` vacía | 28 filas (0,4 %) | La columna se rechaza por estar fuera del esquema canónico, pero no se informa específicamente su falta de completitud. | Registrar una advertencia sobre el extracto crudo y reportarla al dueño. |
| `fecha_alta` posterior a `fecha_corte` | 20 filas (0,3 %) | La salida no reporta la inconsistencia temporal entre ambas fechas. | Registrar una advertencia de coherencia temporal y reportarla al dueño. |

**Precisión sobre los duplicados:** las 22 copias exactas quedan cubiertas por el rechazo de identificadores repetidos. El contrato detecta el incumplimiento de unicidad, aunque no distingue las copias exactas de los registros discordantes. Esa distinción corresponde al perfil y al tratamiento de limpieza.

**Precisión sobre las fechas:** rechazar `fecha_alta` y `fecha_corte` como columnas adicionales no equivale a comprobar sus valores o su coherencia temporal.

Los 28 valores de `fecha_alta` no interpretables reportados en actualidad podrían coincidir con los 28 faltantes de completitud; no deben contabilizarse como casos adicionales sin comprobar esa coincidencia.

**Resultado actualizado del contrato v2 y de las advertencias**

La validación inicial del contrato canónico sobre el extracto crudo
reportó siete reglas incumplidas. Después de incorporar RC-3, el
contrato v2 reportó ocho reglas incumplidas, incluyendo 17 filas con
`internet_service = "none"` y `monthly_charges > 60`.

El esquema de advertencias detectó 28 filas con `fecha_alta` vacía
y 20 con `fecha_alta` posterior a `fecha_corte`. Estas situaciones
se documentan como advertencias y no generan exclusión de filas
por sí mismas.

El conjunto limpio, compuesto por 6.886 filas y nueve columnas
canónicas, fue validado por Jorge Andrés con el contrato v2,
obteniendo el resultado «sin faltas».

La detección de columnas adicionales mediante RC-5 verifica el
esquema. La explicación y cuantificación de la posible fuga de
información se documentan por separado en la sección 3.

## 3. Hallazgos del EDA

### 3.1. Hallazgos iniciales del extracto

El extracto contiene 7042 filas y 13 columnas. El esquema canónico utilizado por el modelo contempla nueve columnas: el identificador del cliente, siete variables predictoras y la variable objetivo.

Las cuatro columnas adicionales son `region`, `fecha_alta`, `fecha_corte` y `oferta_retencion_aceptada`. Sus motivos de exclusión de la salida limpia se documentan en `COLUMNAS_EXCLUIDAS`, dentro de `src/clean.py`.

El perfil inicial identifica faltantes, valores fuera de los dominios o rangos, identificadores repetidos e incumplimientos de RC-3. Los conteos detallados se presentan en la sección 2. Estos hallazgos requieren definir los tratamientos con el dueño del dato antes de implementar la limpieza final.

### 3.2 Disponibilidad temporal de las variables

Se registra la clasificación inicial compartida por Jorge Andrés. La estabilidad de una variable y su disponibilidad al momento de predecir son criterios distintos.

Una variable puede cambiar con el tiempo y ser válida como entrada si se utiliza el valor que estaba disponible antes de puntuar el lote del lunes a las 06:00.

| Columna | Clasificación inicial | Uso en el proyecto | Disponibilidad al momento de predecir |
| --- | --- | --- | --- |
| `customer_id` | Relativamente estable | Identificador; no es predictor. | Indicada como conocida por Jorge Andrés. |
| `fecha_alta` | Relativamente estable | Verificación temporal; excluida del conjunto canónico. | Indicada como conocida por Jorge Andrés; sus defectos se documentan en el diagnóstico. |
| `senior_citizen` | Relativamente estable | Variable predictora. | Indicada como conocida por Jorge Andrés. |
| `region` | Relativamente estable | Variable auxiliar; excluida del conjunto canónico. | Indicada como conocida por Jorge Andrés. |
| `tenure_months` | Relativamente estable | Variable predictora. | Indicada como conocida por Jorge Andrés; debe utilizarse la antigüedad correspondiente al momento de referencia. |
| `contract_type` | Volátil | Variable predictora. | Confirmar que el valor utilizado corresponde al estado disponible antes de puntuar el lote. |
| `internet_service` | Volátil | Variable predictora. | Confirmar que el valor utilizado corresponde al estado disponible antes de puntuar el lote. |
| `payment_method` | Volátil | Variable predictora. | Confirmar que el valor utilizado corresponde al estado disponible antes de puntuar el lote. |
| `monthly_charges` | Volátil | Variable predictora. | Confirmar que el cargo utilizado estaba disponible antes de puntuar el lote. |
| `support_tickets` | Volátil | Variable predictora. | Confirmar que el conteo utiliza únicamente solicitudes conocidas antes de puntuar el lote. |
| `oferta_retencion_aceptada` | Volátil y candidata a fuga | Excluida del conjunto canónico. | Confirmar cuándo se registra y si incorpora información posterior a la predicción. |
| `fecha_corte` | Metadato temporal | Referencia del extracto; excluida del conjunto canónico. | La fecha consta en el archivo; debe verificarse que el extracto se entregue antes de utilizarlo para puntuar. |
| `churn` | Variable objetivo | Etiqueta para entrenamiento y evaluación; no es predictor. | El desenlace futuro de un nuevo caso no se conoce al momento de predecir. |

La disponibilidad temporal no garantiza que el dato sea correcto: los problemas de calidad se verifican por separado.

### 3.3. Cuantificación y análisis temporal de la posible fuga

Jorge Andrés ejecutó PS-4 sobre el extracto crudo, compuesto por
7.042 registros. Agrupó los datos por `oferta_retencion_aceptada`
y calculó la media de `churn` y la cantidad de registros.

Como `churn` toma los valores 0 y 1, su media representa
la proporción de registros con cancelación del servicio.

| `oferta_retencion_aceptada` | Registros | Media de `churn` | Tasa de churn |
|---|---:|---:|---:|
| 0 | 5.544 | 0,339105 | 33,91 % |
| 1 | 1.498 | 0,034713 | 3,47 % |
| **Total** | **7.042** | — | — |

La diferencia entre las tasas es de aproximadamente 30,44 puntos
porcentuales. El resultado muestra una asociación fuerte entre
la variable y el desenlace, pero no demuestra por sí solo una
relación causal ni confirma su disponibilidad al predecir.

**Línea de tiempo del escenario del Reto 02**

Corte → lote del lunes → campaña → registro de la oferta →
etiqueta de churn a 30 días.

**Conclusión sobre la fuga de información**

De acuerdo con la secuencia operativa establecida en el bloque
4.2 del Reto 02, el resultado de la oferta de retención se registra
después de la predicción utilizada para generar el lote del lunes.

Por tanto, en el escenario del reto, `oferta_retencion_aceptada`
constituye fuga de información: su valor incorpora el resultado
de una actuación posterior al momento de predicción.

Utilizar esta columna como predictor permitiría al modelo
aprovechar información que todavía no estaba disponible al
priorizar los clientes y podría producir una evaluación
demasiado optimista.

Los resultados de PS-4 cuantifican la asociación con el desenlace.
La conclusión temporal se sustenta en la secuencia del reto;
las diferencias entre tasas no demuestran por sí solas causalidad.

**Tratamiento aplicado**

La columna `oferta_retencion_aceptada` se excluye del conjunto
canónico mediante `src/clean.py`. Su exclusión está registrada
en `reports/cleaning.json`.

**Verificación adicional con el dueño del dato**

Se conserva la siguiente pregunta para documentar con mayor
precisión el origen del campo:

¿En qué momento se registra el resultado de la última oferta
de retención y a qué campaña corresponde?

Esta consulta complementa la trazabilidad del dato. La conclusión
de fuga para el escenario del Reto 02 queda sustentada en la
línea de tiempo definida por el ejercicio.

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

**Decisión sobre los valores faltantes de `monthly_charges`**

Se aplicó la exclusión acordada de las filas con `monthly_charges`
vacío. No se realizó imputación. La decisión evita introducir un
cargo estimado sin una referencia sustentada para este tratamiento.
Los 57 registros afectados representan aproximadamente el 0,8 %
del extracto original.

**Resultados de ejecución de los tratamientos**

Los siguientes conteos proceden de `reports/cleaning.json`.
Las recodificaciones y las advertencias no representan filas
descartadas.

| Tipo | Tratamiento aplicado | Conteo de ejecución |
|---|---|---:|
| Recodificación | `contract_type`: `Month-to-month` → `month-to-month` | 192 |
| Recodificación | `payment_method`: `tarjeta_debito` → `credit_card` | 82 |
| Advertencia | `fecha_alta` vacía | 28 |
| Advertencia | `fecha_alta` posterior a `fecha_corte` | 20 |
| Exclusión de filas | `monthly_charges` nulo | 57 |
| Exclusión de filas | `tenure_months` igual a -1 | 28 |
| Exclusión de filas | `support_tickets` igual a 99 | 13 |
| Exclusión de filas | Incumplimiento de RC-3: sin internet y cargo mayor a 60 | 17 |
| Exclusión de filas | Copias exactas adicionales | 21 |
| Exclusión de filas | Duplicados discordantes con menor cargo mensual | 20 |
| **Total descartado** | **Filas excluidas, contadas una sola vez** | **156** |

**Balance de filas**

- Entrada: 7.042 filas.
- Descartadas: 156 filas.
- Salida: 6.886 filas.
- Proporción descartada registrada: 0,0222, equivalente al 2,22 %.

El diagnóstico inicial identificó 22 copias exactas adicionales
sobre el extracto crudo. La etapa de deduplicación eliminó 21,
después de las exclusiones anteriores. Los conteos corresponden
a etapas distintas del proceso.

Las advertencias sobre fechas no eliminan filas por sí mismas.
Los registros se conservan cuando cumplen las reglas canónicas.

Se excluyen las columnas `region`, `fecha_alta`, `fecha_corte` y
`oferta_retencion_aceptada`, con las razones documentadas en
`reports/cleaning.json`. El conjunto final contiene nueve columnas
canónicas.

### 4.2 Criterio de severidad

Las reglas canónicas RC-1 a RC-5 conservan su carácter bloqueante. Si el conjunto limpio incumple alguna de ellas, su validación debe fallar y no debe utilizarse para entrenar o predecir.

Las advertencias sobre columnas no canónicas se registran y se reportan al dueño del dato. Una advertencia documental asociada a una recodificación no reemplaza la validación bloqueante del dominio correspondiente.

### 4.3 Control de los tratamientos

La limpieza aplica primero las recodificaciones acordadas y cuenta las advertencias de fechas sobre el extracto recibido. Después aplica las exclusiones por cargo faltante, antigüedad −1, tickets 99 e incumplimiento de RC-3.

Sobre los registros restantes, retira las copias exactas y conserva el mayor `monthly_charges` por cliente. Si existen registros distintos empatados en el cargo máximo, la ejecución se detiene para resolver el caso con el dueño.

Los descartes por tratamiento corresponden a este orden de aplicación. Cada fila retirada se cuenta una sola vez; por ello, los conteos de exclusión pueden diferir de los conteos iniciales del diagnóstico.

El descarte observado en esta ejecución fue de 156 filas sobre
7.042 registros de entrada. La proporción registrada en
`reports/cleaning.json` es 0,0222, equivalente al 2,22 %.

**Presupuesto máximo de descarte**

Jorge Andrés confirmó que el valor configurado es
`MAX_DISCARD_SHARE = 0.05`, equivalente al 5 %.

Este límite establece una exigencia de conservación de al menos
el 95 % de las filas de cada lote. Se documenta como una tolerancia
operativa provisional, que deberá revisarse con nuevos extractos.

En la ejecución actual se descartaron 156 de 7.042 registros.
La proporción registrada en `reports/cleaning.json` es 0,0222,
equivalente al 2,22 %, por debajo del límite configurado.

Para un lote de 7.042 registros, el límite del 5 % permite hasta
352 descartes. Esto deja un margen de 196 filas respecto al
descarte observado, para admitir variaciones frente al extracto
analizado manteniendo un control sobre la pérdida de registros.

La regla `discard_ok` acepta el presupuesto cuando
`proporcion_descartada <= MAX_DISCARD_SHARE`.
Si la proporción supera el 5 %, debe rechazar el lote para revisar
los defectos y los tratamientos aplicados.

El umbral es una decisión operativa, no una estimación estadística
del comportamiento normal. También debe revisarse si las
exclusiones se concentran en determinados grupos de clientes.

La evidencia de ejecución de `discard_ok` y de PS-5 se incorporará
a la bitácora. Un lote cuya proporción descartada sea del 20 %
debe incumplir este control.

### 4.4 Seguimiento de las advertencias de fechas

Se registrarán y comunicarán al dueño del dato:

- Los 20 casos con `fecha_alta` posterior a `fecha_corte`.
- Los 28 casos con `fecha_alta` vacía.

Estas condiciones no producirán descarte de filas por sí mismas. Los registros se conservarán cuando sus campos canónicos cumplan las demás reglas.

La columna `fecha_alta` se excluirá de `clean.csv`, conforme al esquema canónico. Las inconsistencias permanecerán documentadas para que el dueño revise y corrija el proceso de origen.

### 4.5. Implementación, ejecución y validación de la limpieza

La limpieza fue implementada en `src/clean.py` y ejecutada mediante:

`uv run python -m src.clean`

El proceso leyó 7.042 filas del extracto crudo, descartó 156 y
conservó 6.886. La proporción descartada registrada en el informe
es 0,0222, equivalente al 2,22 %.

Se generaron los siguientes resultados:

- `data/processed/clean.csv`: conjunto limpio con 6.886 filas
  y nueve columnas canónicas.
- `reports/cleaning.json`: conteos agregados por tratamiento,
  razones de exclusión de columnas y proporción descartada,
  sin identificadores de clientes.

Jorge Andrés ejecutó la validación v2 sobre el conjunto limpio
y obtuvo el resultado «sin faltas».

Sobre el extracto crudo, el contrato v2 reportó ocho reglas
incumplidas, incluida RC-3. El esquema de advertencias detectó
28 filas con `fecha_alta` vacía y 20 con fecha de alta posterior
al corte.

Estos resultados respaldan la ejecución de la limpieza y la
validación del conjunto resultante. La comprobación del límite
máximo de descarte debe documentarse con el umbral definido
y justificado por el equipo.

La cuantificación de PS-4 fue realizada por Jorge Andrés sobre
los 7.042 registros del extracto crudo. Las tasas de churn fueron
33,91 % para `oferta_retencion_aceptada = 0` y 3,47 % para el
valor 1. Los resultados se documentan en la sección 3.3.

El límite de descarte fue confirmado por Jorge Andrés en
`MAX_DISCARD_SHARE = 0.05` (5 %). Su justificación se documenta
en la sección 4.3.

La proporción descartada del lote actual es 0,0222 y se encuentra
por debajo del límite configurado. 

La prueba PS-5 fue realizada por Jorge Eliecer Leighton, MLOps.
El lote corrupto presentó un 21,7 % de filas descartadas,
superior al límite configurado de
`MAX_DISCARD_SHARE = 0.05` (5 %).

La función `discard_ok` devolvió `False` y el lote fue bloqueado.
Este resultado evidencia que el control rechaza un lote cuya
proporción descartada supera el presupuesto definido en §4.3.

El extracto original registra una proporción descartada de
0,0222 (2,22 %), inferior al límite del 5 %.

## 5. Plan de gobernanza

Estado: documentación del Reto 02 con limpieza ejecutada y conjunto
limpio validado mediante el contrato v2. Se documentan los responsables,
la minimización aplicada y una clasificación preliminar de los datos.
La política de acceso al remoto está propuesta y pendiente de acuerdo
con MLOps y el equipo. Se mantiene documentada la consulta sobre el
alcance de la autorización para entrenar el SRT y priorizar llamadas.

| Elemento | Decisión |
|---|---|
| Propietario y custodio del dato | Dueño del dato: Jefatura de CRM y Facturación de Conecta Andina; el docente representa este rol en el ejercicio. Custodia técnica asignada en el proyecto: Jorge Eliecer Leighton Romero, MLOps. Gloria Ardila realiza el seguimiento documental como Data Steward. |
| Política de acceso al remoto | Propuesta pendiente de acuerdo: lectura para los cuatro roles autorizados del equipo GJJJ y escritura al remoto para MLOps. Se propone un remoto DVC privado con acceso autenticado. Su ubicación y los permisos concretos deben definirse con MLOps; se implementarán en el Reto 03. El extracto y el archivo limpio no se publican en Git. |
| Datos personales, sensibles y campo protegido | El extracto se trata como información personal seudonimizada: customer_id puede vincularse con la identidad mediante la correspondencia que conserva Facturación. La clasificación preliminar por columna aparece en el apartado 5.1. senior_citizen es el atributo protegido para evaluar equidad en el SRT. |
| Finalidad autorizada | Posición preliminar: depende del alcance de la autorización. La fidelización y el análisis estadístico descritos en la ficha son coherentes con el propósito del SRT. Debe consultarse al responsable de protección de datos, a través del dueño del dato, si la autorización cubre el entrenamiento del modelo y la priorización de llamadas, y qué información adicional debe darse a los titulares. |
| Minimización | La limpieza conserva las nueve columnas canónicas. Se excluyen `region`, `fecha_alta`, `fecha_corte` y `oferta_retencion_aceptada`, con los motivos del apartado 5.2, coincidentes con `COLUMNAS_EXCLUIDAS` en `src/clean.py` y con `reports/cleaning.json`. La ejecución produjo 6.886 filas y nueve columnas; Jorge Andrés verificó que el conjunto limpio pasa el contrato v2 sin faltas. |
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

| Columna | Motivo registrado en `COLUMNAS_EXCLUIDAS` |
|---|---|
| `region` | No pertenece al esquema canónico del modelo definido en el contrato. |
| `fecha_alta` | No pertenece al esquema canónico; se utiliza para revisar la coherencia temporal del extracto. |
| `fecha_corte` | No pertenece al esquema canónico; proporciona la referencia temporal del extracto. |
| `oferta_retencion_aceptada` | No pertenece al esquema canónico; se analiza su disponibilidad temporal por posible fuga de información. |

La exclusión se refiere al archivo limpio destinado al modelo.
El extracto original conserva estas columnas para las revisiones
de calidad, trazabilidad y fuga de información.

### 5.3. Verificaciones realizadas y confirmaciones pendientes

**Verificaciones realizadas**

- La limpieza procesó 7.042 filas y produjo 6.886 filas de salida.
- Se descartaron 156 filas. La proporción registrada en
  `reports/cleaning.json` es 0,0222, equivalente al 2,22 %.
- El conjunto limpio contiene nueve columnas canónicas y pasa
  el contrato v2 sin faltas, según la validación de Jorge Andrés.
- Las cuatro columnas excluidas y sus motivos coinciden entre
  este documento y el informe de limpieza.

**Confirmaciones pendientes**

- Con MLOps y el equipo: acordar la ubicación prevista del remoto
  de datos y los permisos concretos de lectura y escritura.
  Su implementación corresponde al Reto 03.
- Con el dueño del dato y el responsable de protección de datos:
  precisar el alcance de la autorización para entrenar el SRT
  y priorizar llamadas.

**Verificación adicional de trazabilidad**

Se conserva para el dueño del dato la pregunta sobre el momento
de registro y la campaña a la que corresponde la última oferta
de retención. Esta consulta complementa la documentación del
origen del campo.

La conclusión de fuga para el escenario del Reto 02 y la exclusión
de la columna ya están documentadas en §3.3.

Referencia normativa:
[Ley 1581 de 2012, artículos 3, 4 y 5](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=49981).
