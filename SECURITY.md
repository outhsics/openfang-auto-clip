# Security Policy

## Supported Versions

The project is still pre-1.0. Security fixes are currently expected only on:

- the latest commit on `main`
- the latest tagged release

Older tags may not receive fixes.

## Reporting a Vulnerability

Please do not open a public issue for a suspected security problem.

Use one of these paths:

1. GitHub Security Advisories for private reporting, if enabled in the repository
2. A maintainer contact method listed in the repository profile

When reporting, include:

- affected version or commit
- impact summary
- reproduction steps or proof of concept
- any suggested mitigation

## Scope Notes

The main security-sensitive areas in this repository are:

- shell command execution around local media processing
- path handling in the local web manager
- secrets management for local API keys
- release automation and generated artifacts
