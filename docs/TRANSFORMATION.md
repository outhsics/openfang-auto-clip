# Transformation Guide

This guide describes the current transformation paths in OpenFang Auto Clip and the boundary between shipped features and roadmap ideas.

## Current State

| Level | Status | Summary |
|------|--------|---------|
| 1 | Working | Local FFmpeg-based visual remix |
| 2 | Scaffolded | Script-regeneration path is not implemented end to end |
| 3 | Scaffolded | Complete recreation is still a concept path |

## Level 1

Level 1 is the main working transformation path today.

It currently does things such as:

- mirror the source
- alter speed and timing
- adjust color and contrast
- add additional FFmpeg-based visual changes

Use it when you want:

- a fast local remix pass
- a reproducible demo path
- a lower-risk workflow than direct reposting

Example:

```bash
./auto_clip.sh "URL" --transform 1
```

Important limits:

- it does not make legal review unnecessary
- it does not remove trademark or character-IP risk automatically
- it should not be described as guaranteed copyright-safe output

## Level 2

Level 2 is a roadmap path for script regeneration.

The intended flow is:

1. transcribe source material
2. extract key concepts
3. write a new script
4. generate new voiceover
5. rebuild visuals around the new script

Current status:

- the CLI exposes the level
- the implementation returns `not_implemented`
- treat it as planned work, not a shipped capability

## Level 3

Level 3 is a roadmap path for full recreation.

The intended flow is:

1. analyze structure and goals of the source material
2. generate an original script
3. generate new visuals, audio, and pacing
4. assemble a fully independent asset

Current status:

- concept only
- not ready for production claims
- not ready for commercial promises

## Which Path To Use

- local evaluation: Level 1
- product demos: Level 1 plus the synthetic benchmark
- roadmap conversations: Level 2 and Level 3

## Compliance Guidance

- treat this repository as a risk-reduction tool, not a legal shield
- check platform rules before publishing
- get legal advice for commercial or high-risk use
- read [DISCLAIMER.md](../DISCLAIMER.md) before making external claims
