# Consolidated Independent Team Reviews
Owner: Qingyang
Purpose: Aggregate independent test observations from every team‑member, deduplicate and assign priority.

> Midterm note：Full AI runtime results [PENDING‑TEAM‑AI‑RUN]. Partial observations are collected from map‑only demo work. AI‑related findings will be appended once model outputs are available.

## Review sources
- Thomas: Map / city‑visit‑count module testing
- Angel: Desktop‑mobile workflow & user trial observation
- Owen: Fresh‑install, persistence, backup‑restore, backend observation
- Qingyang: AI fixture preparation, privacy assessment

Issue categories：
1. AI factual / hallucination risk
2. UI & interaction defects
3. Deployment & installation problems
4. Privacy & security risks
5. Minor enhancement / wishlist

| Priority | Observation | Reporter |
|---|---|---|
### 1. AI factual / hallucination risk
| High | AI test outputs not yet generated; fixtures prepared waiting for backend‑AI handoff | Qingyang |

### 2. UI & interaction defects (map demo)
| Medium | Demo trips stored in browser memory, lost on hard refresh (expected demo limitation) | Thomas |

###3. Deployment & installation problems
| Low | Offline local map works out‑of‑box; Google Maps requires separate .env.maps.local key file | Owen |

###4. Privacy & security risks
| High | AI request payload inspection cannot be performed without live AI calls | Qingyang, Owen |

###5. Minor enhancement / wishlist
| Low | Add better keyboard navigation hints for map panel | Angel |

## Summary & action recommendations
1. High‑priority items must be addressed before final submission.
2. Medium items resolve in next two‑week sprint.
3. Low‑priority polish items may be deferred for v1 scope control.

### Mid‑term scope decision
Keep: map‑album workflow, full T01‑T05 fixture suite, privacy payload inspection plan.
Deferred: none at mid‑term; polish improvements subject to remaining project time.
