# Angel usability and first-use test record

## Purpose

Check whether a first-time user can understand the current map-and-album prototype on desktop and mobile. This record covers the existing fictional demo only; it does not claim that photo upload, backend storage, or AI generation has been tested.

## Initial interface observation

**Date:** 26 October 2026
**Observer:** Angel

The map and album presentation is visually polished, but creating a new memory is unclear. On the selected-city panel, the only creation control is hidden inside **Try visit counting** and is labelled **Add a sample visit**. A new user could reasonably expect a visible "Create new memory" action, but that action does not exist in the current prototype.

### Recommended product change

When the real trip workflow is implemented, add a visible primary action such as **Create new memory** in the selected-city panel. It should open a form with city, photos, optional notes, and save controls. Until that exists, clearly label the current hidden control as a fictional map demo rather than a real creation feature.

## Desktop walkthrough checklist

Run the prototype with `python serve.py`, then open `http://127.0.0.1:8019/app/?map=local`.

| Check | Result | Notes |
| --- | --- | --- |
| Choose Osaka from the map or city list | Pending | |
| Find the sample-visit control without help | Pending | |
| Add a sample visit and see the count become 3 | Pending | |
| Edit sample text without changing the count | Pending | |
| Reload and confirm the demo record remains | Pending | |
| Understand that the app is a fictional demo, not real memory creation | Pending | |

## Mobile walkthrough checklist

Use a phone or browser device emulation. Complete the same checks above and note any clipped text, hidden controls, hard-to-tap controls, or confusing navigation.

| Check | Result | Notes |
| --- | --- | --- |
| Map and Album tabs remain usable | Pending | |
| City list/search remains usable | Pending | |
| Selected-city panel is readable and scrollable | Pending | |
| Demo creation control can be found and tapped | Pending | |

## First-use user trial

Ask one person who has not used the prototype to perform this task without guidance:

> Open Osaka, add a sample visit, edit its sample memory text, save it, and reload the page.

Record only non-sensitive observations. Do not use personal photos, travel notes, or account details.

| Date | Tester description | Completed without help? | Where they hesitated | One improvement |
| --- | --- | --- | --- | --- |
| Pending | | | | |

## Evidence to attach after testing

- One desktop screenshot or short recording.
- One mobile screenshot or short recording.
- The completed tables above.
- The commit hash tested.
