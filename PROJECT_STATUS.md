# Project Status

Updated: 2026-10-20 — tracked against `REAL_MONEY_STRATEGY.md`.

## Where we are

**Gate 1 (software works in simulation): reached.** The full MVP loop runs end-to-end
on persisted data with 56 passing tests:
Offer → Audience → Campaign → Compliance → Simulated send → Click → Conversion →
Commission → Revenue/cost → Optimizer recommendation → Dashboard.

**Gates 2–6 are blocked on non-engineering work** (see "Pending — needs you" below).

## MVP completion (Phases 2, 4–9 + §14)

- **Phase 2:** offers have a unique key on `(network_id, external_offer_id)`; seeding
  upserts on it. Data confirmed to survive a Postgres restart.
- **Phase 4:** campaigns carry a disclosure, A/B subject variants, and an affiliate
  tracking URL whose `sub_id` is the campaign id (for conversion reconciliation).
- **Phase 5:** `policies/send_rules.py` `validate_send` is the final gate: offer/audience/
  content checks plus GEO match, disclosure, sender identity (name, email, postal
  address), unsubscribe link, tracking URL, duplicate-send, frequency cap, and content
  checks on every subject variant. `email_approval_required` offers stay in `REVIEW`
  and never send. Kill switch unchanged.
- **Phase 6:** simulator adds bounces, unsubscribes, and complaints; every result has
  `is_simulated: true`.
- **Phase 7:** `calculate_rates` adds CTR, CVR, EPC, bounce/unsubscribe/complaint rates
  and the primary KPI, net contribution per 1,000 eligible recipients.
- **Phase 8:** optimizer adds `REDUCE` (high unsubscribes) and `PAUSE` on complaint
  rate ≥ 0.1%; runs in recommendation-only mode (`applied: false`).
- **Phase 9:** dashboard shows a SIMULATED DATA badge, kill-switch state, optimizer
  mode, the KPIs above, recommendations with reasons, and blocked campaigns with reasons.
- **§14:** `is_simulated` on offers, audiences, subscribers (defaults to true, so
  unflagged rows are treated as test data); all engine output labeled
  `environment: simulation`.

## Real inbox test (owner-controlled)

Real emails can go to inboxes you own, and only those:

- `TEST_RECIPIENTS` allowlist in `.env`; anything not listed never receives mail.
- `make send-test` = dry run (default); `make send-test-live` = send via SMTP
  (`SMTP_*` in `.env`; Gmail works with an app password).
- Every send passes the full compliance gate, is recorded once per
  (campaign, subscriber) in `events`, and each run moves to the next untried offer.
- Links: `/r/{campaign}/{subscriber}` records a real click and redirects to the mock
  network's offer page, which records a **test** conversion once per click
  (not real money). `/unsubscribe` needs a confirm click, then suppresses the address.
- Results: `GET /api/analytics/real` and the dashboard's "Real test sends" section,
  kept apart from simulated numbers. Simulation never loads real records.

## Real offers and real earnings

- `make add-offer ARGS='--name ... --network ... --payout ... --url "https://...{sub_id}" [--geo ALL] [--email-allowed]'`
  registers your real affiliate link. `{sub_id}` is replaced per click with a short
  click id. Without `--email-allowed` (confirm the program terms first) sends stay blocked.
  Real offers take priority over mock offers in `make send-test(-live)`.
- `make import-commissions ARGS='--network ... --csv report.csv'` imports the network's
  commission report: columns auto-detected, statuses normalized to
  PENDING/APPROVED/REJECTED/REVERSED/PAID (unknown → PENDING), re-imports update in place,
  negative refund rows are netted. Matched to clicks via the click id.
- `commissions` table stores exact decimals. Dashboard "Real earnings" counts only
  APPROVED + PAID as earned. Real money only comes from purchases by people other than
  you; self-clicks/self-purchases are prohibited by networks.

## Opens, API sync, and AI copy

- **Open tracking:** each real email carries a 1x1 pixel (`/o/{campaign}/{subscriber}.gif`);
  opens and unique openers show in `/api/analytics/real` and the dashboard. Approximate by
  nature (Apple Mail preloads images; some clients block them). `TRACK_OPENS=false` disables.
- **ClickBank API sync:** `make sync-commissions` pulls affiliate orders from ClickBank's
  Orders API (`CLICKBANK_API_KEY`, role `api_order_read`) into the same commissions ledger
  as CSV imports; paginated, refunds netted, safe to schedule daily. Field names verified
  against ClickBank's published schema; error paths verified against the live API.
- **AI copy:** with `LLM_PROVIDER=ollama`, real sends get subjects/preheader/body/CTA from
  the local model (default `qwen3.5:9b`, $0). Code adds disclosure, unsubscribe and all links;
  invalid, link-containing or non-compliant output, or Ollama being down, falls back to the
  template. Simulation keeps templates (fast, deterministic).

## Pending — engineering (needed before a real pilot, not before)

- API sync for networks beyond ClickBank (Impact, CJ, Awin…) as you join them.
- Opt-in signup endpoint (unsubscribe exists).
- Signed unsubscribe/click tokens and auth on API/dashboard before public exposure.
- Offer terms "last checked" date; transactional ESP (SES/Resend) instead of Gmail
  SMTP once sending beyond your own inboxes.

## Pending — needs you (cannot be automated)

- Pick one niche and a legitimate audience route (owned opt-in, publisher revenue share).
- Apply to an affiliate network; confirm per-program email permission and rules.
- Sender domain, SPF/DKIM/DMARC, real postal address (`SENDER_POSTAL_ADDRESS`).
- Legal review of commercial-email and privacy rules for your audience's jurisdictions.

## Phase 2 & 3: Persistence

Offers, audiences and subscribers now live in PostgreSQL.

- SQLAlchemy models: `offers`, `audiences`, `subscribers`, `consent_records`,
  `suppression_records` (in `db/models/`).
- One Alembic migration creates all five tables: `make migrate` (`alembic upgrade head`).
- Idempotent seeding: `make seed` → offers=100, audiences=10, subscribers=10,000,
  consent_records=10,000, suppression_records=500. Re-running changes nothing
  (offers/audiences merged by PK; subscriber set inserted only when empty).
- `services/offer_repository.py` + `services/seeding.py`; entrypoint `scripts/seed.py`.
- `GET /api/offers` now reads from PostgreSQL (EPC-ordered), not the in-memory adapter.
- Integration tests (`test_offer_persistence.py`, `test_audience_persistence.py`) prove
  persistence, idempotency, consent/suppression integrity, and API-from-DB. They reset
  the schema via a `fresh_db` fixture and skip cleanly when Postgres is down.

Suite now 43 tests. The orchestrator loop now reads its offers/audiences/subscribers
from these seeded tables (not in-memory): run `make migrate && make seed` first, then
the engine and dashboard reflect the database. Deleting offers from the DB yields a
zero-campaign run, confirming it is DB-backed.

## Autonomous Loop (new)

The full simulated loop now runs end-to-end through an orchestrator that chains the
agents, with no database yet (in-memory, deterministic, $0):

- `agents/orchestrator.py` — `run_engine()`: offer → score → match audience →
  generate creative → **compliance gate** → send → simulate funnel → revenue/cost →
  optimizer decision → aggregated overview. Respects the kill switch and the
  deterministic compliance gate (neither can be overridden by an agent).
- `agents/optimizer_agent/graph.py` — rule-based `decide()` returning SCALE / PAUSE /
  KILL / TEST / RETRY (AI seam).
- `agents/campaign_agent/graph.py` — `generate_creative()` templated creative (AI seam).
- `simulator/world.py` — 10 synthetic audiences + subscribers (configurable size).
- `simulator/events.py` — deterministic delivery/click/conversion funnel with
  configurable rates.
- API: `POST /api/engine/run`, and `GET /api/analytics/overview` + `/campaigns` now
  return **live computed** numbers (previously hardcoded). Kill switch via
  `SYSTEM_ACTIVE`.
- Dashboard fetches the live overview/campaigns (falls back gracefully if API is down).
- Tests: event simulator, optimizer, and full e2e loop (incl. compliance-blocks and
  kill-switch). Suite now 39 tests, all passing.

Still deterministic only (no LLM yet) and still in-memory (no persistence) — those are
the next increments.

---
Updated: 2026-09-20

## Summary

Phase 0 architecture work is complete. Phase 1 local infrastructure is complete and reproducible with Docker Compose. Phase 2 has started but is not complete because mock offers are not yet persisted in PostgreSQL.

## Completed

### Phase 0: Architecture

- Replaced the original instructions with the updated `$0` local-development instructions in `PROJECT_INSTRUCTIONS.md`.
- Added domain event contracts with event IDs, event types, aggregate IDs, timestamps, payloads, correlation IDs, and idempotency keys.
- Added deterministic compliance decision contracts: `APPROVE`, `REVIEW`, and `BLOCK`.
- Preserved the adapter boundary for affiliate networks.
- Documented ownership boundaries in `docs/architecture/phase-0-boundaries.md`.
- No real affiliate accounts or real traffic are required.

### Phase 1: Local Infrastructure

- Docker Compose stack includes:
  - PostgreSQL
  - Redis
  - FastAPI API
  - Worker
  - n8n
  - listmonk and its PostgreSQL database
  - Postal web server
  - Postal SMTP server
  - Postal worker
  - Postal MariaDB
  - Postal RabbitMQ
- Added SQLAlchemy and Alembic foundations.
- Added API `/health` and dependency-aware `/ready` checks.
- Added Postal lab configuration with generated, ignored runtime secrets.
- Added listmonk configuration and initialization.
- Added idempotent Phase 1 bootstrap:

```bash
make phase1-up
```

The bootstrap starts the stack and initializes listmonk and Postal only when their schemas are missing.

### Engineering Baseline

- Ruff linting configured and passing.
- GitHub Actions runs backend lint/tests and the dashboard build.
- Next.js dashboard shell exists with overview and campaign detail routes.
- Backend test suite currently passes 23 tests.
- Current Docker services are healthy locally.

## Current Infrastructure Status

| Service | Status |
|---|---|
| API | Healthy |
| Worker | Healthy |
| PostgreSQL | Healthy |
| Redis | Healthy |
| n8n | Healthy |
| listmonk | Healthy |
| listmonk PostgreSQL | Healthy |
| Postal web | Healthy |
| Postal SMTP | Running |
| Postal worker | Running |
| Postal MariaDB | Healthy |
| Postal RabbitMQ | Healthy |

## Phase 2: Started, Not Complete

Implemented:

- Mock affiliate adapter.
- 100 synthetic offers.
- Offer normalization.
- Offer API route.
- Offer eligibility and scoring tests.

Still required:

- SQLAlchemy `offers` model.
- Alembic migration for the offers table.
- Offer repository/service.
- Persist all 100 mock offers in PostgreSQL.
- Make the Offer API read from PostgreSQL.
- Add integration tests proving persistence and repeatable seeding.

The current database only has Alembic's tracking table; the offer data is still generated in memory.

## Git Promotion Status

The project uses:

```text
feature -> develop -> release -> main
```

Merged:

- Phase 0 feature merged into `develop`, then promoted through `release` to `main`.
- PR #5 merged Phase 1 Postal infrastructure and updated architecture instructions into `develop`.
- PR #6 merged the Phase 1 bootstrap automation into `develop`.

PR links:

- [PR #5: Add Postal lab mail infrastructure](https://github.com/harshajv7981/autonomous-affiliate-engine/pull/5)
- [PR #6: Automate Phase 1 local bootstrap](https://github.com/harshajv7981/autonomous-affiliate-engine/pull/6)

## Next Work

The next milestone is Phase 2 completion:

1. Create the SQLAlchemy offer model.
2. Generate the first Alembic domain migration.
3. Add PostgreSQL offer persistence.
4. Seed the 100 mock offers idempotently.
5. Serve offers from the database through the API.
6. Add integration coverage for the full offer ingestion path.
