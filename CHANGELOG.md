# Changelog

Changes that affect operators of the worker. How to write entries and cut a release: [docs/releasing.md](docs/releasing.md).

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The worker registers its ingestors, the buckets it reads and its versions with the API (`PUT /workers/{hostname}`), renews the registration every `heartbeat_seconds` the API returns, and deregisters on shutdown. Needs crucible-api with worker registration; older APIs are retried quietly. The API key must belong to a service account.
- A job for an ingestor this worker lacks, but another live worker offers, is returned to the queue after 30 s instead of failing.

### Changed

- crucible-ingestion 0.3.5, which lists each ingestor's capabilities for the registration.

## [0.4.2] - 2026-11-24

RGA/TEY batch zip ingestion on opaque storage paths. crucible-ingestion 0.3.4.

### Fixed

- crucible-ingestion 0.3.4: `RgaTeyBatchIngestor` extracts nested batch folders using `file_name` when `file_to_upload` is an opaque storage path.

## [0.4.1] - 2026-11-24

Attolight cathodoluminescence and SUR ingestors. crucible-ingestion 0.3.3.

### Added

- `AttolightCLIngestor` for Attolight cathodoluminescence `.xml` and `.txt` acquisitions.
- `SurIngestor` for `.sur` surface files.

### Changed

- crucible-ingestion 0.3.3: ingested datasets no longer send a `size`; Attolight child datasets take the parent's owner.

## [0.4.0] - 2026-11-18

Crucible API 4.0, Kratos XPS ingestor, and Nirvana holder splitting. crucible-ingestion 0.3.2.

### Breaking changes

- crucible-ingestion 0.3.2 requires Crucible API 4.0 (`nano-crucible>=4.0.1`).

### Added

- `KratosXpsIngestor` for B30 Kratos `.kal` XPS spectra.
- Server-side per-position child dataset and thumbnail splitting in `NirvanaMultiPosLineScanIngestor` and `NirvanaMultiPosSpecRunIngestor` for holder overrides.

## [0.3.2] - 2026-11-17

crucible-ingestion 0.2.1.

### Changed

- crucible-ingestion 0.2.1: Nirvana child datasets no longer send `instrument_name`, which API 4.0 refuses.

## [0.3.1] - 2026-11-16

Numeric image user. crucible-ingestion 0.2.0.

### Changed

- The image sets its user as `10001:10001`, so `runAsNonRoot` works without `runAsUser`.

## [0.3.0] - 2026-11-13

Direct reads from GCS or S3, no rerun of completed jobs, and a read-only root filesystem. crucible-ingestion 0.2.0.

### Added

- Direct reads from GCS or an S3-compatible store when no mount covers the bucket: `STORAGE_BACKEND`, `STORAGE_BUCKETS`, `S3_ENDPOINT_URL`, `S3_REGION`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`. Files download to `WORK_DIR` (default `/tmp/work`).
- A redelivered job whose request is already `complete` is acknowledged without running.

### Changed

- `STORAGE_EXISTS_CHECK=gcs` uses obstore; `google-cloud-storage` and `google-auth` are no longer direct dependencies.
- The image runs on a read-only root filesystem; `/tmp` must be writable.

## [0.2.0] - 2026-11-13

First release as `crucible-ingestion-worker`: generic configuration, threaded jobs, graceful shutdown, published to ghcr. crucible-ingestion 0.2.0.

### Breaking changes

- `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_VHOST` and `QUEUE` replace `RMQ_HOST`, `RMQ_PORT`, `RMQ_ROUTING_SUFFIX`, `SECRET_STORE` and `GCS_CLIENT_ID`.
- Secrets `CRUCIBLE_API_KEY` and `RABBITMQ_PASSWORD` are given exactly one way: the value, `<NAME>_FILE` or `<NAME>_VERSION` (Secret Manager).
- `STORAGE_MOUNTS` replaces the built-in Foundry mounts.
- Runs as uid 10001.
- crucible-ingestion comes from PyPI, locked in `uv.lock`.

### Added

- Jobs run in a thread, so long jobs no longer drop the RabbitMQ connection.
- `PREFETCH_COUNT` (default 1), `SHUTDOWN_TIMEOUT` (default 25 s), `HEALTH_FILE` and `HEALTH_INTERVAL`.
- Unreadable or crashing messages move to the failed queue.
- Images on ghcr from version tags, with the crucible-ingestion version in the label `gov.lbl.crucible.ingestion.version`; `CRUCIBLE_INGESTION_SPEC` builds against another crucible-ingestion.

[Unreleased]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/compare/v0.4.2...HEAD
[0.4.2]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/compare/v0.3.2...v0.4.0
[0.3.2]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/MolecularFoundryCrucible/crucible-ingestion-worker/releases/tag/v0.2.0
