# Actual cloud AI demo — 14 November 2026

[Watch the captioned MP4](../../../docs/assets/real-ai-demo.mp4). Duration 71.21 seconds; browser content 1440 × 960 plus a caption band. This is the actual local backend and **qwen3.8-flash**, not mock output. The operator is Codex under Thomas's instruction. All input photos/notes are synthetic or fictional. It is not a human quality review or the required all-member Zoom presentation.

## Recorded path

- Select Osaka, save notes, upload T02's synthetic park image; the city lights up.
- Inspect the current-trip disclosure; explicitly send one cloud request.
- Receive a draft, edit it and explicitly save; reload verifies persistence and one visit.
- Save a separate trip using T05's CLOSED image with an OPEN note; the city now has two visits.
- Send the second cloud request; receive **clarification** about the contradiction. Reload preserves the original note and empty memory text.

Both calls returned HTTP 200 and retain unedited provider messages and usage in the two exchange JSON files. `saved-trips.json` verifies the edited first record and unchanged second memory. These repeat existing scenarios; they do not increase the original independent-case sample size or resolve missing T03/human ratings.

## Recording integrity and limits

119 timestamped browser screenshots cover one 71.208-second run, encoded in chronological order at original elapsed speed with repeated frames. No interval was deliberately cut and no response was substituted. Capture averaged about 1.67 frames/s; the longest capture gap was 3.186 seconds, so this is a low-frame-rate browser capture, not a native high-frame-rate screen recording. English captions were added below the browser area. There is no voiceover. `capture.json` records timings; source-frame SHA-256 values are recorded separately. Original frames remain in the local delivery directory. The first pre-fix take also remains there.

The local MP4 still needs team viewing and a real YouTube upload/link. It does not replace the distinct ≤3-minute four-member Zoom presentation. No Moodle submission has been made.

## Defect discovered and fixed

At city zoom, SVG pin/selection/photo-border widths were expressed in map units and expanded into large white blobs. The marker radius already scaled appropriately, but its stroke did not. `app/styles.css` now uses fixed 2–3 pixel non-scaling strokes. Before/after captures are included. The fixed build was used for this final demo. Existing 22 Node tests passed; maximum city zoom was visually checked. The previous backend 68-test result is unchanged, not a new run claimed here.

Source base: main `6ac0f821dc5b7a49d035f5ceea22bf9e28e2822a` plus the CSS fix. App/backend source hashes are retained in exchange records; the CSS hash is in `SHA256SUMS.json`.
