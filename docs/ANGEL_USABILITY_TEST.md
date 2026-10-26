# Angel usability and first-use test record

## Purpose

Check whether a first-time user can understand the current map-and-album
prototype on desktop and mobile. The original observation was made on the
fictional demo; a follow-up check on 26 October 2026 confirmed that the
integrated API-mode interface resolves the reported creation-control problem.

## Completed first-use observation

**Date:** 26 October 2026
**Observer:** Angel

The desktop and mobile sample workflow ran successfully. In the earlier
fictional demo, user feedback was that the controls for adding a new place and
memory were unclear: the only creation control was hidden inside **Try visit
counting** and labelled **Add a sample visit**.

### Follow-up result: resolved in the integrated interface

The current API-mode interface now presents a visible **Add a memory** action.
It opens the real trip form, after which the user can add a photo, edit the
memory, request an AI draft, review it, and save it explicitly. Angel tested
this flow successfully on desktop and mobile on 26 October 2026. The original
usability issue is therefore **resolved for the current interface**. The
fictional `serve.py` demo intentionally retains its separate sample-visit
control and should not be used as evidence for the real creation workflow.

### Recommended product change

This recommendation has been implemented in API mode through the visible
**Add a memory** action. Keep the fictional sample-visit control clearly
separated from the real workflow in documentation and demonstrations.

## Desktop walkthrough checklist

Run `python -m backend`, then open
`http://127.0.0.1:8019/app/?mode=api`.

| Check | Result | Notes |
| --- | --- | --- |
| Choose a city from the map or city list | Pass | Workflow ran successfully. |
| Find the control to add a new memory without help | Pass | **Add a memory** is visible in API mode. |
| Create a trip, add a photo and edit the memory | Pass | Real local album workflow completed. |
| Request, review and save an AI draft | Pass | Draft required review before explicit saving. |
| Reload and confirm the saved record remains | Pass | Local trip, photo and reviewed text persisted. |

## Mobile walkthrough checklist

Use a phone or browser device emulation. Complete the same checks above and note any clipped text, hidden controls, hard-to-tap controls, or confusing navigation.

| Check | Result | Notes |
| --- | --- | --- |
| Map and Album tabs remain usable | Pass | Workflow ran successfully on mobile. |
| City list/search remains usable | Pass | Workflow ran successfully on mobile. |
| Selected-city panel is readable and scrollable | Pass | Workflow ran successfully on mobile. |
| **Add a memory** control can be found and tapped | Pass | The visible real-workflow action resolves the earlier ambiguity. |

## First-use user trial

Ask one person who has not used the prototype to perform this task without guidance:

> Open Osaka, add a sample visit, edit its sample memory text, save it, and reload the page.

Record only non-sensitive observations. Do not use personal photos, travel notes, or account details.

| Date | Tester description | Completed without help? | Where they hesitated | One improvement |
| --- | --- | --- | --- | --- |
| 26 October 2026 | First-time user | Completed the sample workflow | Finding the control to add a new place/memory | Add a visible **Create new memory** button and label the existing control as a fictional demo |
| 26 October 2026 | Follow-up integrated-interface check | Completed the real workflow | No hesitation at creation step | Resolved: visible **Add a memory** action opens the trip form |

## Evidence to attach after testing

- One desktop screenshot or short recording.
- One mobile screenshot or short recording.
- The completed tables above.
- The commit hash tested.
