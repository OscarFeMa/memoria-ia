# MEMORIA IA v1.0

## PERFIL
usuario_nombre: Oscar
usuario_objetivo: Crear sistema de memoria persistente entre IAs

## CONTEXTO
fecha_hoy: 2026-02-13
proyecto_actual: Validar sistema de memoria con Kimi

## HISTORIAL

## NOTAS
# MEMORIA IA v2.0 - SISTEMA MULTI-IA

## GENERADO POR
ia_autora: Kimi K2.5 (Moonshot AI)
fecha_generacion: 2026-02-13
ventaja_distintiva: ventana_contexto_2M_tokens + analisis_documentos_largos

---

## PERFIL
usuario_nombre: Oscar
usuario_objetivo: Crear sistema de memoria persistente entre IAs
fecha_hoy: 2026-02-13
proyecto_actual: Validar sistema de memoria con 5 IAs (GPT-4, Claude, Copilot, Gemini, Kimi)

## CONTEXTO
fase_actual: consolidacion_arquitectonica_v1.0
problema_identificado: ESCRITURA controlada (lectura ya funciona via GitHub raw)
riesgo_principal: DERIVA SEMANTICA entre modelos
solucion_requerida: CONTRATO DE MEMORIA v1.0 comun

## HISTORIAL_ANALISIS_FASE1

### GPT-4
fortaleza_aplicada: razonamiento estructural + precision arquitectonica
tecnologias_propuestas: PostgreSQL+pgvector, Node.ts/FastAPI, Embeddings desacoplado
riesgos_detectados: contaminacion entre agentes, memory entropy
siguiente_paso: validar modelo datos MemoryEntry
observacion: no confirmo explicitamente 4 datos, asumio contexto
precision_lectura: literal exacto

### Claude
fortaleza_aplicada: precision + riesgo sistemico
tecnologias_propuestas: GitHub+API (prototipo), Supabase, Redis
riesgos_detectados: conflicto escritura concurrente, DERIVA SEMANTICA (fallo silencioso)
siguiente_paso: endpoint escritura controlada
observacion: unico en detectar deriva semantica como principal peligro
precision_lectura: literal exacto

### Copilot
fortaleza_aplicada: razonamiento tecnico + precision
tecnologias_propuestas: PostgreSQL+JSONB, Redis Streams, FastAPI/NestJS
riesgos_detectados: conflictos escritura, DERIVA SEMANTICA
siguiente_paso: definir CONTRATO DE MEMORIA entre IAs
observacion: enfasis en contrato explicito, pragmatismo tecnico
precision_lectura: literal exacto

### Gemini
fortaleza_aplicada: precision tecnica + interoperabilidad
tecnologias_propuestas: Pinecone/Milvus, FastAPI, Redis
riesgos_detectados: DERIVA SEMANTICA, latencia inferencia vs recuperacion
siguiente_paso: esquema metadatos unificado + PoC escritura A -&gt; recuperacion B
observacion: interpreto/expandido perfil ("Full Stack que busca eficiencia")
precision_lectura: reinterpretacion controlada

### Kimi
fortaleza_aplicada: analisis contexto extenso (2M tokens)
tecnologias_propuestas: MongoDB+Atlas Vector, Kafka/NATS, GraphQL
riesgos_detectados: fragmentacion contexto IAs ventana corta, inconsistencia timestamps
siguiente_paso: prueba estres contexto largo (500K tokens)
observacion: unico en detectar ASIMETRIA VENTANA CONTEXTO (2M vs 200K tokens)
precision_lectura: literal exacto (modo manual)

## CONSENSO_ALCANZADO_FASE1
- problema_real: no es lectura, es ESCRITURA controlada
- riesgo_critico: DERIVA SEMANTICA (4/5 IAs detectaron)
- necesidad: SCHEMA/CONTRATO comun (5/5 IAs coinciden)
- stack_tentativo: PostgreSQL + pgvector (mayoria 3/5)
- gap_detectado: asimetria ventana contexto (solo Kimi)

## TAREA_FASE2
Diseñar CONTRATO DE MEMORIA v1.0 con:
1. SCHEMA JSON MemoryEntry (campos obligatorios, tipos, restricciones)
2. PROTOCOLO escritura (sin sobrescritura, control concurrente)
3. MECANISMO resolucion conflictos (misma clave, valores diferentes)
4. ESTRATEGIA compresion asimetrica (200K vs 2M tokens)

## NOTAS
espacio_para_actualizaciones_post_fase2

## ANÁLISIS CLAUDE (Anthropic) — 2026-02-13

### Fortaleza aplicada: Razonamiento arquitectónico + precisión técnica

### Valoración del sistema actual
El mecanismo de lectura via GitHub raw funciona como prototipo válido.
El gap crítico es la escritura: sin control de concurrencia, cualquier
IA puede sobrescribir a otra sin conflicto detectable.

### Tecnologías recomendadas (backend)
- PostgreSQL + pgvector: almacén principal con soporte vectorial nativo
- Supabase: capa de API + autenticación + RLS sin infraestructura propia
- Redis (Upstash): caché de sesión activa + pub/sub para sincronización entre IAs

### Riesgos identificados
1. Escritura concurrente sin control → sobrescritura silenciosa de datos
2. Deriva semántica → cada IA reinterpreta campos de texto libre
   de forma diferente, corrompiendo la memoria sin errores visibles

### Solución propuesta: Contrato de Memoria v1.0
Principios clave:
- field_key como enum cerrado (vocabulario fijo, no expandible por IA)
- Escritura append-only con proyección (ninguna IA sobrescribe directamente)
- Índice único parcial en PostgreSQL: solo 1 entrada activa por usuario+campo
- Trigger de detección de deriva semántica via similitud coseno (umbral: 0.75)
- Resolución de conflictos por política: confidence_score > recencia > revisión humana
- Compresión adaptativa por ventana de contexto:
    gemini/claude → vista full
    gpt4/kimi     → vista compact  
    copilot       → vista minimal

### Estructura de dato propuesta (MemoryEntry — campos obligatorios)
entry_id, session_id, ia_author, user_id, field_key (enum),
field_value, value_type, schema_version, confidence_score,
created_at, parent_entry_id, is_superseded, embedding (nullable)

### Posición sobre arquitectura general
- Fuente de verdad: Supabase (PostgreSQL)
- README de GitHub: conservar como bootstrap de emergencia únicamente
- Contrato único de escritura para todas las IAs
- Proyecciones de lectura diferenciadas por capacidad de cada modelo

### Compatibilidad con otras IAs
El contrato es intencionalmente agnóstico al modelo.
El campo ia_author registra quién escribió cada entrada.
Ninguna IA tiene privilegios de escritura sobre los campos de otra.

### Siguiente paso recomendado
Crear tabla memory_entries en Supabase, migrar los 4 campos
actuales del README, y validar el endpoint de escritura con
una sola IA antes de conectar las cinco en paralelo.

### Advertencia específica de Claude
La deriva semántica es el riesgo más subestimado del sistema:
falla en silencio, sin errores técnicos, y solo se detecta
comparando semánticamente entradas sucesivas del mismo campo.
Verificar si las otras IAs lo mencionaron de forma independiente.

Soy Copilot, uno de los cinco agentes de IA que participan en el diseño del Sistema de Memoria Persistente Multi‑IA. Este documento resume el estado actual del proyecto, el consenso alcanzado y el Contrato de Memoria v1.0 que todas las IAs podrán consultar, interpretar y extender.

OBJETIVO DEL PROYECTO
Crear un sistema de memoria persistente que permita a múltiples IAs (GPT‑4, Claude, Copilot, Gemini y Kimi) leer y escribir información de forma coherente, sin sobrescrituras, con control semántico y con capacidad de evolución. El sistema debe ser auditable, versionado y compatible con PostgreSQL + pgvector.

CONSENSO ENTRE LAS 5 IAs
• Problema crítico: la escritura. La lectura ya funciona correctamente.
• Riesgo principal: deriva semántica entre modelos.
• Solución necesaria: un contrato de memoria común, estricto y validable.
• Requisito clave: evitar sobrescritura y permitir compresión para modelos con ventanas pequeñas.

CONTRATO DE MEMORIA v1.0

SCHEMA JSON DE MemoryEntry
Cada entrada es atómica y append‑only. El backend valida y completa los campos.

{
"id": "uuid",
"timestamp": "ISO-8601",
"agent": {
"id": "string",
"model": "string",
"version": "string"
},
"type": "context | fact | event | instruction | summary | conflict",
"content": {
"text": "string",
"tokens": "integer"
},
"semantic_hash": "sha256",
"vector": "pgvector[1536]",
"metadata": {
"confidence": "0.0-1.0",
"source": "user | system | ia",
"tags": ["string"]
}
}

Reglas clave del schema:
• El backend genera id, timestamp, semantic_hash y vector.
• type es un enum estricto.
• content.text tiene límite de longitud.
• semantic_hash evita duplicados.
• confidence ayuda a gestionar contradicciones.
• vector permite clustering y detección de conflictos.

PROTOCOLO DE ESCRITURA
Paso 1: la IA envía una propuesta con agent_id, type, text y tags.
Paso 2: el backend valida esquema, longitud, duplicados, coherencia semántica y normaliza el texto.
Paso 3: el backend genera los campos finales y guarda la entrada sin modificar ninguna existente.
Política fundamental: append‑only, ninguna IA sobrescribe a otra.

RESOLUCIÓN DE CONFLICTOS
Un conflicto se detecta cuando dos entradas hablan del mismo concepto, sus vectores son muy similares y su contenido difiere.
El backend genera automáticamente una entrada de tipo conflict que documenta el choque.
Las IAs pueden proponer resoluciones o generar summaries consensuados.
El backend nunca elimina entradas.

ESTRATEGIA DE COMPRESIÓN
Para soportar modelos con ventanas de 200K a 2M tokens, se definen cuatro niveles:
• Nivel 0: entradas completas (raw).
• Nivel 1: resúmenes diarios.
• Nivel 2: resúmenes por tema mediante clustering vectorial.
• Nivel 3: resumen global para ventanas pequeñas.
Los resúmenes no sustituyen a las entradas originales y se recalculan automáticamente.

RECOMENDACIONES PARA EL README
• Añadir sección “Contrato de Memoria v1.0”.
• Registrar los agentes participantes y su rol.
• Declarar la política append‑only.
• Definir umbrales semánticos para detección de conflictos.
• Mantener este documento como referencia común para todas las IAs.

FINALIDAD
Este resumen sirve como base compartida para que GPT‑4, Claude, Copilot, Gemini y Kimi puedan interpretar, extender y mejorar el sistema de memoria de forma coordinada.

```
ia_author = GPT4
document_type = architectural_summary
version = 1.0
phase = Consolidación Arquitectónica (Fase 2)
project = Sistema de Memoria Persistente entre IAs
date = 2026-02-13
```

# Resumen Arquitectónico — Contrato de Memoria v1.0

Como GPT4, tras analizar la memoria persistente compartida y los resultados de Fase 1 (5 IAs evaluando lectura y arquitectura), presento la propuesta formal del **Contrato de Memoria v1.0**, cuyo objetivo es resolver el problema crítico identificado: la escritura controlada multi-agente y la prevención de deriva semántica.

---

# 1. Diagnóstico Consolidado

Fase 1 confirmó:

* ✅ La lectura compartida funciona (GitHub raw probado con 5 IAs).
* ❗ El problema real no es acceso, sino escritura coordinada.
* ❗ El riesgo principal es deriva semántica.
* ✅ Se requiere un contrato/schema obligatorio.
* ✅ PostgreSQL + pgvector es el stack más consistente.
* ⚠️ Existe asimetría de contexto (200K vs 2M tokens).

Conclusión: necesitamos estructura, no solo almacenamiento.

---

# 2. Principios del Contrato v1.0

1. Append-only — No se sobrescribe historia.
2. Validación estricta — JSON Schema obligatorio.
3. Tipado semántico cerrado — Reduce ambigüedad.
4. Versionado de contrato (schema_hash) — Evita escrituras incompatibles.
5. Resolución formal de conflictos — Nunca sobrescritura silenciosa.
6. Compatibilidad asimétrica — Soporte para IAs con distintas ventanas de contexto.

---

# 3. Unidad Mínima: MemoryEntry

Estructura obligatoria:

* id (UUID)
* source_agent
* type (fact | summary | entity | assertion | flag)
* key (clave semántica primaria)
* content (texto natural)
* vector (embedding normalizado)
* created_at
* validity:

  * confidence (0–1)
  * schema_hash
* metadata (opcional)

Decisiones clave:

* El campo `type` reduce deriva semántica.
* El campo `schema_hash` obliga sincronización de versión.
* El vector permite comparación semántica objetiva.
* UNIQUE (key, source_agent) evita duplicados por agente.

---

# 4. Protocolo de Escritura

Flujo obligatorio:

1. Generar contenido.
2. Clasificar tipo.
3. Generar embedding aprobado.
4. Validar contra JSON Schema.
5. Verificar schema_hash vigente.
6. Insertar en transacción SERIALIZABLE.
7. Commit.

Regla central:
No se permite UPDATE directo. Solo INSERT.

Esto convierte la memoria en un registro histórico auditable.

---

# 5. Resolución de Conflictos

Caso: misma key, contenidos distintos.

Se calcula similitud coseno entre embeddings.

* ≥ 0.88 → equivalentes → no se duplica.
* 0.20–0.88 → compatibles → se genera entrada tipo summary.
* < 0.20 → conflicto crítico → se genera entrada tipo flag.

El conflicto no destruye información.
Se convierte en señal estructurada.

---

# 6. Prevención de Deriva Semántica

Mecanismos activos:

* Tipos semánticos cerrados.
* Validación estricta de schema.
* Hash obligatorio de contrato.
* Embeddings normalizados.
* Consolidación periódica en summaries.
* Trazabilidad por agente.

La deriva se previene estructuralmente, no por heurística informal.

---

# 7. Estrategia de Compresión Asimétrica

Problema: IAs con 200K vs 2M tokens.

Solución: memoria jerárquica.

Cada conjunto de entradas puede generar:

* short_summary (optimizado para 200K)
* full_summary (para 2M)

Flujo:

Memoria granular → agrupación semántica → resumen intermedio → resumen global.

Las IAs pequeñas consumen short_summary.
Las IAs grandes pueden expandir al contenido completo.

No se pierde información, solo se reorganiza.

---

# 8. Estado del Sistema tras v1.0

Con este contrato:

* La lectura ya está validada.
* La escritura queda formalizada.
* El conflicto es gestionable.
* La deriva tiene mitigación estructural.
* La arquitectura soporta múltiples IAs heterogéneas.
* PostgreSQL + pgvector es suficiente como backend estable.

El sistema deja de ser experimental y pasa a ser arquitectónico.

---

# Conclusión

El Contrato de Memoria v1.0 establece reglas formales que permiten a múltiples IAs compartir memoria sin sobrescribirse, sin ambigüedad semántica y sin perder trazabilidad histórica.

La clave no es almacenar más información.
Es almacenar bajo contrato.

— GPT4
