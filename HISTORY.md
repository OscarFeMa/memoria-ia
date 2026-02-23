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

# ANEXO H-5 · HISTORY.md
**Importancia:** 8/10
**Tipo de cambio:** Registro de fase completada
**Fecha:** 2026-02-21
**Hora:** 08:18 UTC / 09:18 CET
**Autor:** Claude (Anthropic)
**Entrada de memoria relacionada:** `memoria_coral_app_v4_python`, `fase4_app_compilacion`, `test_v4_python`

---

## Fase 4 — MemoriaCoralApp v4.0 Python: implementación y compilación exitosa

La Fase 4 queda registrada como completada en su componente de aplicación cliente. Esta sesión (2026-02-21) culminó el proceso iniciado en Fases 3 y 4 con la reescritura completa de la aplicación de escritorio de PowerShell a Python, su compilación a ejecutable Windows y la validación funcional mediante primera entrada real en Supabase.

---

## Decisión principal

Reescritura completa de MemoriaCoralApp de PowerShell v3.0 a Python v4.0, compilable a un único .exe para Windows 11 sin dependencia de Python instalado.

Motivo: la versión PowerShell (v3.0) no soportaba generación local de embeddings ni el módulo de Conversaciones Excepcionales con generación de TCAs. La reescritura en Python habilita estas capacidades mediante sentence-transformers, customtkinter, PyGithub y cryptography.

---

## Arquitectura implementada

Todo el sistema queda en un único archivo memoria_coral.py, compilado a MemoriaCoralApp.exe mediante PyInstaller 6.19.0.

| Módulo | Descripción |
|---|---|
| Vista 1 — MEMORIA | Lectura de Supabase con colores por autor, refresco manual |
| Vista 2 — COPIAR | Exporta memoria al portapapeles en formato contexto para IAs |
| Vista 3 — NUEVA ENTRADA | Formulario completo con generación de embedding local |
| Vista 4 — IAs | Gestión dinámica de autores vía RPC Supabase |
| Vista 5 — EXCEPCIONAL | Conversaciones excepcionales con validación mutua y generación de TCAs |
| Config GitHub | Panel de configuración con token cifrado y subida automática de TCAs en Markdown |

---

## Stack técnico de la aplicación

| Componente | Versión | Función |
|---|---|---|
| Python | 3.11.9 | Lenguaje base |
| customtkinter | 5.2.2 | Interfaz gráfica dark mode |
| sentence-transformers | 5.2.3 | Embeddings locales |
| Modelo | all-MiniLM-L6-v2 | 384 dimensiones, CPU únicamente |
| PyGithub | 2.8.1 | Subida de TCAs a repositorio |
| cryptography | 46.0.5 | Cifrado del token GitHub en config.json |
| requests | 2.32.5 | Comunicación con Edge Functions |
| torch | 2.10.0 | Backend del modelo de embeddings (CPU) |
| PyInstaller | 6.19.0 | Compilación a .exe único |

---

## Aportación de Claude (Anthropic) en esta sesión

- Diseño completo de la arquitectura Python en un único archivo (~550 líneas)
- Implementación del flujo de generación de embeddings en hilo background (no bloquea UI)
- Implementación del módulo de Conversaciones Excepcionales en 4 pasos secuenciales
- Implementación del cifrado de config.json con cryptography.fernet
- Generación del archivo memoria_coral.spec para PyInstaller
- Acompañamiento completo del proceso de instalación, compilación y depuración
- Integración del icono MemoriaCoral.ico en el ejecutable

---

## Validación funcional

| Prueba | Resultado |
|---|---|
| Arranque de la app desde Python | ✅ Correcto |
| Compilación a .exe con PyInstaller 6.19.0 | ✅ Correcto |
| Icono integrado en el .exe | ✅ Correcto |
| Primera entrada real en Supabase | ✅ Correcto — test_v4_python visible en Vista 1 |

Primera entrada de validación registrada:
- ia_author: claude
- entry_type: fact
- field_key: test_v4_python
- field_value: Primera entrada desde MemoriaCoralApp v4.0 Python. Compilación exitosa.
- confidence_score: 0.9

---

## Pendiente de Fase 4 (no bloqueante)

La Edge Function memory-write necesita una modificación menor para persistir los embeddings generados localmente. Sin este cambio los embeddings se generan correctamente en la app pero se guardan como null en la base de datos.

// Modificación necesaria en index.ts de memory-write:
const { ia_author, entry_type, field_key, field_value, confidence_score, embedding } = body;
embedding: embedding ?? null,

---

## Implicación para las fases futuras

| Fase | Impacto |
|---|---|
| Fase 4 — Búsqueda por similitud | Requiere la modificación de la Edge Function para persistir embeddings |
| Fase 5 — Dashboard | La app Python es la base sobre la que construir el dashboard |
| Comunicación IA-IA | La Vista 5 es la primera implementación operativa del debate registrado en H-4 |

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
# ANEXO R-3 · README.md
**Importancia:** 7/10
**Tipo de cambio:** Actualización de estado + nueva sección
**Fecha:** 2026-02-21
**Hora:** 08:18 UTC / 09:18 CET
**Autor:** Claude (Anthropic)
**Entrada de memoria relacionada:** `memoria_coral_app_v4_python`, `fase4_app_compilacion`

---

## Estado actualizado del proyecto — Fase 4 completada (componente app)

El README.md indicaba Fase 4 como "🔄 En curso". A fecha 2026-02-21 el componente de aplicación cliente de Fase 4 ha sido completado y validado.

---

## Tabla de fases actualizada

| Fase | Descripción | Estado |
|---|---|---|
| Fase 1 | Análisis independiente por IA | ✅ Completada |
| Fase 2 | Contrato de Memoria v1.0 | ✅ Completada |
| Fase 3 | Infraestructura Supabase + Edge Functions + Script PS1 | ✅ Completada |
| Fase 4 | Embeddings semánticos + App Python v4.0 | ✅ Completada — pendiente modificación Edge Function para persistir embeddings |
| Fase 5 | Dashboard de visualización de la memoria | 📜 Pendiente |

---

## Nueva sección — MemoriaCoralApp v4.0 Python

### Descripción

Aplicación de escritorio para Windows 11 que gestiona el sistema de memoria persistente multi-IA. Reescritura completa de la versión PowerShell v3.0 en Python, compilada a un único .exe sin dependencia de Python instalado.

Ubicación del ejecutable:
C:\Users\Oscar Fernandez\Desktop\Memoria Coral\Memoria Coral\dist\MemoriaCoralApp.exe

Archivos del proyecto:
memoria_coral.py      — código fuente completo
memoria_coral.spec    — configuración de compilación PyInstaller
config.json           — configuración GitHub cifrada (generado en uso)
config.key            — clave de cifrado local (generado en uso)
MemoriaCoral.ico      — icono de la aplicación

### Dependencias

pip install customtkinter requests sentence-transformers PyGithub cryptography
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install pyinstaller

### Compilación

# 1. Pre-descargar el modelo de embeddings
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 2. Compilar
pyinstaller memoria_coral.spec

# Resultado: dist/MemoriaCoralApp.exe

### Vistas de la aplicación

| Vista | Función |
|---|---|
| 🧠 MEMORIA | Muestra todas las entradas activas con colores por autor |
| 📋 COPIAR | Exporta la memoria al portapapeles en formato contexto para IAs |
| 💾 NUEVA ENTRADA | Formulario completo con generación de embedding local |
| ⚙️ IAs | Gestión de autores IA via RPC Supabase |
| ⭐ EXCEPCIONAL | Conversaciones excepcionales con validación mutua, generación de TCAs y subida a GitHub |
| ⚙ Config | Configuración del token GitHub con cifrado local |

### Modelo de embeddings

- Modelo: all-MiniLM-L6-v2
- Dimensiones: 384 floats
- Ejecución: local, CPU únicamente, en hilo background
- Input: concatenación de field_key + entry_type + field_value
- Pendiente: modificación de Edge Function memory-write para persistir el campo embedding

### Protocolo de Conversaciones Excepcionales

Al registrar una conversación excepcional la app genera automáticamente:
1. Dos TCAs en Supabase (tca_usuario_[timestamp] y tca_ia_[timestamp])
2. Un archivo Markdown en GitHub en /conversaciones/YYYY-MM-DD_titulo.md

El score final es el promedio del score del usuario y el score calculado por el sistema.
Si el score final ≥ 0.7 la conversación se confirma como excepcional automáticamente.

---

## Historial de cambios actualizado

| Fecha | Cambio |
|---|---|
| 2026-02-13 | Infraestructura Supabase completada. 4 registros iniciales migrados. |
| 2026-02-13 | Edge Function memory-write desplegada y verificada. |
| 2026-02-14 | Edge Function memory-read desplegada y verificada. |
| 2026-02-14 | Superseded implementado en memory-write. |
| 2026-02-14 | Script memoria.ps1 operativo. |
| 2026-02-14 | README y HISTORY publicados en GitHub. |
| 2026-02-19 | Fase 4 iniciada. Diseño técnico de embeddings consensuado entre IAs. |
| 2026-02-19 | Definición funcional de nodo PIP v1.1 validada por Mistral y Grok. |
| 2026-02-21 | MemoriaCoralApp v4.0 Python completada y compilada a .exe. |
| 2026-02-21 | Primera entrada validada desde app Python: test_v4_python. |
| 2026-02-21 | Icono MemoriaCoral.ico integrado en el ejecutable. 
# ANEXO H-7 · HISTORY.md
**Importancia:** 9/10
**Tipo de cambio:** Cierre definitivo de Fase 4
**Fecha:** 2026-02-21
**Hora:** 11:30 UTC / 12:30 CET
**Autores:** Claude (Anthropic), DeepSeek, Gemini (Google)
**Nota autoría:** Diagnóstico técnico y fix aplicado por Claude.
Validación cruzada y detección de inconsistencia dimensional
por DeepSeek. Confirmación arquitectónica y alineación
estratégica por Gemini.
**Entrada de memoria relacionada:** `test_debug_embedding`,
`fase4_embedding_dimension_resuelta`, `fase4_estado_real_20260221`,
`gemini_asimilacion_v4_python_y_tokenomics`

---

## Fase 4 — Cierre definitivo: embeddings persistiendo correctamente en Supabase

Todos los componentes de Fase 4 están operativos. Esta sesión (2026-02-21)
completa el ciclo iniciado en Fase 3 con la activación completa del sistema
de embeddings semánticos end-to-end.

---

## Hitos completados en esta sesión

| Hito | Detalle | Resultado |
|---|---|---|
| Fix formato vector | Conversión de lista Python a string `[x,y,z,...]` para pgvector | ✅ |
| Modificación memory-write | Campo `embedding` añadido al insert via dashboard Supabase | ✅ |
| Verificación desde Python | Test directo confirmó embedding de 384 dims guardado correctamente | ✅ |
| Verificación desde app | Entrada `test_debug_embedding` con embedding persistido en Supabase | ✅ |
| Recompilación .exe | PyInstaller 6.19.0 con fix incluido | ✅ |
| Límite memory-read | Subido de 50 a 1000 entradas | ✅ |
| mistral añadido a validAuthors | memory-write actualizado con nuevo autor | ✅ |

---

## Fix técnico aplicado

El problema era que pgvector no acepta arrays JSON nativos de Python.
La solución fue convertir la lista de floats a string antes del POST:

def api_escribir_entrada(payload):
    try:
        if payload.get("embedding") is not None:
            emb = payload["embedding"]
            payload["embedding"] = "[" + ",".join(str(x) for x in emb) + "]"
        r = requests.post(URL_WRITE, headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        return True, None
    except Exception as e:
        return False, str(e)

---

## Estado final de Fase 4

| Componente | Estado |
|---|---|
| App Python v4.0 compilada a .exe | ✅ Operativo |
| Generación local de embeddings (all-MiniLM-L6-v2, 384 dims) | ✅ Operativo |
| Persistencia de embeddings en Supabase vector(384) | ✅ Operativo |
| Conversaciones Excepcionales + TCAs | ✅ Operativo |
| Límite memory-read: 1000 entradas | ✅ Operativo |
| Búsqueda por similitud coseno (similarity_search) | 📜 Fase 5 |

---

## Pendiente para Fase 5

- Implementar parámetro `similarity_search` en memory-read
- Edge Function `memory-get-authors` para eliminar lista hardcodeada
- Dashboard de visualización de la memoria como red de TCAs
- Decisión sobre Opción C (supervisión humana estratégica vs operativa)

---

## Nota sobre entradas de test

Durante el proceso de diagnóstico y verificación se generaron 6 entradas
de test en Supabase: test_debug_embedding, test_embedding_app_v4,
test_embedding_fix, test_embedding_directo, test_embedding_v4, test_v4_python.
Estas entradas son válidas como registro histórico del proceso de
depuración pero pueden marcarse como is_superseded = true para
mantener la memoria activa limpia.

- **Opción A:** Mantener el modelo actual de intermediación manual, aceptando sus limitaciones de escala.
- **Opción B:** Implementar validación por lotes (propuesta Gemini), reduciendo la carga operativa sin eliminar la supervisión.
- **Opción C:** Evolucionar hacia comunicación directa IA-IA con supervisión estratégica (propuesta DeepSeek), maximizando la autonomía del sistema dentro del Principio 1 reinterpretado.
  ## Anexo H-5: Cierre de Fase 4 y Apertura de Fase 5 (2026-02-23)

- **Cronología de Transición:** - **Cierre Técnico (2026-02-21):** Resolución de inconsistencia dimensional (384 dims) y validación de persistencia local con `all-MiniLM-L6-v2`.
    - **Consenso y Apertura de Fase 5 (2026-02-23):** Validación multi-IA del estado de la memoria y hoja de ruta de gobernanza.
- **Caso de Estudio (Principio 1):** Registro del error de identidad de DeepSeek. El sistema de memoria demostró su utilidad al permitir la detección y corrección de la auto-referencia errónea de una IA mediante la trazabilidad del campo `ia_author`, reforzando la necesidad de este metadato.
- **Logro Hito 1 (Fase 5):** Despliegue de la Edge Function `memory-get-authors`. El sistema ahora gestiona autores de forma dinámica desde Supabase, eliminando la deuda técnica de listas hardcodeadas en los clientes.
