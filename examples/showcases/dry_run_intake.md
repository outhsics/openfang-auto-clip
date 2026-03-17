# Showcase: Dry-Run Intake Flow

## Goal

Show the safest way to evaluate the operator workflow before downloading or transforming any real media.

## Command

```bash
./auto_clip.sh --doctor
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --dry-run
```

## What This Proves

- required local tools are visible on PATH
- output directories resolve correctly
- the repo can generate a processing plan before spending time or API budget

## Why It Matters

- reduces demo risk during onboarding
- gives operators a clear preflight step
- is a better first-run story than immediately telling users to download a real video

## Best Use

- installation guides
- operator onboarding
- support replies in Discussions
