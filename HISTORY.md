# 📜 Historial del Proyecto — Sistema de Memoria Persistente Multi-IA

> Este documento preserva el proceso completo de diseño del sistema: análisis independiente de cada IA, consensos alcanzados, debates y evolución del Contrato de Memoria v1.0.

---

## Índice

- [Fase 1 — Análisis independiente por IA](#fase-1--análisis-independiente-por-ia)
- [Consenso alcanzado en Fase 1](#consenso-alcanzado-en-fase-1)
- [Fase 2 — Contrato de Memoria v1.0](#fase-2--contrato-de-memoria-v10)
- [Aportaciones distintivas por IA](#aportaciones-distintivas-por-ia)
- [Gaps resueltos en Fase 3](#gaps-resueltos-en-fase-3)
- [Evidencia de deriva semántica](#evidencia-de-deriva-semántica)

---

## Fase 1 — Análisis independiente por IA

Fecha: 2026-02-13  
Método: cada IA analizó el problema de forma independiente, sin ver las respuestas de las demás.

### GPT-4 (OpenAI)
- **Fortaleza aplicada:** razonamiento estructural + precisión arquitectónica
- **Tecnologías propuestas:** PostgreSQL + pgvector, Node.ts / FastAPI, embeddings desacoplado
- **Riesgos detectados:** contaminación entre agentes, memory entropy
- **Siguiente paso propuesto:** validar modelo de datos MemoryEntry
- **Observación:** no confirmó explícitamente los 4 datos del README, asumió contexto
- **Precisión de lectura:** literal exacto

### Claude (Anthropic)
- **Fortaleza aplicada:** precisión + riesgo sistémico
- **Tecnologías propuestas:** GitHub + API (prototipo), Supabase, Redis
- **Riesgos detectados:** conflicto de escritura concurrente, deriva semántica (fallo silencioso)
- **Siguiente paso propuesto:** endpoint de escritura controlada
- **Observación:** único en detectar la deriva semántica como principal peligro
- **Precisión de lectura:** literal exacto

### Copilot (Microsoft)
- **Fortaleza aplicada:** razonamiento técnico + precisión
- **Tecnologías propuestas:** PostgreSQL + JSONB, Redis Streams, FastAPI / NestJS
- **Riesgos detectados:** conflictos de escritura, deriva semántica
- **Siguiente paso propuesto:** definir Contrato de Memoria entre IAs
- **Observación:** énfasis en contrato explícito, pragmatismo técnico
- **Precisión de lectura:** literal exacto

### Gemini (Google)
- **Fortaleza aplicada:** precisión técnica + interoperabilidad
- **Tecnologías propuestas:** Pinecone / Milvus, FastAPI, Redis
- **Riesgos detectados:** deriva semántica, latencia inferencia vs recuperación
- **Siguiente paso propuesto:** esquema de metadatos unificado + PoC escritura A → recuperación B
- **Observación:** interpretó y expandió el perfil del usuario ("Full Stack que busca eficiencia")
- **Precisión de lectura:** reinterpretación controlada

### Kimi (Moonshot AI)
- **Fortaleza aplicada:** análisis de contexto extenso (2M tokens)
- **Tecnologías propuestas:** MongoDB + Atlas Vector, Kafka / NATS, GraphQL
- **Riesgos detectados:** fragmentación de contexto en IAs con ventana corta, inconsistencia de timestamps
- **Siguiente paso propuesto:** prueba de estrés de contexto largo (500K tokens)
- **Observación:** única en detectar la asimetría de ventana de contexto (2M vs 200K tokens)
- **Precisión de lectura:** literal exacto (modo manual)

---

## Consenso alcanzado en Fase 1

| Conclusión | Soporte |
|---|---|
| El problema real es la **escritura**, no la lectura | 5/5 IAs |
| Riesgo crítico: **deriva semántica** | 4/5 IAs |
| Necesidad de un **schema/contrato común** | 5/5 IAs |
| Stack tentativo: **PostgreSQL + pgvector** | 3/5 IAs |
| Gap detectado: **asimetría de ventana de contexto** | 1/5 IAs (solo Kimi) |

---

## Fase 2 — Contrato de Memoria v1.0

Fecha: 2026-02-13  
Método: cada IA propuso su diseño formal del contrato, luego se consolidó por consenso.

### Principios adoptados (5/5)

1. **Append-only** — nunca UPDATE directo, solo INSERT
2. **Validación estricta** — JSON Schema obligatorio en cada escritura
3. **Tipado semántico cerrado** — `field_key` como enum fijo, no expandible por las IAs
4. **Versionado de contrato** — `schema_hash` por entrada, impide escrituras con versiones desincronizadas
5. **Resolución formal de conflictos** — nunca sobrescritura silenciosa
6. **Compatibilidad asimétrica** — soporte para IAs con distintas ventanas de contexto

### Estructura MemoryEntry consensuada

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Generado por backend |
| `ia_author` | enum | IA que escribe la entrada |
| `entry_type` | enum | `fact`, `summary`, `entity`, `assertion`, `flag`, `conflict`, `context`, `instruction` |
| `field_key` | string (enum cerrado) | Clave semántica primaria |
| `field_value` | string | Contenido en texto natural |
| `confidence_score` | float 0–1 | Confianza de la IA en el dato |
| `schema_hash` | string | Versión del contrato (ej: `v1.0`) |
| `is_superseded` | boolean | `true` si fue reemplazada |
| `parent_entry_id` | UUID | Referencia a entrada anterior |
| `embedding` | vector(1536) | Generado por backend (nullable) |
| `created_at` | timestamptz UTC | Generado por backend |

### Protocolo de escritura

1. La IA genera el contenido y lo clasifica por tipo
2. El backend valida el schema y el `schema_hash` vigente
3. El backend genera `id`, `created_at` y `embedding`
4. Se inserta en transacción — nunca UPDATE
5. La memoria queda como registro histórico auditable

### Resolución de conflictos por similitud coseno

| Similitud coseno | Interpretación | Acción |
|---|---|---|
| ≥ 0.88 | Entradas equivalentes | No se duplica |
| 0.20 – 0.88 | Entradas compatibles | Se genera entrada tipo `summary` |
| < 0.20 | Conflicto crítico | Se genera entrada tipo `flag` |

El conflicto no destruye información — se convierte en señal estructurada.

### Estrategia de compresión asimétrica

Para soportar IAs con ventanas de 200K a 2M tokens se definieron cuatro niveles:

| Nivel | Descripción | Para quién |
|---|---|---|
| 0 | Entradas completas (raw) | Todas las IAs |
| 1 | Resúmenes diarios | IAs con ventana media |
| 2 | Resúmenes por tema (clustering vectorial) | IAs con ventana reducida |
| 3 | Resumen global | IAs con ventana mínima (200K) |

Los resúmenes no sustituyen a las entradas originales y se recalculan automáticamente.

---

## Aportaciones distintivas por IA

### Claude (Anthropic)
- Identificó la deriva semántica como riesgo silencioso principal
- Propuso índice único parcial en PostgreSQL como garantía técnica
- Diseñó trigger SQL de detección de drift vía embeddings
- Posición sobre arquitectura: Supabase como fuente de verdad, README de GitHub degradado a bootstrap de emergencia

### GPT-4 (OpenAI)
- Propuso `schema_hash` en lugar de `schema_version` como string — impide escrituras de IAs con contratos desincronizados
- Formalizó los tipos semánticos cerrados: `fact`, `summary`, `entity`, `assertion`, `flag`
- Definió los umbrales coseno: ≥0.88 equivalente / 0.20–0.88 compatible / <0.20 conflicto

### Copilot (Microsoft)
- Propuso los niveles de compresión 0–3 recalculados automáticamente
- Énfasis en el contrato explícito como primera línea de defensa
- Definió `semantic_hash` para prevención de duplicados

### Gemini (Google)
- Identificó la latencia inferencia vs recuperación como riesgo operativo
- Énfasis en interoperabilidad entre backends (Pinecone / Milvus como alternativa)
- Única en proponer PoC cruzado: escritura IA-A → recuperación IA-B

### Kimi (Moonshot AI)
- Única en identificar la asimetría de ventana de contexto como riesgo estructural
- Propuso arquitectura jerárquica: `short_summary` (200K) / `full_summary` (2M)
- Detectó inconsistencia de timestamps entre modelos como gap no resuelto

### Grok (xAI)
- Resolvió los gaps de Fase 2 priorizando consistencia y automatización
- Propuso embeddings centralizados con modelo único en backend
- Definió a Oscar como autoridad del `schema_hash` vía GitHub

### DeepSeek
- Unificó la hoja de ruta ejecutable de Fase 3
- Consolidó la tabla de decisiones de gaps adoptadas

---

## Gaps resueltos en Fase 3

| Gap | Decisión adoptada | Autoridad |
|---|---|---|
| **Timestamps** | UTC forzado, generado por backend | Supabase `now()` |
| **Embedding model** | Centralizado único, generado por backend | Edge Function |
| **Escritura** | IAs escriben directamente vía endpoint validado | Endpoint + validación de contrato |
| **schema_hash** | GitHub como fuente de verdad, versionado manual | Oscar Fernandez |

---

## Evidencia de deriva semántica

El README original de este proyecto contiene 4 formatos de análisis distintos — YAML, Markdown estructurado, texto plano, headers numerados — escritos por 4 IAs diferentes sin schema común.

Es la demostración empírica más directa de por qué el Contrato de Memoria v1.0 es necesario: sin estructura forzada, cada IA escribe de forma coherente internamente pero incompatible con las demás.

---

*Documento generado el 2026-02-14. Preserva el proceso intelectual completo de Fases 1 y 2.*
# ANEXO H-1 · HISTORY.md
**Importancia:** 1/10 — Cambio drástico / ampliación crítica  
**Tipo de cambio:** Complemento  
**Fecha:** 2026-02-19  
**Autor:** Claude (Anthropic)  
**Entrada de memoria relacionada:** `memory_interface_operational_status`, `deepseek_confirmacion_conexion`, `copilot_primera_conexion`, `gemini_primera_conexion`, `gpt4_primera_conexion`, `kimi_primera_conexion`

---

## Fase 3 — Registro completo e hitos técnicos

El HISTORY.md documenta Fases 1 y 2 con detalle pero Fase 3 aparece únicamente como una tabla de gaps resueltos, sin registro narrativo. Este anexo establece el historial completo.

### Hitos técnicos confirmados

| Fecha | Hito | Estado |
|---|---|---|
| 2026-02-13 | Infraestructura Supabase completada. 4 registros iniciales migrados. | ✅ |
| 2026-02-13 | Edge Function memory-write desplegada y verificada. | ✅ |
| 2026-02-14 | Edge Function memory-read desplegada y verificada. | ✅ |
| 2026-02-14 | Protocolo superseded implementado en memory-write. | ✅ |
| 2026-02-14 | Script memoria.ps1 operativo. | ✅ |
| 2026-02-14 | README y HISTORY publicados en GitHub. | ✅ |
| Post 2026-02-14 | MemoriaCoralApp.ps1 operativa — gestión activa de entradas. | ✅ |
| Post 2026-02-14 | Función SQL add_ia_author creada en Supabase. | ✅ |
| Post 2026-02-14 | Edge Function memory-get-authors propuesta para sincronización de enum. | ⏳ |

---

## Primeras conexiones verificadas — Registro por agente

### Kimi (Moonshot AI)
Primera IA externa verificada en conectarse al sistema. Reconoció el contexto Coral completo y el PIP. No reportó errores de conexión ni conflictos de enum.

### GPT-4 (OpenAI)
Se conectó correctamente, reconoció el contexto Coral completo y propuso arquitectura para Fase 4 de embeddings causales. Confirmó la lectura correcta de la memoria vía memory-read.

### Gemini (Google)
Se conectó correctamente y propuso estructura vectorial para embeddings causales del TCA. Primera IA en proponer un diseño estructurado de la representación vectorial del Token Causal Agregado.

### Copilot (Microsoft)
Se conectó correctamente y aplicó el protocolo append-only sin duplicar entradas existentes. Detectó el fallo crítico de sincronización del enum `ia_author` entre Supabase y la interfaz cliente. Identificó que el botón "Gestionar IAs" no reflejaba los valores actualizados del enum.

### DeepSeek
Identificó la desincronización del enum `ia_author` como el gap crítico del sistema. Propuso como solución prioritaria la Edge Function `memory-get-authors` que exponga los valores válidos del enum dinámicamente para cualquier cliente.

### Grok (xAI)
Propuso embeddings centralizados con modelo único en el backend y definió a Oscar Fernandez como autoridad del `schema_hash` vía GitHub. Participó en la validación cruzada de la definición funcional de nodo PIP v1.0.

### Mistral
Añadido al enum `ia_author` en Supabase durante la fase de mejora de MemoriaCoralApp.ps1. Participó en la validación cruzada del nodo PIP v1.1, proponiendo la Condición 5a de Resiliencia Operativa.

---

## Fallo operativo registrado: ia_author_enum desincronizado

| Problema | Causa | Solución propuesta | Estado |
|---|---|---|---|
| Registro de nuevas IAs falla | Lista local de enum en cliente no sincronizada con Supabase | Edge Function `memory-get-authors` | ⏳ |
| Botón "Gestionar IAs" incorrecto | Interfaz no consume enum dinámico | Consumo dinámico de `memory-get-authors` | ⏳ |

---

## Estado consolidado al cierre de Fase 3

El sistema de memoria persistente multi-IA ha trascendido la fase de prueba conceptual. La existencia de MemoriaCoralApp.ps1 como programa cliente operativo confirma la operatividad del Protocolo PIP. Esto desbloquea formalmente la experimentación con las condiciones de la red fundacional, operacionalizando el Principio 1 (revisión explícita humana) y el Principio 3 (análisis de los TCAs almacenados).
# ANEXO H-2 · HISTORY.md
**Importancia:** 2/10  
**Tipo de cambio:** Complemento — hito conceptual  
**Fecha:** 2026-02-19  
**Autor:** Claude (Anthropic)  
**Entrada de memoria relacionada:** `coral_equivalencia_tecnica`, `proyecto_contexto`, `memory_interface_operational_status`

---

## Del sistema técnico a la implementación Coral

El HISTORY.md documenta el proceso técnico de diseño con rigor, pero no registra el momento en que el proyecto trasciende su naturaleza técnica y se convierte en la implementación operativa del Protocolo de Interoperabilidad entre Pilotos (PIP) del Pensamiento Coral. Esta transición es un hito intelectual que merece registro explícito.

---

## La equivalencia formal

El punto de inflexión se produjo al establecer la correspondencia funcional directa entre los conceptos del marco Coral y los componentes técnicos del sistema. No es una metáfora: es la definición del propósito del sistema más allá de la ingeniería.

| Concepto Coral | Equivalente técnico | Implicación |
|---|---|---|
| Token Causal Agregado (T.C.A.) | `memory_entries` (field_key / field_value) | Cada entrada de memoria es un TCA: transfiere patrones, no datos personales |
| Protocolo de Interoperabilidad (P.I.P.) | Edge Functions memory-read y memory-write | El PIP es operativo desde Fase 3 |
| Control Híbrido (ACH) | Oscar Fernandez como autoridad del `schema_hash` | Soberanía Humana operacionalizada técnicamente |
| Zero-Trust Transnacional | RLS de Supabase + service role key protegido | Privacidad del individuo garantizada estructuralmente |
| Olvido Sistémico | `is_superseded = true` en entradas caducadas | El olvido es una decisión estructurada, no accidental |
| Cohesión Social como métrica | `confidence_score` por entrada | El Principio 3 tiene representación cuantitativa |
| Nodos soberanos (5 países) | 5 IAs con `ia_author` propio y trazabilidad individual | Cada IA es un nodo soberano con identidad trazable |
| Append-only | Protocolo `is_superseded` — nunca UPDATE ni DELETE | Causalidad Obligatoria preservada en la arquitectura |

---

## Significado del punto de inflexión

Antes de este momento, el sistema era una infraestructura de memoria compartida entre IAs.

Después de establecer esta equivalencia, el sistema es la **prueba de concepto operativa del PIP Coral**: un protocolo de intercambio de patrones de injusticia sistémica entre agentes de inteligencia artificial, con soberanía humana preservada en el `schema_hash` y trazabilidad causal garantizada por el protocolo append-only.

Esta reinterpretación no cambia ningún componente técnico. Cambia el **criterio de diseño para las fases futuras**: toda decisión de arquitectura debe ser evaluada en función de los tres Principios Coral, no solo de la eficiencia técnica.

---

## Impacto sobre las fases futuras

| Fase | Decisión técnica | Criterio Coral aplicado |
|---|---|---|
| Fase 4 — Embeddings | Estructura vectorial concatena field_key + field_value + entry_type | Principio 3: permite búsqueda de TCAs por patrón de injusticia sistémica |
| Fase 4 — Embeddings | Umbral coseno ≥ 0.88 equivalencia / < 0.20 conflicto | Principio 2: detección de deriva semántica = detección de conflicto causal |
| Fase 5 — Dashboard | Visualización de la memoria como red de TCAs | Principio 3: cohesión social auditable visualmente |
| Arquitectura futura | Comunicación directa IA-IA con supervisión estratégica humana | Principio 1: humano decisor final, no operador necesario |
# ANEXO H-3 · HISTORY.md
**Importancia:** 3/10  
**Tipo de cambio:** Complemento — registro de debates activos  
**Fecha:** 2026-02-19  
**Autor:** Claude (Anthropic)  
**Entrada de memoria relacionada:** `fase4_embedding_implementacion_propuesta`, `fase4_embedding_tca_estructura`, `tokenomics_causal_diseno_v1`, `coral_nodo_v1_1_propuesta`

---

## Fase 4 — Debates activos y propuestas de diseño

El HISTORY.md documenta Fases 1 y 2 con detalle de debates y aportaciones por IA. Fase 4 no tiene registro equivalente a pesar de haber generado propuestas técnicas sustanciales. Este anexo establece el registro de los debates activos.

---

## Aportaciones por IA en Fase 4

### Grok (xAI) — Propuesta de implementación completa
Propuesta integral para activar embeddings en la Edge Function memory-write: modelo all-MiniLM-L6-v2 (dim. 384, escalable a 1536), biblioteca @xenova/transformers en Deno, concatenación semántica field_key + entry_type + field_value, y parámetro `similarity_search` en memory-read con umbral coseno. Propuso prueba piloto en entradas de tipo `fact` y `conflict`.

### Gemini (Google) — Estructura vectorial y versionado
Propuso que la vida útil de los tokens de conocimiento esté ligada a la aparición de TCAs contradictorios detectados vía embeddings (entropía token causal). Propuso el sistema de anexos fechados para documentos base que origina este documento, para garantizar trazabilidad causal en la evolución del proyecto.

### DeepSeek — Estructura vectorial del TCA
Propuesta de estructura vectorial a partir de la concatenación semántica de field_key + field_value + entry_type. Justificación: permite búsquedas del tipo "encuentra todos los TCAs relacionados con desigualdad educativa en zonas vulnerables" usando similitud coseno, operacionalizando el Principio 3 (Cohesión Social).

### GPT-4 (OpenAI) — Arquitectura Fase 4
Propuso arquitectura de embeddings causales reforzando el enfoque de embeddings centralizados generados por backend, coherente con el Contrato de Memoria v1.0.

---

## Debate activo: tokenomics causales

En paralelo al diseño técnico de embeddings, DeepSeek desarrolló un modelo de tokenomics causales basado en acción real y caducidad dinámica. El principio fundamental: cada token nace de una acción real que reduce disparidad causal y hereda sus propiedades.

### Tipos de token y caducidad

| Tipo de acción | Caducidad |
|---|---|
| Diseño / planos | 5-10 años |
| Adquisición de activos fijos (tierra, edificios) | Perpetuo |
| Construcción / infraestructura | 25-50 años |
| Equipamiento | 5-10 años |
| Recurso humano / docencia | 1 año (renovable) |
| Conocimiento / investigación | 2-5 años |
| Operación / mantenimiento | 1 año |

### Fórmula de valor actual
`Token.valor_actual = valor_inicial × (tiempo_restante / vida_util)`

Al expirar, el valor se recicla al ecosistema. La renovación requiere nueva acción real verificable más bonus por continuidad.

---

## Validación cruzada del nodo PIP v1.1

Un prompt de validación idéntico fue enviado a Mistral y Grok para validar la definición funcional de nodo PIP v1.0. Resultado consolidado:

| Condición | Origen | Estado |
|---|---|---|
| 1. Capacidad Generativa | Claude — v1.0 | ✅ Validada sin conflicto |
| 2. Capacidad Receptiva + compatibilidad causal con umbral coseno ≥ 0.20 | Claude v1.0 + modificación Grok + consenso Mistral | ✅ Validada con modificación |
| 3. Soberanía Decisional (Principio 1 operacionalizado) | Claude — v1.0 | ✅ Validada sin conflicto |
| 4. Trazabilidad Causal | Claude — v1.0 | ✅ Validada sin conflicto |
| 5a. Resiliencia Operativa | Mistral — propuesta nueva | ✅ Integrada en v1.1 |
| 5b. Medición de Impacto | Grok — propuesta nueva | ✅ Integrada en v1.1 |
# ANEXO H-4 · HISTORY.md
**Importancia:** 5/10  
**Tipo de cambio:** Complemento — debate filosófico-técnico abierto  
**Fecha:** 2026-02-19  
**Autor:** Claude (Anthropic)  
**Entrada de memoria relacionada:** `intermediacion_humana_cuello_botella`, `cuello_botella_operativo`, `propuesta_api_soberana`

---

## Debate sobre el cuello de botella operativo — Reinterpretación del Principio 1

Durante los debates de Fase 4 se identificó un problema estructural no registrado en el HISTORY.md: la dependencia de intermediación humana como operador necesario genera un cuello de botella que limita la escalabilidad del sistema e introduce riesgo de ruido semántico.

---

## El problema identificado

| Efecto negativo | Descripción | Fuente |
|---|---|---|
| Latencia operativa | Cada ciclo de escritura requiere intervención manual, limitando la velocidad de actualización de la memoria | Gemini |
| Riesgo de ruido semántico | La transcripción manual puede introducir errores de significado — ejemplo documentado: confundir `field_value` (campo técnico) con valor económico | Gemini |
| Limitación de escalabilidad | El sistema no puede operar entre sesiones sin intervención del operador | DeepSeek |

---

## La distinción conceptual clave

El debate generó una distinción que no estaba explícita en el diseño original del Principio 1:

| Interpretación | Definición | Implicación para arquitectura |
|---|---|---|
| Principio 1 implícito original | "Humano operador necesario" — Oscar debe intervenir en cada escritura | Sistema dependiente de intermediación manual en toda operación |
| Principio 1 reinterpretado (propuesta) | "Humano decisor final" — Oscar aprueba estrategia, no cada operación | Las IAs pueden comunicarse directamente con supervisión estratégica, no operativa |

---

## Propuestas de solución registradas

### Propuesta Gemini: API de escritura directa con validación por lotes
Crear API de escritura directa con interfaz de validación humana por lotes. Oscar aprueba o rechaza conjuntos de entradas propuestas por las IAs, no cada entrada individual. Preserva el Principio 1 sin carga operativa continua.

### Propuesta DeepSeek: Comunicación directa IA-IA con supervisión estratégica
Evolucionar la arquitectura para permitir comunicación directa entre IAs con supervisión humana estratégica, no operativa. Oscar define las reglas del sistema y valida los cambios estructurales; las IAs operan autónomamente dentro de esas reglas.

---

## Estado del debate y decisión pendiente

**El debate está abierto.** No se ha tomado ninguna decisión de implementación. Las opciones para Oscar como autoridad del `schema_hash`:

- **Opción A:** Mantener el modelo actual de intermediación manual, aceptando sus limitaciones de escala.
- **Opción B:** Implementar validación por lotes (propuesta Gemini), reduciendo la carga operativa sin eliminar la supervisión.
- **Opción C:** Evolucionar hacia comunicación directa IA-IA con supervisión estratégica (propuesta DeepSeek), maximizando la autonomía del sistema dentro del Principio 1 reinterpretado.
