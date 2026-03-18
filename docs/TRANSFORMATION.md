# Transformation Guide

This guide describes the current transformation paths in OpenFang Auto Clip and the boundary between shipped features and roadmap ideas.

## Current State

| Level | Status | Summary |
|------|--------|---------|
| 1 | Working | Local FFmpeg-based visual remix |
| 2 | Partial | Transcript-to-script package is shipped; full rebuilt output is not |
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

Level 2 now ships a first milestone for script regeneration.

The current local milestone is:

1. read a transcript or subtitle file
2. extract source beats
3. draft a fresh narration structure
4. write a JSON + Markdown script package for operator review

Example:

```bash
./auto_clip.sh "URL" --transform 2 --transcript path/to/source.srt
```

Current status:

- the CLI can generate a transcript-to-script package today
- the package includes source outline, narration draft, and production checklist
- voiceover synthesis, rebuilt visuals, and final video assembly are still manual follow-up work

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
- early script-regeneration work: Level 2
- roadmap conversations: Level 3

## Compliance Guidance

- treat this repository as a risk-reduction tool, not a legal shield
- check platform rules before publishing
- get legal advice for commercial or high-risk use
- read [DISCLAIMER.md](../DISCLAIMER.md) before making external claims
