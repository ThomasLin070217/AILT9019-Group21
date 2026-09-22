# AILT9019 Group 21 Team Guide

## Where we are now

Our private repository is ready: [AILT9019-Group21](https://github.com/ThomasLin070217/AILT9019-Group21). The `main` branch contains the project structure, course plan, proposal worksheet, testing template, AI-use log, Friday standup log, milestones, labels, and pull-request template.

The project topic has not been chosen yet. Do not start building a large application before we agree on one user, one task, one data source, and one minimum working workflow.

## Current deadlines

The latest course overview says the proposal draft is due on **30 September 2026**, followed by the revised proposal on **10 October**, the mid-term check on **26 October**, and final deliverables on **20 November**. Moodle remains the authoritative source if it announces a change.

## What every member should do now

1. Accept the GitHub invitation and clone the repository.
2. Read `docs/COURSE_PLAN.md` and `proposal/PROPOSAL_WORKSHEET.md` before the next discussion.
3. Bring one focused project idea. It must name one primary user, one concrete task, a realistic data source, and a safe boundary.
4. At the meeting, agree on the must-have version only. Put optional features in the should-have column.
5. Help complete one part of the proposal worksheet, then turn it into the official anonymous Moodle template.

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

## Open item: course-account access

The course requires `ailt9019hku@gmail.com` to receive Read access to the private repository. GitHub resolved it as `AILT9019`, but a personal GitHub repository cannot assign Read to an outside collaborator through GitHub's API: it only offers Write. The incorrect Write invitation was withdrawn.

We need the course team to confirm whether Write is acceptable for its checker account, or tell us to transfer the repository to a team GitHub organization where Read access is available. Do not add the course account with Write until that is resolved.
