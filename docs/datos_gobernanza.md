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
| Elemento | Decisión |
|---|---|
| Propietario y custodio del dato | |
| Política de acceso | |
| Datos personales y tratamiento (Ley 1581 de 2012) | |
| Versionamiento (DVC y remoto) | |
| Linaje (crudo → validado → train/test → modelo) | `dvc dag` |
| Retención | |
