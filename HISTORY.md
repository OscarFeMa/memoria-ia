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
