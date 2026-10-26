# Angel usability and first-use test record

## Purpose

Check whether a first-time user can understand the current map-and-album prototype on desktop and mobile. This record covers the existing fictional demo only; it does not claim that photo upload, backend storage, or AI generation has been tested.

## Completed first-use observation

**Date:** 26 October 2026
**Observer:** Angel

The desktop and mobile sample workflow ran successfully. User feedback was that the buttons for adding a new place and memory were unclear. On the selected-city panel, the only creation control is hidden inside **Try visit counting** and is labelled **Add a sample visit**. A new user could reasonably expect a visible "Create new memory" action, but that action does not exist in the current prototype.

### Recommended product change

When the real trip workflow is implemented, add a visible primary action such as **Create new memory** in the selected-city panel. It should open a form with city, photos, optional notes, and save controls. Until that exists, clearly label the current hidden control as a fictional map demo rather than a real creation feature.

## Desktop walkthrough checklist

Run the prototype with `python serve.py`, then open `http://127.0.0.1:8019/app/?map=local`.

| Check | Result | Notes |
| --- | --- | --- |
| Choose Osaka from the map or city list | Pass | Workflow ran successfully. |
| Find the sample-visit control without help | Issue found | User feedback: the control for adding a new place/memory was unclear. |
| Add a sample visit and see the count become 3 | Pass | Workflow ran successfully. |
| Edit sample text without changing the count | Pass | Workflow ran successfully. |
| Reload and confirm the demo record remains | Pass | Workflow ran successfully. |
| Understand that the app is a fictional demo, not real memory creation | Issue found | A visible creation action and clearer demo label are needed. |

## Mobile walkthrough checklist

Use a phone or browser device emulation. Complete the same checks above and note any clipped text, hidden controls, hard-to-tap controls, or confusing navigation.

| Check | Result | Notes |
| --- | --- | --- |
| Map and Album tabs remain usable | Pass | Workflow ran successfully on mobile. |
| City list/search remains usable | Pass | Workflow ran successfully on mobile. |
| Selected-city panel is readable and scrollable | Pass | Workflow ran successfully on mobile. |
| Demo creation control can be found and tapped | Issue found | The control is technically usable but its purpose is unclear. |

## First-use user trial

Ask one person who has not used the prototype to perform this task without guidance:

> Open Osaka, add a sample visit, edit its sample memory text, save it, and reload the page.

Record only non-sensitive observations. Do not use personal photos, travel notes, or account details.

| Date | Tester description | Completed without help? | Where they hesitated | One improvement |
| --- | --- | --- | --- | --- |
| 26 October 2026 | First-time user | Completed the sample workflow | Finding the control to add a new place/memory | Add a visible **Create new memory** button and label the existing control as a fictional demo |

## Evidence to attach after testing

- One desktop screenshot or short recording.
- One mobile screenshot or short recording.
- The completed tables above.
- The commit hash tested.
