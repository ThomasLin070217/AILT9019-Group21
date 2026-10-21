# AILT9019 Group 21 Team Guide

## Where we are now

Our private repository is ready: [AILT9019-Group21](https://github.com/ThomasLin070217/AILT9019-Group21). The `main` branch contains the project structure, course plan, proposal worksheet, testing template, AI-use log, Friday standup log, milestones, labels, and pull-request template.

The topic is **Travel Memory Map**. Thomas reports that the proposal has been submitted. See the [proposal baseline](../proposal/Travel_Memory_Map_Proposal.docx) and [work allocation](WORK_ALLOCATION.md). The local album, SQLite/photo storage and real course Bailian AI integration are implemented. Five fixed cases have real raw outputs; independent human reviews, teammate-device reproduction and delivery materials remain to be completed. Follow the [21 October per-person TODOs](TEAM_TODOS_2026-10-21.md) and [current acceptance record](PRODUCT_ACCEPTANCE.md). The runnable review branch is published in [draft PR #3](https://github.com/ThomasLin070217/AILT9019-Group21/pull/3); use [team release instructions](TEAM_RELEASE.md) to fetch the correct version. It is not merged into main.

The flow is city selection → photos and optional notes → saved card and lit city, followed by optional user-triggered AI writing. Repeat trips get separate cards, and saved-trip counts determine brightness. The first version is local with a cloud AI API and preset cities in mainland China, Hong Kong, Macau, Taiwan and Japan.

## Current deadlines

The latest course overview says the proposal draft is due on **30 September 2026**, followed by the revised proposal on **10 October**, the mid-term check on **26 October**, and final deliverables on **20 November**. Moodle remains the authoritative source if it announces a change.

## What every member should do now

1. Accept your invitation if needed and clone the repository.
2. Read the proposal and `docs/WORK_ALLOCATION.md`.
3. Check the current TODOs, first deliverable and reviewer; raise availability conflicts immediately.
4. Work from the same shared commit, reproduce the integrated workflow, and record concrete failures.
5. Complete assigned independent case reviews and record AI assistance and actual checks.

## How to work in the repository

```bash
git clone git@github.com:ThomasLin070217/AILT9019-Group21.git
cd AILT9019-Group21
git checkout -b short-description
```

Make a small, tested change. Commit it with a meaningful message, push the branch, and open a pull request. Use the pull-request template to state what changed, how it was tested, and any limitation. Never commit API keys, `.env` files, personal data, passwords, screenshots containing private information, or unlicensed datasets.

## Proposal requirements

The proposal must stay anonymous. Do not include the team number, names, student IDs, emails, or other personal information in the content or filename.

It needs six sections: Background, Project pipeline, Evaluation and test, Distribution and accessibility, Ethics and risks, and Checkpoints. The largest peer-review marks are for a specific end-to-end pipeline and measurable evaluation. Add a simple pipeline figure, a small timeline, a fixed test set, a success threshold, and at least one safe-refusal or fail-safe case.

## What the final project must show

We need a working AI application, a genuine domain customisation, a reproducible GitHub repository, a project webpage, a three-minute presentation plus real demo, and a report of no more than five pages with Ethics and AI-use disclosure. A demo must show one successful run and one limitation or failure case.

During Weeks 5–10, we post a three-line Ed standup every Friday. We also need one team consultation with the assigned consultant during Weeks 4–6 or Week 8, ideally before the revised proposal.

## Course account access

Checked on 30 September: the repository is private and a Write invitation for `AILT9019` is pending. Thomas previously authorised Write because the personal repository did not support the requested Read collaborator role. This records the actual setting, not course approval of the difference. See [access status](COURSE_ACCOUNT_ACCESS.md). No permissions were changed when publishing this plan.
