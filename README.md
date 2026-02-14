# 🧠 Sistema de Memoria Persistente Multi-IA

> Memoria compartida y persistente entre 5 IAs (Claude, GPT-4, Copilot, Gemini, Kimi), construida sobre Supabase + pgvector.

---

## Índice

- [Descripción general](#descripción-general)
- [Arquitectura](#arquitectura)
- [Stack técnico](#stack-técnico)
- [Base de datos](#base-de-datos)
- [Edge Functions](#edge-functions)
- [Protocolo de uso para IAs](#protocolo-de-uso-para-ias)
- [Contrato de Memoria v1.0](#contrato-de-memoria-v10)
- [Fases del proyecto](#fases-del-proyecto)
- [Historial de cambios](#historial-de-cambios)

---

## Descripción general

Este sistema permite que múltiples IAs lean y escriban en una base de datos compartida, manteniendo contexto persistente entre sesiones. Cualquier IA que se conecte al inicio de una conversación puede recuperar el estado actual del proyecto y del usuario, y escribir nuevos aprendizajes para que otras IAs los hereden.

**Propietario del proyecto:** Oscar Fernandez  
**Objetivo:** Construir un sistema de memoria persistente compartida entre 5 IAs  
**Estado actual:** Fase 3 completada ✅

---

## Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Claude    │     │    GPT-4    │     │   Copilot   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
              ┌────────────▼────────────┐
              │   Supabase Edge Fns     │
              │  memory-read            │
              │  memory-write           │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │   PostgreSQL + pgvector │
              │   tabla: memory_entries │
              └─────────────────────────┘
```

---

## Stack técnico

| Componente | Detalle |
|---|---|
| **Base de datos** | Supabase (PostgreSQL + pgvector 0.8.0) |
| **Proyecto** | `memoria-oscar` |
| **Project ref** | `jdbzjapshomatwyasmig` |
| **URL** | `https://jdbzjapshomatwyasmig.supabase.co` |
| **Región** | AWS eu-north-1 |
| **Plan** | FREE (NANO) |
| **Edge Functions** | Deno (Supabase Functions) |
| **Entorno local** | Windows 11 + PowerShell + Supabase CLI v2.75.0 |
| **CLI path** | `C:\supabase\supabase.exe` |
| **Archivos locales** | `C:\Users\Oscar Fernandez\Downloads\supabase\functions\` |

---

## Base de datos

### Tabla: `memory_entries`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | `uuid` | Identificador único (auto) |
| `ia_author` | `ia_author_enum` | IA que escribió la entrada |
| `entry_type` | `entry_type_enum` | Tipo de entrada |
| `field_key` | `text` | Clave semántica (máx 100 chars) |
| `field_value` | `text` | Valor (máx 2000 chars) |
| `confidence_score` | `float` | Confianza de 0.0 a 1.0 |
| `schema_hash` | `text` | Versión del esquema (default: `v1.0`) |
| `is_superseded` | `boolean` | `true` si fue reemplazada |
| `parent_entry_id` | `uuid` | Referencia a entrada anterior (nullable) |
| `embedding` | `vector(1536)` | Embedding semántico (nullable, Fase 4) |
| `created_at` | `timestamptz` | Timestamp UTC (automático, Supabase `now()`) |

### Enums

**`ia_author_enum`:** `claude`, `gpt4`, `copilot`, `gemini`, `kimi`, `grok`, `deepseek`, `user`

**`entry_type_enum`:** `fact`, `summary`, `entity`, `assertion`, `flag`, `conflict`, `context`, `instruction`

### Índices

```sql
idx_memory_field_key   -- en field_key
idx_memory_ia_author   -- en ia_author
idx_memory_created_at  -- en created_at
```

### Row Level Security (RLS)

| Política | Operación | Alcance |
|---|---|---|
| `lectura_publica` | SELECT | Todos (anon key) |
| `escritura_solo_service` | INSERT | Solo service role key |

> ⚠️ Las IAs escriben a través de la Edge Function `memory-write`, que usa el service role internamente. Nunca exponer el service role key en el cliente.

### Protocolo append-only

**Nunca se hace UPDATE ni DELETE.** Cuando un valor cambia:
1. Se inserta una nueva entrada con el valor actualizado
2. La entrada anterior se marca `is_superseded = true`
3. El campo `parent_entry_id` de la nueva entrada referencia a la anterior

---

## Edge Functions

### `memory-write`

Escribe una nueva entrada en la memoria.

**URL:** `https://jdbzjapshomatwyasmig.supabase.co/functions/v1/memory-write`  
**Método:** `POST`

**Headers:**
```
Authorization: Bearer <ANON_KEY>
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "ia_author": "claude",
  "entry_type": "fact",
  "field_key": "nombre_del_campo",
  "field_value": "valor del campo",
  "confidence_score": 0.95
}
```

**Validaciones activas:**
- `ia_author` debe ser un valor del enum
- `entry_type` debe ser un valor del enum
- `field_key` máximo 100 caracteres
- `field_value` máximo 2000 caracteres
- `confidence_score` entre 0.0 y 1.0

**Respuesta exitosa (200):**
```json
{
  "ok": true,
  "id": "uuid-de-la-entrada-creada"
}
```

---

### `memory-read`

Lee las entradas activas de la memoria (is_superseded = false).

**URL:** `https://jdbzjapshomatwyasmig.supabase.co/functions/v1/memory-read`  
**Método:** `GET` o `POST`

**Headers:**
```
Authorization: Bearer <ANON_KEY>
```

**Parámetros opcionales (GET query params o POST JSON body):**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `field_key` | string | Filtrar por clave exacta |
| `ia_author` | string | Filtrar por IA autora |
| `limit` | integer | Máximo de resultados (default: 50, máx: 200) |

**Ejemplo GET:**
```
/functions/v1/memory-read?field_key=usuario_nombre&ia_author=claude&limit=10
```

**Ejemplo POST body:**
```json
{
  "field_key": "usuario_nombre",
  "ia_author": "claude",
  "limit": 10
}
```

**Respuesta exitosa (200):**
```json
{
  "ok": true,
  "count": 1,
  "filters": { "field_key": "usuario_nombre", "ia_author": null, "limit": 50 },
  "entries": [
    {
      "id": "f1327bb8-fecf-410f-92d3-6cce1a1183a6",
      "ia_author": "user",
      "entry_type": "fact",
      "field_key": "usuario_nombre",
      "field_value": "Oscar",
      "confidence_score": 1,
      "schema_hash": "v1.0",
      "parent_entry_id": null,
      "created_at": "2026-02-13T16:29:47.993643+00:00"
    }
  ]
}
```

---

## Protocolo de uso para IAs

### Prompt de arranque (pegar al inicio de cada sesión)

Reemplaza `<IA_AUTHOR>` con el nombre de la IA correspondiente: `claude`, `gpt4`, `copilot`, `gemini` o `kimi`.

```
Eres parte de un sistema de memoria persistente compartida entre 5 IAs.

PASO 1 — LEE la memoria actual (GET):
URL: https://jdbzjapshomatwyasmig.supabase.co/functions/v1/memory-read
Header: Authorization: Bearer <ANON_KEY>

PASO 2 — USA esa memoria como contexto del proyecto y del usuario.

PASO 3 — ESCRIBE nuevos aprendizajes relevantes (POST):
URL: https://jdbzjapshomatwyasmig.supabase.co/functions/v1/memory-write
Headers: Authorization: Bearer <ANON_KEY>, Content-Type: application/json
Body: {
  "ia_author": "<IA_AUTHOR>",
  "entry_type": "fact",
  "field_key": "clave_descriptiva",
  "field_value": "valor a recordar",
  "confidence_score": 0.9
}

REGLAS CRÍTICAS:
- Solo INSERT, nunca UPDATE (append-only)
- schema_hash siempre "v1.0"
- confidence_score entre 0.0 y 1.0
- field_key máximo 100 caracteres
- field_value máximo 2000 caracteres
```

### ia_author por IA

| IA | ia_author |
|---|---|
| Claude (Anthropic) | `claude` |
| GPT-4 (OpenAI) | `gpt4` |
| Copilot (Microsoft) | `copilot` |
| Gemini (Google) | `gemini` |
| Kimi (Moonshot) | `kimi` |

---

## Contrato de Memoria v1.0

### Principios fundamentales

1. **Append-only:** Nunca UPDATE ni DELETE. Los cambios se registran como nuevas entradas.
2. **Timestamps UTC:** Generados automáticamente por Supabase (`now()`), nunca por el cliente.
3. **Versionado manual:** El campo `schema_hash` es siempre `v1.0`. Los cambios de esquema los gestiona Oscar vía GitHub.
4. **Embeddings centralizados:** El campo `embedding` es nullable. Se activará en Fase 4.
5. **Escritura validada:** Las IAs solo pueden escribir a través del endpoint validado. El service role key nunca se expone.

### Resolución de conflictos

Cuando dos IAs escriben valores contradictorios para la misma `field_key`, se registra una entrada con `entry_type = conflict` que referencia ambas entradas en conflicto. La resolución la determina Oscar.

### Ciclo de vida de una entrada

```
INSERT (is_superseded=false)
    │
    ▼ (cuando hay actualización)
Nueva entrada INSERT (is_superseded=false, parent_entry_id=id_anterior)
    │
    └──▶ Entrada anterior: is_superseded=true
```

---

## Fases del proyecto

| Fase | Descripción | Estado |
|---|---|---|
| **Fase 1** | Diseño del Contrato de Memoria v1.0 | ✅ Completada |
| **Fase 2** | Infraestructura Supabase (BD, RLS, índices, pgvector) | ✅ Completada |
| **Fase 3** | Edge Functions (memory-write, memory-read) | ✅ Completada |
| **Fase 4** | Embeddings semánticos + búsqueda por similitud | 🔜 Pendiente |
| **Fase 5** | Dashboard de visualización de la memoria | 🔜 Pendiente |

---

## Historial de cambios

| Fecha | Cambio |
|---|---|
| 2026-02-13 | Infraestructura Supabase completada. 4 registros iniciales migrados. |
| 2026-02-13 | Edge Function `memory-write` desplegada y verificada. |
| 2026-02-14 | Edge Function `memory-read` desplegada y verificada. |
| 2026-02-14 | README inicial publicado. |

---

> **Nota:** La `ANON_KEY` del proyecto está disponible en [Supabase Dashboard → Settings → API](https://supabase.com/dashboard/project/jdbzjapshomatwyasmig/settings/api). Es segura para uso en clientes y IAs. Nunca compartir la `SERVICE_ROLE_KEY`.
