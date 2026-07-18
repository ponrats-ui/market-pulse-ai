# 21 Version History

## Table of Contents

- [Purpose](#purpose)
- [Version Timeline](#version-timeline)
- [Major Milestones](#major-milestones)
- [Accepted Founder Specifications](#accepted-founder-specifications)
- [Release History](#release-history)
- [Branch History](#branch-history)
- [Current Production](#current-production)
- [Future Roadmap](#future-roadmap)
- [Known Limitations](#known-limitations)
- [Related Documents](#related-documents)

## Purpose

This document preserves the historical path of Market Pulse AI so future engineers understand why the current release branch contains many founder-led phases.

## Version Timeline

Sprint 0:

- React/Vite frontend
- FastAPI backend
- yfinance foundation

Sprint 1:

- normalized provider data layer
- quote and history endpoints
- cache behavior

Sprint 2:

- Thai/English localization
- AI Committee and Chief AI dashboard surfaces

Sprint 3 and RC phases:

- research terminal features
- real-data policy
- provider abstractions
- portfolio and compare foundations
- premium and alert architecture without payment activation

FS series:

- FS-100 investment platform experience
- FS-200 professional chart engine
- FS-300 UI restoration
- FS-300A density optimization
- FS-300B visual excellence
- FS-300B.1 batch quote abort lifecycle

Documentation Freeze:

- FS-DOC-100 knowledge base
- FS-DOC-200 engineering handbook

## Major Milestones

- Open-source governance added.
- Render backend deployment configuration added.
- Cloudflare Pages frontend configuration added.
- Real Data / Zero Mock policy established.
- Founder UI Freeze accepted.
- Release branch `release/v1.0.0-rc1` created.

## Accepted Founder Specifications

Accepted chain includes:

- FS-100
- FS-200
- FS-300
- FS-300A
- FS-300B
- FS-300B.1
- FS-DOC-100
- FS-DOC-200

## Release History

Current release candidate:

- Branch: `release/v1.0.0-rc1`
- Source: accepted `develop`
- UI Freeze: accepted
- Deployment: not performed by this document

## Branch History

Important branches:

- `develop`: accepted integration branch
- `release/v1.0.0-rc1`: release candidate preparation
- `fix/fs-300b1-batch-quote-abort`: accepted final UI freeze chain source

## Current Production

This document describes the release-candidate repository state. It does not claim production deployment.

## Future Roadmap

- add Git tag history after approved releases
- add production deployment dates
- add changelog alignment for each release

## Known Limitations

- Some older sprint names are summarized rather than fully expanded.
- Production URLs and tags are recorded elsewhere after deployment approval.

## Related Documents

- [05 Release Engineering](05_RELEASE_ENGINEERING.md)
- [Founder UI Freeze Acceptance](FOUNDER-UI-FREEZE-ACCEPTANCE.md)
- [CHANGELOG](../CHANGELOG.md)

