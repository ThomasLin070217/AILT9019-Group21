# Group 21 final recording kit

Verified on Moodle on 14 November 2026. **Two separate YouTube links are required.** Use Unlisted. The presentation must be recorded in Zoom, at most 3 minutes, with all four members speaking and each speaker's full name visible. Faces are optional. The genuine system demo has no time limit. Neither video file belongs in the Moodle ZIP.

## Presentation script

Rehearse at a natural pace. Target 2:40–2:50, leaving time for speaker handovers. Each person uses their own voice. Replace any changed results only after evidence is recorded. This script describes the verified 14 November state, not a claim that the remaining reviews are finished.

**0:00–0:40 — Yunian Lin (Thomas)**

> We are Group 21, and our project is Travel Memory Map. After travelling, students may have many photos but little organised context. Our app connects each completed trip to a city and a separate memory card. Saving another visit creates a new card and brightens that city's area. I coordinated the map, integration and delivery, using coding assistance and recorded checks. The goal is an easy way to revisit memories; we have not yet measured whether it improves long-term recall.

**0:40–1:20 — Ho Yeung Seto (Owen)**

> I worked on the local backend and storage. The browser connects to FastAPI, with SQLite for trips and local files for photos. Image uploads are validated and re-encoded to remove metadata. The core album works without an AI key. For optional AI, the app first shows what will be sent. Only the current trip goes to the provider. Returned text stays an editable draft until the user saves it, so a failed request cannot silently replace the original memory.

**1:20–2:00 — Xinyue Li (Angel)**

> My contributions include quick-start instructions, first-use observations, a brief-note photo fixture and an adapter revision. The workflow is choose a city, save a trip, add photos and optionally generate a memory. We made the creation action visible rather than hiding it in the sample demo. The system distinguishes an ordinary draft from a clarification or refusal. We also separate permission to publish a photo in GitHub from permission to send that photo to a cloud model.

**2:00–2:45 — Qingyang Lin**

> I prepared unclear-photo and conflicting-input materials and evaluation documentation. The integrated Qwen run now has six live outputs with the expected response types, plus sixty-eight Python and twenty-two Node checks. Those six results are not a human accuracy score. One original case still awaits cloud permission, and independent content ratings remain pending. A real failure was prose returned instead of JSON; model-specific JSON mode fixed the reproduced case while validation remained strict. Our main lesson is to preserve evidence, acknowledge uncertainty and keep users in control of saved memories.

## Zoom checklist

- Display names: **Yunian Lin**, **Ho Yeung Seto**, **Xinyue Li**, **Qingyang Lin**. Check each appears in the actual recording while speaking, not only in the live Zoom window.
- Record one continuous presentation in Zoom; show the app or a simple pipeline page while explaining. Test the chosen Zoom recording layout first.
- Keep the final file at or below 3:00. Check audio, readability, visible names and all four speaking contributions. Do not substitute AI voices for members.
- Upload to YouTube as Unlisted. Verify access while signed out. Copy its URL into `submission_links.txt` and the report identification block.

## Separate real demo recording

Owner: Angel; Thomas supplies the integrated build, evidence and this sequence. Aim for 3–5 minutes of readable, continuous execution, not a fast montage. Use only synthetic fixtures and fictional notes. Do not record terminal environment variables, keys, notifications or personal albums.

1. Pull the chosen main commit and record its short SHA. Start the real local backend in API mode, with a valid server-side Qwen configuration. Use `/app/?mode=api&map=local` for an offline map; the AI call still uses the cloud.
2. Start in an empty isolated album. Choose Osaka, save a fictional trip with notes such as “Two days; it rained on the first day.” Upload the synthetic T01 images or T02 park image. Clearly label the input as fictional/synthetic.
3. Select **Write with AI**. Show the current-trip disclosure, Cancel once, then reopen and explicitly confirm. Wait for the real response. Do not replace or crop out the processing step to imply a fabricated call was live.
4. Show the editable draft and warnings. Change its title, explicitly save, and reload. Demonstrate that the saved card and photo persist.
5. Add a second trip to Osaka. Show two distinct cards and the updated visit count/brightness. Explain that editing the first card did not create an extra visit.
6. Show one real boundary case: create a new isolated test trip using T05's closed-sign image and conflicting “open” notes. Request AI and show the actual clarification if it occurs. If it differs from expectation, keep and explain the observed result; do not manufacture the expected response. Alternatively record the missing-key failure with a deliberately unconfigured backend and show the saved card remains unchanged.
7. Briefly open the retained live-results page: distinguish 6/6 response types, 4/5 original cases run, and pending human ratings. Mention 19 approximate city areas, local-only storage and no travel verification.
8. Show no confidential data. Add accurate captions or narration. Upload this demo separately to YouTube as Unlisted and verify signed-out playback.

The school key batch expires on **19 November**. Make any permitted live recording before expiry or obtain renewed access. No need to rerun all cases just to record; make only the calls needed and keep requests sequential.

## Required final links

Use actual accessible URLs, not placeholder text. Report and links file must agree. Do not copy the existing 13-second webpage clip into the final slot and call it the completed presentation: it has no four-member Zoom speaking record and predates the real AI run.
