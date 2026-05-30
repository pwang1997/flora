# Change: Reset to supervised skeleton

## Why
The project should restart from a minimal foundation so each product feature can be discussed, specified, and implemented under direct supervision.

## What Changes
- Remove the previously scaffolded MVP feature behavior.
- Keep only standalone service folders, OpenSpec project context, health-only core API, idle worker, and placeholder UI.
- Require future feature work to start with an OpenSpec change before implementation.

## Impact
- Affected specs: project-skeleton
- Affected code: `flora-core`, `flora-worker`, `flora-ui`, local runtime docs
