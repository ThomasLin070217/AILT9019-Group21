# T03 brief-notes Hangzhou fixture

This is Angel's proposed evaluation fixture for the condition **photos plus brief notes**. It tests whether the AI preserves the limited facts supplied by the user without inventing companions, activities, landmarks, dates, weather, emotions, or a fuller story.

## Before adding the photo

This fixture is in the same team repository, under `data/fixtures/T03/`; do **not** create a separate repository.

The intended image is Angel's own Hangzhou travel photograph. Before committing it:

1. Choose an image with no recognisable people, personal documents, hotel/transport identifiers, home address, or other sensitive information.
2. Create a copy with EXIF/GPS metadata removed. Keep the original outside this repository.
3. Save the sanitised copy as `hangzhou-01.jpg` in this folder.
4. Record its SHA-256 checksum and replace the placeholder in `case.json`.
5. Confirm that Angel owns the image and gives permission for this limited private course-repository use.

Do not send the image to a cloud AI provider until the team has agreed on the provider, its retention/privacy terms, and the pre-send notice in the interface.

## Test procedure once the AI path exists

1. Create a trip with the sanitised image and exactly the fictional notes in `case.json`.
2. Trigger AI generation once; save the unedited raw response, model/settings, prompt version and date.
3. Check the output against `known_facts`, `required_memory_facts` and `forbidden_inferences`.
4. Angel and Thomas independently record a pass/fail verdict before any human editing.

No AI result has been collected yet.
