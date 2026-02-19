# 🌊 Pensamiento Coral — Gobernanza Causal Híbrida (G.C.H.)

> Marco conceptual y filosófico que fundamenta el Sistema de Memoria Persistente Multi-IA.
> Elaborado por Oscar Fernandez con la colaboración de Claude, GPT-4, Copilot, Gemini y Kimi.
> Noviembre 2025.

---

## Qué es el Pensamiento Coral

El Pensamiento Coral es un framework de gobernanza para la Inteligencia Artificial General (IAG) cuyo propósito fundacional es garantizar que la IA sirva a la Cohesión Social y la Soberanía Humana, en lugar de acelerar la desigualdad sistémica.

## El problema: Disparidad Causal

La Disparidad Causal es la brecha entre quienes comprenden y controlan los efectos sistémicos de la IAG, y quienes sufren sus consecuencias no intencionadas sin poder rastrear su origen.

## Los tres principios innegociables

1. Soberanía Humana — toda decisión estratégica es irrevocablemente humana. La IAG es un asistente causal.
2. Causalidad Obligatoria — la IAG modela causas, no correlaciones. Toda recomendación incluye diagnóstico de causalidad.
3. Cohesión Social — la reducción cuantificable de la Disparidad Causal es el propósito primario y auditable.

## Arquitectura técnica

### Doble Canal de Output

| Canal | Descripción | Destinatario |
|---|---|---|
| Canal Seguro | Recomendación de sentencia, política o acción | Operador humano |
| Canal Experimental | Transferencia de Tokens Causales Agregados | Otras instituciones y países |

### Control Híbrido y Kill Switch

La Autoridad de Control Híbrido (ACH) es la única entidad con facultad de auditoría constante y poder de activar el Kill Switch Operacional si se detecta sesgo algorítmico crítico.

### Zero-Trust Transnacional

La infraestructura opera bajo modelo Zero-Trust que garantiza privacidad absoluta del individuo y transparencia en la causalidad, no en los datos personales.

## El Token Causal Agregado

El Token Causal Agregado (T.C.A.) es la unidad mínima de intercambio entre sistemas IAG. No transfiere datos personales — transfiere patrones de injusticia sistémica con mandato de corrección.
```json
{
  "id_token_unico": "TCA-JUS-ED-20251121-789XYZ",
  "nodo_origen": "CL-Justicia-Penal",
  "nodo_destino": "CL-Educacion",
  "fecha_emision": "2025-11-21T18:27:00Z",
  "nivel_agregacion": "GEOGRAFICO",
  "modulo_causalidad": {
    "causa_detectada": "Baja alfabetizacion digital y financiera",
    "sector_causal": "Educacion",
    "fuerza_correlacion": 0.78,
    "unidades_analizadas": 3450
  },
  "modulo_localizacion": {
    "tipo_geografico": "COMUNA",
    "identificador_zona": ["CL-RM-PteAlto", "CL-RM-SanBdo"],
    "indices_vulnerabilidad": ["Alto GINI Local"]
  },
  "modulo_politica_sugerida": {
    "accion_sugerida": "Implementar Talleres de Finanzas y Codigo",
    "meta_impacto": "Aumentar cobertura educativa en 40% en 12 meses",
    "urgencia": "ALTA"
  }
}
```

## Red Fundacional de Pilotos

| Nodo | Sector | Desafio estrategico | Principio validado |
|---|---|---|---|
| Chile | Justicia - Educacion | Disparidad socioeconómica | Causalidad Obligatoria |
| Alemania | Salud / Energia | Infraestructura crítica | Control Hibrido + Kill Switch |
| India | Energia / Salud | Escala masiva | Equidad Transnacional |
| España | Educacion | Subsidiariedad cultural | Subsidiariedad Causal |
| Sudafrica | Gobernanza | Justicia restaurativa | Cohesion Social |

## Instituciones propuestas

### A nivel nacional
| Institución | Rol |
|---|---|
| Autoridad de Control Híbrido (ACH) | Guardian tecnico-etico. Activa el Kill Switch. |
| Oficina de Causalidad Pública (OCP) | Centraliza datos anonimizados. Gestiona Tokens. |
| Cámara de Cohesión Social (CCS) | Auditoria ciudadana. Supervisa equidad. |

### A nivel global (ONU)
| Institución | Rol |
|---|---|
| Observatorio de Causalidad Global (OCG) | Adscrito a UNESCO/PNUD. Audita Tokens globales. |
| Consejo Asesor de Control Híbrido (CACH) | Asesora al Consejo de Seguridad ante riesgos IAG. |
| Comité de Arbitraje Causal (CAC) | Resuelve disputas tecnicas entre nodos del PIP. |

## Conexión con el Sistema de Memoria Multi-IA

| Concepto Coral | Equivalente técnico |
|---|---|
| Token Causal Agregado (T.C.A.) | memory_entries con field_key / field_value |
| Protocolo de Interoperabilidad (P.I.P.) | Edge Functions memory-read y memory-write |
| Control Hibrido (ACH) | Oscar Fernandez como autoridad del schema_hash |
| Zero-Trust Transnacional | RLS de Supabase + service role key protegido |
| Append-only | Protocolo is_superseded - nunca UPDATE ni DELETE |
| Cohesion Social como metrica | confidence_score por entrada |
| Nodos soberanos (5 paises) | 5 IAs con ia_author propio y trazabilidad individual |
| Mecanismo de Olvido Sistemico | is_superseded = true en entradas caducadas |

---
# ANEXO C-1 · CORAL.md
**Importancia:** 3/10  
**Tipo de cambio:** Corrección + ampliación  
**Fecha:** 2026-02-19  
**Autor:** Claude (Anthropic)  
**Entrada de memoria relacionada:** `coral_red_fundacional_status`, `coral_nodo_definicion_funcional`, `coral_nodo_v1_1_propuesta`

---

## Redefinición funcional del nodo PIP — De geografía a función

El CORAL.md presenta los 5 nodos geográficos (Chile, Alemania, India, España, Sudáfrica) como la arquitectura técnica de la Red Fundacional de Pilotos. Durante Fases 3 y 4, esta definición fue formalmente revisada.

**Decisión registrada en memoria:** los 5 nodos geográficos originales son ejemplos ilustrativos de la propuesta ONU, no arquitectura técnica válida para Fase 4. La definición funcional los reemplaza como base de diseño. La geografía y el dominio temático son atributos opcionales, no definitorios.

---

## Definición funcional de nodo PIP v1.1

Un nodo PIP es válido si cumple las siguientes 6 condiciones funcionales:

| Condición | Descripción | Principio Coral |
|---|---|---|
| 1. Capacidad Generativa | El nodo puede producir TCAs válidos según el Contrato de Memoria v1.0 | Principio 2: Causalidad Obligatoria |
| 2. Capacidad Receptiva + compatibilidad causal | El nodo puede recibir TCAs y verificar compatibilidad causal con umbral coseno ≥ 0.20 | Principio 2: Causalidad Obligatoria |
| 3. Soberanía Decisional | Toda decisión estratégica del nodo es irrevocablemente humana | Principio 1: Soberanía Humana |
| 4. Trazabilidad Causal | El nodo mantiene registro auditable de todos los TCAs emitidos y recibidos (append-only) | Principio 2: Causalidad Obligatoria |
| 5a. Resiliencia Operativa *(nueva en v1.1)* | El nodo mantiene operatividad ante fallos parciales sin perder trazabilidad | Principios 1 y 2 |
| 5b. Medición de Impacto *(nueva en v1.1)* | El nodo implementa métricas cuantificables de reducción de Disparidad Causal | Principio 3: Cohesión Social |

---

## Implicación para la tabla de nodos de CORAL.md

La tabla de la Red Fundacional de Pilotos permanece válida como **ejemplo ilustrativo** de aplicación potencial del framework, pero debe incorporar la aclaración de que los nodos reales se definen por las 6 condiciones funcionales anteriores, no por su localización geográfica.

| Nodo geográfico | Dominio | Condiciones funcionales | Estado |
|---|---|---|---|
| Chile — Justicia/Educación | Disparidad socioeconómica | Por verificar según definición v1.1 | Ejemplo ilustrativo |
| Alemania — Salud/Energía | Infraestructura crítica | Por verificar según definición v1.1 | Ejemplo ilustrativo |
| India — Energía/Salud | Escala masiva | Por verificar según definición v1.1 | Ejemplo ilustrativo |
| España — Educación | Subsidiariedad cultural | Por verificar según definición v1.1 | Ejemplo ilustrativo |
| Sudáfrica — Gobernanza | Justicia restaurativa | Por verificar según definición v1.1 | Ejemplo ilustrativo |
# ANEXO C-2 · CORAL.md
**Importancia:** 6/10  
**Tipo de cambio:** Ampliación — nuevo modelo conceptual compatible  
**Fecha:** 2026-02-19  
**Autor:** Claude (Anthropic)  
**Entrada de memoria relacionada:** `tokenomics_causal_diseno_v1`, `entropia_token_causal`, `coral_token_causal`

---

## Tokenomics causales v1 — Diseño del ciclo de vida del TCA

El CORAL.md define el Token Causal Agregado (TCA) como unidad mínima de intercambio e incluye un ejemplo JSON de su estructura. No incluye el modelo de tokenomics que gobierna el ciclo de vida, caducidad y mecanismos de valor. Este diseño fue desarrollado por DeepSeek en Fase 4 y es compatible con los tres Principios Coral.

---

## Principios fundamentales

- Cada token nace de una **acción real** que reduce disparidad causal.
- El token hereda las propiedades de la acción: tipo, duración estimada, impacto, localización.
- No existen tokens genéricos: cada uno es una huella digital única de una acción real.

---

## Tipos de token por acción y caducidad

| Tipo de acción | Caducidad | Renovable | Observación |
|---|---|---|---|
| Diseño / planos | 5-10 años | Sí | Requiere actualización del diseño |
| Adquisición de activos fijos (tierra, edificios) | Perpetuo | N/A | El activo persiste |
| Construcción / infraestructura | 25-50 años | Sí | Renovación con obra de mantenimiento |
| Equipamiento | 5-10 años | Sí | Renovación con reposición de equipo |
| Recurso humano / docencia | 1 año | Sí — bonus por continuidad | Renovación anual con actividad verificada |
| Conocimiento / investigación | 2-5 años | Sí | Renovación con nueva publicación o aplicación |
| Operación / mantenimiento | 1 año | Sí | Renovación con actividad verificada |

---

## Mecanismo de caducidad

```
Token.valor_actual = valor_inicial × (tiempo_restante / vida_util)
```

Al expirar, el valor residual se recicla al ecosistema como incentivo para nuevas acciones en el mismo dominio. La renovación requiere una nueva acción real verificable más un bonus por continuidad que premia la persistencia de la acción en el tiempo.

---

## Mecanismos antifraude

| Mecanismo | Descripción | Efecto |
|---|---|---|
| Movilidad obligatoria | Tokens no aplicados a acciones reales en 90 días pierden valor progresivamente | Desincentiva la acumulación especulativa |
| Saturación progresiva | La concentración de tokens en el mismo sitio o dominio reduce el valor marginal de cada nuevo token | Desincentiva la saturación de un único nodo |
| Verificación multi-IA | Las acciones que generan tokens son verificadas por múltiples agentes IA antes de emitir | Reduce el riesgo de tokens por acción inexistente |
| Proof-of-Uniqueness | Cada identidad en el sistema tiene un identificador único verificado | Impide la duplicación de identidades para multiplicar tokens |

---

## Rol de las IAs

| Rol | Descripción | Principio Coral |
|---|---|---|
| Calcular vida útil estimada | Basada en datos históricos de acciones similares y sus efectos reales | Principio 2: Causalidad Obligatoria |
| Detectar necesidades de renovación | Alertar cuando un token se aproxima a su caducidad con acción sugerida | Principio 3: Cohesión Social |
| Predecir valor futuro | Estimar el impacto causal de acciones antes de que se ejecuten | Principio 2: Causalidad Obligatoria |
| Alertar sobre concentraciones | Identificar acumulaciones anómalas que podrían indicar fraude o sesgo | Principio 3: Cohesión Social |
| Decisión final | Siempre humana — las IAs asesoran, Oscar y la ACH deciden | Principio 1: Soberanía Humana |

---

## Compatibilidad con los Principios Coral

| Principio | Implementación en el tokenomics causal |
|---|---|
| Principio 1: Soberanía Humana | La emisión, renovación o cancelación de un token es siempre decisión humana. Las IAs calculan y proponen; Oscar y la ACH aprueban. |
| Principio 2: Causalidad Obligatoria | Cada token está causalmente vinculado a una acción real verificada. No existen tokens abstractos o especulativos. |
| Principio 3: Cohesión Social | La caducidad dinámica y los mecanismos antifraude garantizan que los tokens circulen hacia donde hay disparidad causal real, no donde hay concentración de poder. |
*Para la implementacion tecnica ver README.md. Para el historial del proceso ver HISTORY.md.*
