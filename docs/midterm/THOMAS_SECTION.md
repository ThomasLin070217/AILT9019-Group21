# Thomas — Problem and integrated workflow

Prepared on 21 October 2026 with AI assistance. This is a draft for Thomas to verify and present; it does not claim that Thomas personally wrote or independently tested every implementation detail.

## Written section

Travel photos often remain scattered across folders, while a conventional album gives little sense of which cities someone has visited or how repeated trips relate to one another. Travel Memory Map connects each saved trip to a preset city, allowing students to keep photographs, dates and short notes together and revisit them through a map or album view.

The application runs locally in a browser with a Python server. A user selects a city, uploads photographs and saves a trip. SQLite stores the record, while processed photo copies remain in a separate local directory. Each distinct saved trip ID counts as one visit. Repeated visits therefore produce separate cards, and city markers change brightness at one, two to three, and four or more visits. Editing a title, replacing photographs or saving reviewed text updates the existing trip instead of creating another visit.

AI writing is optional. After reviewing a disclosure, the user can send only the current trip's photo copies, city, date and notes to the course-sponsored Bailian qwen3.8-flash model. The returned title and memory remain editable drafts until the user explicitly saves them. Unclear or contradictory inputs can produce clarification questions, and provider failures leave the local album intact.

Integration checks cover count transitions, persistence, safe retries and draft handling. Five real model cases have recorded outputs, but response-type matching does not establish factual accuracy. Independent human reviews, including resolving a completeness issue in the photo-only case, remain part of acceptance.

## Approximately 45-second speaking script

Travel photos are easy to collect but harder to revisit as separate trips. Our app connects a local photo album to a city map. Users choose a city, add photos and notes, and save one trip. Repeat visits get separate cards and brighten the marker. Editing a trip keeps the visit count unchanged. AI is optional: after checking what will be sent, users can request a draft, edit it and explicitly save it. The local album works without AI. We have recorded real model outputs, but factual quality still needs human review. One photo-only result also missed a required detail.

## Screen cues

- Start with the selected city and its saved cards.
- Show separate visits and the printed count beside the marker; do not rely on colour alone.
- Mention that the later demonstration uses permitted example photos and fictional trip notes.
- Hand over to Angel at 00:45. Do not imply that the model wrote the manually authored map-demo text.
