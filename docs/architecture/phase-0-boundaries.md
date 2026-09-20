# Phase 0 Architecture Boundaries

This document freezes the contracts required by the updated project
instructions before the synthetic campaign loop is expanded.

## Domain boundaries

- `domain/` owns business objects, state transitions, events, and compliance results.
- `policies/` owns deterministic rules. No agent may override a `BLOCK` decision.
- `services/` owns application workflows and calculations.
- `integrations/` owns vendor adapters. Vendor payloads must not leak into domain models.
- `db/` owns persistence and transaction boundaries.
- `apps/api/` owns HTTP transport and API schemas.
- `apps/worker/` owns background job execution.

## Event envelope

Every durable business event uses `DomainEvent` with:

- immutable `event_id`
- typed `event_type`
- `aggregate_id`
- UTC `occurred_at`
- structured `payload`
- optional `correlation_id`
- optional `idempotency_key`

Consumers must use `event_id` or `idempotency_key` to tolerate duplicate
delivery.

## Compliance boundary

`ComplianceResult.is_sendable` is true only for `APPROVE`. `REVIEW` and
`BLOCK` are never sendable. Deterministic rules remain authoritative over
agent recommendations.

## Adapter boundary

Affiliate providers implement `AffiliateNetworkAdapter`:

- `sync_offers`
- `build_tracking_link`
- `sync_conversions`
- `sync_reports`

The mock adapter is the first implementation. Real providers are deferred
until the synthetic loop is proven.

## Phase 0 exit criteria

- contracts are represented in code and covered by tests
- no real affiliate accounts or traffic are required
- the local Phase 1 stack is reproducible with Docker Compose
- secrets remain in ignored runtime files or environment variables