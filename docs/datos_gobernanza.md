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

| Dimensión | Regla por verificar | Resultado | Acción pendiente |
|---|---|---|---|
| Completitud | Ninguna columna admite valores vacíos, según la ficha técnica. | Pendiente: cantidad y porcentaje de filas afectadas por columna. | Recibir el perfil de calidad y consultar el tratamiento de los faltantes con el dueño del dato. |
| Validez | Los tipos, dominios y rangos deben corresponder a la ficha técnica. | Pendiente: cantidad y porcentaje de filas afectadas por regla. | Identificar los valores concretos fuera del dominio y registrar el tratamiento autorizado. |
| Consistencia | Si internet_service es none, monthly_charges debe ser menor o igual a 60. | Pendiente: cantidad y porcentaje de filas que incumplen RC-3. | Consultar al dueño del dato cómo tratar las inconsistencias encontradas. |
| Unicidad | customer_id debe ser único en el archivo. | Pendiente: cantidad de códigos repetidos y filas involucradas, con su porcentaje. | Consultar el criterio para resolver duplicados y documentar la decisión. |

El diagnóstico está pendiente de recibir y revisar los resultados
agregados del perfil de calidad de la variante V2. Los tratamientos
se incorporarán después de registrar las respuestas del dueño del dato.

## 3. Hallazgos del EDA

## 4. Contrato de datos
Implementado en `contracts/churn_contract.py` y verificado en la etapa `validate` de `dvc.yaml`.

| Campo | Tipo | Reglas | Responsable | Acción si falla |
|---|---|---|---|---|
| tenure_months | int | 0–72 | Dueño del CRM | Detener pipeline |
| contract_type | str | {month-to-month, one-year, two-year} | Dueño del CRM | Detener pipeline |
| … | | | | |

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
