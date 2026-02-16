# 🧠 Sistema de Memoria Persistente Multi-IA

> Memoria compartida y persistente entre 5 IAs (Claude, GPT-4, Copilot, Gemini, Kimi), construida sobre Supabase + pgvector.

---

## Índice

- [Descripción general](#descripción-general)
- [Arquitectura](#arquitectura)
- [Stack técnico](#stack-técnico)
- [Base de datos](#base-de-datos)
- [Edge Functions](#edge-functions)
- [Script memoria.ps1](#script-memoriaps1)
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
| **Proyecto** | memoria-oscar |
| **Project ref** | jdbzjapshomatwyasmig |
| **URL** | https://jdbzjapshomatwyasmig.supabase.co |
| **Región** | AWS eu-north-1 |
| **Plan** | FREE (NANO) |
| **Edge Functions** | Deno (Supabase Functions) |
| **Entorno local** | Windows 11 + PowerShell + Supabase CLI v2.75.0 |
| **CLI path** | C:\supabase\supabase.exe |
| **Archivos locales** | C:\Users\Oscar Fernandez\Downloads\supabase\functions\ |

---

## Base de datos

### Tabla: memory_entries

| Campo | Tipo | Descripción |
|---|---|---|
| id | uuid | Identificador único (auto) |
| ia_author | ia_author_enum | IA que escribió la entrada |
| entry_type | entry_type_enum | Tipo de entrada |
| field_key | text | Clave semántica (máx 100 chars) |
| field_value | text | Valor (máx 2000 chars) |
| confidence_score | float | Confianza de 0.0 a 1.0 |
| schema_hash | text | Versión del esquema (default: v1.0) |
| is_superseded | boolean | true si fue reemplazada |
| parent_entry_id | uuid | Referencia a entrada anterior (nullable) |
| embedding | vector(1536) | Embedding semántico (nullable, Fase 4) |
| created_at | timestamptz | Timestamp UTC (automático) |

### Enums

**ia_author_enum:** claude, gpt4, copilot, gemini, kimi, grok, deepseek, user

**entry_type_enum:** fact, summary, entity, assertion, flag, conflict, context, instruction

### Índices

- idx_memory_field_key
- idx_memory_ia_author
- idx_memory_created_at

### Row Level Security (RLS)

| Política | Operación | Alcance |
|---|---|---|
| lectura_publica | SELECT | Todos (anon key) |
| escritura_solo_service | INSERT | Solo service role key |

### Protocolo append-only

Nunca se hace UPDATE ni DELETE. Cuando un valor cambia la entrada anterior se marca is_superseded = true y se inserta una nueva.

---

## Edge Functions

### memory-write

**URL:** https://jdbzjapshomatwyasmig.supabase.co/functions/v1/memory-write
**Método:** POST

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkYnpqYXBzaG9tYXR3eWFzbWlnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM4ODAzNzMsImV4cCI6MjA3OTQ1NjM3M30.AmHDH1dmJ3qme8VYN1EU3zjf7zZAKESal5NXWhX-KMk
Content-Type: application/json
```

**Body:**
```json
{
  "ia_author": "claude",
  "entry_type": "fact",
  "field_key": "nombre_del_campo",
  "field_value": "valor del campo",
  "confidence_score": 0.95
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "entry": { "id": "uuid", ... }
}
```

---

### memory-read

**URL:** https://jdbzjapshomatwyasmig.supabase.co/functions/v1/memory-read
**Método:** GET o POST

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpkYnpqYXBzaG9tYXR3eWFzbWlnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM4ODAzNzMsImV4cCI6MjA3OTQ1NjM3M30.AmHDH1dmJ3qme8VYN1EU3zjf7zZAKESal5NXWhX-KMk
```

**Parámetros opcionales:**

| Parámetro | Descripción |
|---|---|
| field_key | Filtrar por clave exacta |
| ia_author | Filtrar por IA autora |
| limit | Máximo de resultados (default 50, máx 200) |

---

## Script memoria.ps1

Script PowerShell para gestionar la memoria desde el terminal local.

**Ubicación:** C:\Users\Oscar Fernandez\Downloads\supabase\memoria.ps1

**Comandos:**
```powershell
.\memoria.ps1 ver        # Muestra la memoria completa en pantalla
.\memoria.ps1 leer       # Copia la memoria al portapapeles para pegar en una IA
.\memoria.ps1 escribir   # Guarda una nueva entrada interactivamente
```

**Flujo recomendado:**
1. `.\memoria.ps1 leer` — copia el contexto al portapapeles
2. Abre cualquier IA y pega con Ctrl+V
3. Trabaja normalmente
4. Cuando la IA sugiera algo para guardar: `.\memoria.ps1 escribir`

---

## Protocolo de uso para IAs

### Tabla de ia_author

| IA | ia_author |
|---|---|
| Claude (Anthropic) | claude |
| GPT-4 (OpenAI) | gpt4 |
| Copilot (Microsoft) | copilot |
| Gemini (Google) | gemini |
| Kimi (Moonshot AI) | kimi |

### Nota importante

Las IAs de chat no pueden hacer llamadas HTTP externas directamente. El flujo recomendado es usar el script `memoria.ps1` como intermediario.

---

## Contrato de Memoria v1.0

1. **Append-only:** nunca UPDATE ni DELETE
2. **Timestamps UTC:** generados automáticamente por Supabase
3. **Versionado manual:** schema_hash siempre v1.0
4. **Embeddings centralizados:** campo nullable, se activa en Fase 4
5. **Escritura validada:** solo a través del endpoint validado

---

## Fases del proyecto

| Fase | Descripción | Estado |
|---|---|---|
| Fase 1 | Análisis independiente por IA | ✅ Completada |
| Fase 2 | Contrato de Memoria v1.0 | ✅ Completada |
| Fase 3 | Infraestructura Supabase + Edge Functions + Script PS1 | ✅ Completada |
| Fase 4 | Embeddings semánticos + búsqueda por similitud | 🔜 Pendiente |
| Fase 5 | Dashboard de visualización de la memoria | 🔜 Pendiente |

---

## Historial de cambios

| Fecha | Cambio |
|---|---|
| 2026-02-13 | Infraestructura Supabase completada. 4 registros iniciales migrados. |
| 2026-02-13 | Edge Function memory-write desplegada y verificada. |
| 2026-02-14 | Edge Function memory-read desplegada y verificada. |
| 2026-02-14 | Superseded implementado en memory-write. |
| 2026-02-14 | Script memoria.ps1 operativo. |
| 2026-02-14 | README y HISTORY publicados en GitHub. |
🆕 Gestión de nuevos autores IA (Fase 4)
A partir de Fase 4, el sistema permite añadir nuevas IAs al enum ia_author_enum.
Sin embargo, para que la aplicación y las Edge Functions funcionen correctamente, es necesario sincronizar tres capas:

El enum en Supabase

La interfaz o scripts locales (MemoriaCoralApp.ps1)

El Prompt de Arranque usado por las IAs

Si cualquiera de estas capas queda desactualizada, la aplicación no podrá registrar nuevas IAs aunque el enum haya sido modificado en la base de datos.

1. Actualización del enum en Supabase
Para añadir una nueva IA (por ejemplo, mistral), debe ejecutarse:

sql
ALTER TYPE ia_author_enum ADD VALUE IF NOT EXISTS 'mistral';
Este comando requiere permisos service_role.

2. Sincronización con la aplicación local
La aplicación MemoriaCoralApp.ps1 y cualquier interfaz gráfica deben leer dinámicamente los valores del enum desde Supabase.

Consulta recomendada:

sql
SELECT enumlabel
FROM pg_enum
JOIN pg_type ON pg_enum.enumtypid = pg_type.oid
WHERE pg_type.typname = 'ia_author_enum';
Si la aplicación usa una lista local hardcodeada, no podrá registrar nuevas IAs.

3. Sincronización con el Prompt de Arranque
El Prompt de Arranque debe reflejar siempre la lista completa de IAs disponibles.

Tabla actualizada:

IA	ia_author
Claude	claude
GPT‑4	gpt4
Copilot	copilot
Gemini	gemini
Kimi	kimi
Grok	grok
DeepSeek	deepseek
Mistral	mistral
Usuario	user
4. Flujo recomendado para añadir una nueva IA
Ejecutar ALTER TYPE en Supabase.

Verificar que la app lee el enum dinámicamente.

Actualizar el Prompt de Arranque.

Registrar la primera escritura de la nueva IA mediante memory-write.

Confirmar que aparece en memory-read.

5. Problemas comunes
Problema	Causa	Solución
La app no muestra la nueva IA	Lista local hardcodeada	Cambiar a lectura dinámica del enum
La IA no puede escribir	Prompt desactualizado	Actualizar tabla de ia_author
Error en memory-write	Enum no actualizado	Ejecutar ALTER TYPE
6. Estado actual (Fase 4)
mistral ha sido añadido al enum en Supabase.

La aplicación aún no refleja el cambio.

El botón Gestionar IAs requiere verificación.

Se recomienda migrar la app a lectura dinámica del enum.
