# Travel Memory Map

## Platform

web

## Users and purpose

Students recording completed trips as city-based memories. Select a city, supply photos/date/notes, save an independent trip and optionally request a cloud AI draft. Repeated visits are separate cards with exact counts and brightness tiers.

## Implementation

Vanilla browser JavaScript and a loopback Python server. SQLite and metadata-free local photo copies persist real albums independently of the fictional browser demo. Creation, text/date/memory editing, photo replacement, confirmed deletion, ZIP backup/merge restore, PNG export, date filtering and reduced-motion-aware marker feedback are implemented.

OpenAI-compatible Responses vision integration is implemented: disclose current-trip payload, explicit send, editable unsaved draft, explicit reviewed save, clarification and safe failure. The course Bailian qwen3.8-flash API is configured privately. Five frozen licensed/synthetic cases have real outputs, and the real browser draft/edit/save workflow passes. Final response-type checks match all five cases, while two independent human factual reviews remain pending. Earlier failed calls are preserved alongside the final run.

## Boundaries

Single-user local application; 19 preset cities. No 3D maps, navigation, social sharing, automatic classification or cloud sync. No geographic visit verification. Optional Google Maps is separate from album/AI. A model can still hallucinate, so review each draft. Acceptance evidence and limits: docs/PRODUCT_ACCEPTANCE.md.
