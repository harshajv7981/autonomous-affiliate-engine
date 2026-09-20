# Autonomous Affiliate Campaign Engine

> **Purpose:** Master engineering and operating instructions for building a private, automation-first affiliate performance-marketing system in VS Code.
>
> **Primary goal:** Build a system that can discover permitted affiliate offers, evaluate them, match them to permitted traffic/audience sources, generate campaigns, run compliance gates, execute campaigns, track clicks/conversions/revenue, optimize future campaigns, and show profitability from one dashboard.
>
> **Non-goal:** Build a spam engine, scrape/buy random consumer email lists, bypass mailbox filtering, fake traffic, fake conversions, or evade affiliate-network rules.

---

## 0. Project Rules — Read Before Coding

These rules are part of the system design, not optional guidance.

1. **Never send to an audience unless the traffic source and campaign allow it and the audience/contact use is authorized and appropriately permissioned for the intended communication.**
2. **Never use purchased/scraped/random email lists as a shortcut.** A public email address is not automatically permission to send commercial marketing.
3. **Never try to bypass Gmail/Yahoo/other mailbox filtering.** The system optimizes sender reputation, authentication, relevance, complaint rate, and engagement; it does not promise Primary-tab placement.
4. **Affiliate-network terms override our AI.** If an offer says email traffic is prohibited, the system must block the campaign.
5. **Deterministic rules beat LLM judgment for hard compliance/security rules.** An LLM may explain a rule or flag ambiguity, but it cannot override a hard block.
6. **No automated scale-up until the economics and deliverability are proven.** Start with sandbox/test data and small approved traffic volumes.
7. **All important decisions must be auditable.** Store what the system knew, what rule/model made the decision, and what happened afterward.
8. **Secrets never go into Git.** Use `.env` locally and a real secrets manager in production.
9. **Every external integration gets an adapter.** Never couple the core domain directly to one affiliate network or one email provider.
10. **The system optimizes for profit and valid outcomes, not vanity metrics.** Opens/CTR matter only insofar as they support legitimate conversions and revenue.

---

# 1. Product Definition

## 1.1 What we are building

A private autonomous platform with this loop:

```text
Affiliate Networks / Offer Feeds
            |
            v
      Offer Ingestion
            |
            v
       Offer Engine
            |
            v
    Audience / Traffic Sources
            |
            v
      Matching Engine
            |
            v
      Campaign Agent
            |
            v
      Compliance Gate
            |
            v
      Email Execution
            |
            v
        Recipients
            |
      clicks/conversions
            |
            v
     Analytics + Finance
            |
            v
   Optimization / Learning
            |
            +-----------------> next campaign
```

## 1.2 Business model

The project is designed as a **performance/affiliate publisher operation**, not as a SaaS product sold to clients.

Revenue can come from:

- CPA (commission per approved acquisition)
- CPL (commission per qualified lead)
- CPS / revenue share (commission on sale)
- other network-specific performance models

The platform itself does not need to own the advertised product.

## 1.3 What makes the product valuable

The moat is not “we can send email.” The valuable layer is:

```text
Offer data
+ audience/traffic data
+ campaign data
+ conversion data
+ economics
+ compliance state
+ historical learning
= optimization system
```

---

# 2. Final Architecture

## 2.1 High-level system

```text
                         EXTERNAL WORLD

      +-------------------+       +----------------------+
      | Affiliate         |       | Approved Audience /  |
      | Networks          |       | Traffic Sources      |
      | Awin              |       | Email publishers     |
      | CJ                |       | opt-in properties    |
      | Rakuten           |       | other approved       |
      | Partnerize        |       | sources               |
      | FlexOffers        |       +----------+-----------+
      +---------+---------+                  |
                |                            |
                v                            v
      +------------------------------------------------+
      |               INTEGRATION LAYER                |
      | Network adapters | Audience connectors         |
      +-------------------------+----------------------+
                                |
                                v
      +------------------------------------------------+
      |             DOMAIN / DATA LAYER               |
      | PostgreSQL                                     |
      | offers | rules | audiences | campaigns        |
      | clicks | conversions | commissions | costs    |
      +-------------------------+----------------------+
                                |
                                v
      +------------------------------------------------+
      |                INTELLIGENCE                    |
      | Offer Agent                                    |
      | Audience Agent                                 |
      | Campaign Agent                                 |
      | Compliance Agent                               |
      | Optimization Agent                             |
      +-------------------------+----------------------+
                                |
                                v
      +------------------------------------------------+
      |                 EXECUTION                      |
      | Campaign scheduler                             |
      | listmonk                                       |
      | Postal / approved ESP                          |
      +-------------------------+----------------------+
                                |
                                v
      +------------------------------------------------+
      |              OBSERVABILITY                     |
      | delivery | opens | clicks | conversions       |
      | revenue | costs | profit | failures            |
      +-------------------------+----------------------+
                                |
                                v
      +------------------------------------------------+
      |              OPTIMIZATION LOOP                 |
      | learn -> score -> test -> scale/pause/stop     |
      +------------------------------------------------+
```

## 2.2 Core architectural principle

**Own the domain logic; outsource commodity infrastructure to mature open-source systems.**

Use:

- PostgreSQL for system-of-record data.
- listmonk for subscriber/list/campaign mechanics.
- Postal or an approved ESP for mail delivery.
- n8n for integration workflows where it simplifies operations.
- LangGraph for stateful agent workflows.
- Redis for queues/cache/short-lived state.
- FastAPI for our application API.
- React/Next.js for the control dashboard.

Do not rebuild these commodity capabilities prematurely.

---

# 3. Technology Decisions

| Layer | Decision | Notes |
|---|---|---|
| Language | Python | Main application + AI orchestration |
| API | FastAPI | Internal/external REST API |
| ORM | SQLAlchemy | Database access |
| Migrations | Alembic | Database schema versioning |
| Database | PostgreSQL | System of record |
| Queue/cache | Redis | Jobs, locks, short-lived data |
| Workflow | n8n | Cross-service automation/integrations |
| Agent orchestration | LangGraph | Stateful, branching, durable agent workflows |
| Email campaign engine | listmonk | Self-hosted list/campaign management |
| Mail transport | Postal initially for lab; approved ESP as needed | Do not assume self-hosting solves deliverability |
| Frontend | Next.js + TypeScript | Dashboard |
| UI | Tailwind + component library | Keep dashboard simple |
| Charts | Recharts or ECharts | Metrics |
| Containers | Docker Compose locally | Move to managed containers later if needed |
| Reverse proxy | Caddy or Nginx | HTTPS |
| Testing | pytest | Unit/integration |
| API testing | httpx | FastAPI integration tests |
| Lint/format | Ruff | Python |
| Type checking | mypy or pyright | Prefer strict typing over time |
| Frontend lint/format | ESLint + Prettier | TypeScript |
| Monitoring | Prometheus + Grafana | Phase 3+ |
| Logs | JSON logs; Loki later | Phase 3+ |

### Current upstream reference points

- listmonk: https://github.com/knadh/listmonk — self-hosted newsletter/list manager; current stable release observed during planning: **v6.2.0**. 
- Postal: https://github.com/postalserver/postal — self-hosted mail platform; current release observed during planning: **v3.3.7**.
- n8n: https://github.com/n8n-io/n8n — workflow automation; note its current licensing is described by the project as **fair-code / Sustainable Use License**, so review licensing before commercial redistribution.
- LangGraph: https://github.com/langchain-ai/langgraph — stateful agent orchestration with persistence, branching and human-in-the-loop support.
- Trigger.dev: https://github.com/triggerdotdev/trigger.dev — optional alternative for durable jobs/AI workflows; self-hosting is supported. Do not add it unless we have a concrete need.

---

# 4. Why We Use Both Normal Code and Agents

Do **not** turn every rule into an LLM prompt.

## 4.1 Deterministic software handles

- authentication
- authorization
- database updates
- API calls
- eligibility rules
- GEO filters
- offer status
- email permission flags
- suppression
- unsubscribe
- rate limits
- idempotency
- financial calculations
- retries
- state transitions
- emergency stop

## 4.2 Agents handle

- offer interpretation
- audience/offer matching
- campaign angle selection
- copy generation
- creative variation
- performance diagnosis
- experiment proposals
- anomaly explanations
- optimization recommendations

### Example 1 — compliance

Bad:

```text
LLM: “I think this offer probably allows email.”
```

Good:

```python
if not offer.email_allowed:
    block_campaign("EMAIL_NOT_ALLOWED")
```

### Example 2 — finance

Bad:

```text
LLM: “Net profit looks positive.”
```

Good:

```python
net_profit = revenue - traffic_cost - email_cost - ai_cost - infrastructure_cost
```

---

# 5. Agents — Final Responsibilities

## 5.1 Offer Intelligence Agent

### Input

- normalized offer records
- payout
- GEO
- category
- EPC
- conversion data
- traffic restrictions
- advertiser rules

### Output

```json
{
  "offer_id": "...",
  "score": 0.0,
  "reasons": [],
  "recommended_audiences": [],
  "risk_flags": [],
  "recommended_action": "TEST"
}
```

### Do not let it

- alter network rules
- assume email is allowed
- fabricate missing metrics
- create tracking links outside the approved adapter

---

## 5.2 Audience Intelligence Agent

### Input

- audience metadata
- permitted traffic types
- GEO
- category
- engagement history
- consent/permission state
- previous performance

### Output

- eligible segments
- audience/offer fit
- expected CTR/CVR ranges from observed data
- risk flags

### Important

This agent **does not scrape random consumer email addresses**.

It works with approved/authorized audience sources only.

---

## 5.3 Campaign Agent

### Input

- offer
- audience segment
- objective
- allowed claims
- brand/offer restrictions

### Output

```text
subject variants
preheader variants
email body variants
CTA variants
tracking configuration
campaign metadata
```

The output must be structured JSON before being converted to HTML.

---

## 5.4 Compliance Agent

The compliance agent is a second layer. It does **not** replace hard-coded rules.

### Checks

- traffic source approved
- email traffic allowed
- audience permission state acceptable
- GEO allowed
- campaign date within offer window
- required disclosure present
- sender identity valid
- unsubscribe present
- suppression list enforced
- prohibited claims absent
- required advertiser wording present

### Final decision

```text
APPROVE
REVIEW
BLOCK
```

Any deterministic `BLOCK` wins.

---

## 5.5 Optimization Agent

### Inputs

- delivered count
- bounce rate
- complaint rate when available
- click rate
- conversion rate
- EPC
- commission
- traffic cost
- AI cost
- net profit

### Possible actions

```text
CONTINUE
TEST_NEW_CREATIVE
TEST_NEW_SEGMENT
REDUCE_VOLUME
PAUSE
STOP
SCALE_WITHIN_LIMITS
```

No uncontrolled scaling.

---

# 6. Campaign State Machine

Every campaign must have an explicit state.

```text
DRAFT
  |
  v
ELIGIBILITY_CHECK
  |
  v
MATCHED
  |
  v
GENERATING
  |
  v
QA
  |
  v
COMPLIANCE_CHECK
  |
  +----> BLOCKED
  |
  v
SCHEDULED
  |
  v
SENDING
  |
  v
RUNNING
  |
  v
ANALYZING
  |
  v
OPTIMIZING
  |
  +----> NEXT_EXPERIMENT
  |
  v
COMPLETED
```

Every transition must be logged.

---

# 7. Folder Structure

Use a monorepo initially.

```text
autonomous-affiliate-engine/
│
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   ├── api/
│   │   │   │   ├── routes/
│   │   │   │   └── schemas/
│   │   │   ├── services/
│   │   │   └── middleware/
│   │   └── tests/
│   │
│   ├── worker/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── jobs/
│   │   │   └── schedulers/
│   │   └── tests/
│   │
│   └── dashboard/
│       ├── app/
│       ├── components/
│       ├── lib/
│       └── tests/
│
├── agents/
│   ├── offer_agent/
│   │   ├── graph.py
│   │   ├── prompts.py
│   │   ├── schemas.py
│   │   ├── tools.py
│   │   └── tests/
│   │
│   ├── audience_agent/
│   ├── campaign_agent/
│   ├── compliance_agent/
│   └── optimizer_agent/
│
├── domain/
│   ├── offers/
│   ├── audiences/
│   ├── campaigns/
│   ├── conversions/
│   ├── finance/
│   └── experiments/
│
├── integrations/
│   ├── affiliate/
│   │   ├── base.py
│   │   ├── awin/
│   │   ├── cj/
│   │   ├── rakuten/
│   │   ├── partnerize/
│   │   └── flexoffers/
│   │
│   ├── audience/
│   │   └── base.py
│   │
│   ├── email/
│   │   ├── listmonk/
│   │   ├── postal/
│   │   └── base.py
│   │
│   └── analytics/
│
├── db/
│   ├── migrations/
│   ├── models/
│   ├── repositories/
│   └── session.py
│
├── policies/
│   ├── offer_rules.py
│   ├── email_rules.py
│   ├── audience_rules.py
│   ├── geo_rules.py
│   └── risk_limits.py
│
├── templates/
│   ├── email/
│   └── prompts/
│
├── infrastructure/
│   ├── docker/
│   ├── postgres/
│   ├── redis/
│   ├── listmonk/
│   ├── postal/
│   ├── n8n/
│   └── monitoring/
│
├── scripts/
│   ├── bootstrap/
│   ├── seed/
│   └── maintenance/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── e2e/
│
├── docs/
│   ├── architecture/
│   ├── decisions/
│   ├── integrations/
│   └── runbooks/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── README.md
└── PROJECT_INSTRUCTIONS.md
```

---

# 8. Database Design

PostgreSQL is the source of truth for our business data.

## 8.1 Core tables

```text
users
affiliate_networks
affiliate_accounts
advertisers
offers
offer_rules
offer_events
traffic_sources
audiences
audience_segments
subscribers
consent_records
suppression_records
campaigns
campaign_variants
campaign_recipients
messages
click_events
conversion_events
commission_events
revenue_events
cost_events
experiments
experiment_results
agent_runs
agent_decisions
system_alerts
audit_logs
donation_ledger
```

## 8.2 Offer schema

```text
offers
-----------------------------
id
network_id
external_offer_id
name
description
advertiser
category
geo
payout
payout_type
epc
conversion_rate
allowed_traffic_types
email_allowed
email_approval_required
terms_url
tracking_url_template
status
starts_at
ends_at
last_synced_at
created_at
updated_at
```

## 8.3 Audience schema

```text
audiences
-----------------------------
id
name
source_type
source_provider
geo
category
estimated_size
permission_model
permission_verified
email_allowed
status
created_at
updated_at
```

## 8.4 Subscriber schema

```text
subscribers
-----------------------------
id
audience_id
email
country
attributes_json
permission_source
permission_timestamp
status
unsubscribed_at
created_at
updated_at
```

Do not store more personal data than necessary.

---

# 9. Affiliate Integration Design

Every affiliate network gets the same interface.

```python
from abc import ABC, abstractmethod

class AffiliateNetworkAdapter(ABC):
    @abstractmethod
    async def sync_offers(self) -> list[dict]:
        ...

    @abstractmethod
    async def build_tracking_link(self, offer_id: str, sub_id: str) -> str:
        ...

    @abstractmethod
    async def sync_conversions(self, since_timestamp):
        ...

    @abstractmethod
    async def sync_reports(self, since_timestamp):
        ...
```

Implement in this order:

```text
P0: MockNetworkAdapter
P1: AwinAdapter
P1: CJAdapter
P2: RakutenAdapter
P2: PartnerizeAdapter
P3: FlexOffersAdapter
```

Do not let one vendor's JSON schema leak into the domain model.

---

# 10. Email System Design

## 10.1 listmonk role

Use listmonk for:

- subscriber/list mechanics
- campaign mechanics
- templates
- list membership
- campaign API calls
- basic mailing operations

Current listmonk releases show ongoing security and permission fixes, so pin stable versions and keep backups before upgrades.

## 10.2 Postal role

Use Postal as the self-hosted mail layer in the development/lab path and only in production after deliverability testing.

Postal provides HTTP/API/webhook-oriented mail infrastructure, but self-hosting does not make an IP/domain reputable automatically.

## 10.3 Alternative production mail path

The email abstraction must support an approved ESP as another adapter.

```text
Campaign Service
      |
      v
EmailProvider interface
   /        |         \
Listmonk  Postal   Approved ESP
```

This prevents a complete redesign if production deliverability requirements favor a managed sender.

---

# 11. Deliverability Design

The system must optimize **deliverability**, not “inbox-tab hacking.”

## Required controls

- SPF
- DKIM
- DMARC
- TLS
- correct sender identity
- unsubscribe support
- suppression lists
- bounce processing
- complaint monitoring where available
- controlled sending rate
- domain/IP warm-up
- content quality
- audience relevance

Gmail's current sender guidance says senders sending 5,000+ messages/day to Gmail accounts are subject to additional requirements and that non-compliant traffic can face temporary or permanent rejection. It also emphasizes authentication, avoiding unsolicited email, and easy unsubscribe. See: https://support.google.com/mail/answer/14229414

## Do not promise

```text
“Primary inbox guaranteed”
“Never goes to Promotions”
“Spam filter bypass”
```

Those are not valid product guarantees.

---

# 12. Compliance Architecture

## 12.1 Policy hierarchy

```text
Law / regulation
      ↓
Affiliate network terms
      ↓
Advertiser offer rules
      ↓
Traffic-source rules
      ↓
Internal risk policy
      ↓
AI recommendations
```

Lower layers may never override a higher layer.

## 12.2 Required campaign gates

```text
[ ] Affiliate account active
[ ] Offer active
[ ] Traffic type permitted
[ ] Email permitted
[ ] Required approval present
[ ] GEO permitted
[ ] Audience permission verified
[ ] Suppression applied
[ ] Unsubscribe present
[ ] Disclosure requirements satisfied
[ ] Prohibited claims absent
[ ] Tracking validated
[ ] Frequency/rate limits satisfied
[ ] Kill switch inactive
```

For U.S. commercial email, CAN-SPAM requirements include truthful header/subject information, an opt-out mechanism and other requirements. See: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

The exact legal requirements vary by jurisdiction; do not hard-code one country's assumptions as global truth.

---

# 13. Tracking and Attribution

Every outbound campaign should produce identifiers that survive the full journey.

```text
campaign_id
variant_id
subscriber_id / audience_id
click_id
session_id
conversion_id
network_transaction_id
```

Example:

```text
Email
  ↓
Tracking URL
  ↓
Click event
  ↓
Affiliate tracking ID
  ↓
Advertiser landing page
  ↓
Conversion
  ↓
Affiliate network report
  ↓
Revenue event
```

## Do not trust open tracking as the primary revenue metric

Opens can be noisy. Build economics around clicks, approved conversions, commissions and verified revenue where possible.

---

# 14. Economics Engine

The system should calculate:

```text
gross_revenue
- traffic_cost
- email_cost
- ai_cost
- infrastructure_cost
- payment/transaction_cost
= net_profit
```

Also calculate:

```text
revenue_per_1000
profit_per_1000
revenue_per_click
profit_per_click
EPC
CVR
ROI
payback_period (when applicable)
```

## Example

```text
1,000 recipients
30 clicks
3 conversions
$20 payout each

Revenue = $60

Then subtract actual operating costs.
```

Do not optimize only on payout.

A $50 CPA offer can be worse than a $12 CPA offer if the $12 offer converts much better.

---

# 15. Optimization Logic

## 15.1 Initial deterministic score

Start with a weighted formula instead of an ML model.

```text
score =
  0.30 * normalized_epc
+ 0.20 * normalized_cvr
+ 0.15 * geo_fit
+ 0.15 * audience_fit
+ 0.10 * offer_stability
+ 0.10 * historical_profitability
```

Tune the weights using actual data.

## 15.2 AI layer

The optimizer can propose:

- next subject line
- next creative angle
- next segment
- next offer
- send-window test
- stop/continue decision

The executor must still obey deterministic risk limits.

---

# 16. n8n Workflows

Keep n8n outside the core business logic.

Use it for:

```text
Schedule
  ↓
call FastAPI
  ↓
wait / retry
  ↓
call external system
  ↓
webhook
  ↓
notify dashboard
```

Do not put the entire business domain inside giant n8n workflows. That becomes hard to test and version.

Recommended first workflows:

1. `offer_sync`
2. `conversion_sync`
3. `campaign_scheduler`
4. `bounce_webhook`
5. `daily_profit_report`
6. `system_alerts`

---

# 17. LangGraph Design

Use one graph per major long-running process instead of “one agent that does everything.”

Example campaign graph:

```text
START
  |
  v
load_offer
  |
  v
load_audience
  |
  v
check_hard_rules
  |
  +---- blocked ----> END
  |
  v
score_match
  |
  v
generate_campaign
  |
  v
content_qa
  |
  v
compliance_review
  |
  +---- review ----> HUMAN_REVIEW / later policy-based path
  |
  v
schedule
  |
  v
send
  |
  v
collect_results
  |
  v
analyze
  |
  v
optimizer
  |
  v
END
```

The LangGraph repository explicitly positions LangGraph for stateful, long-running, persistent workflows and human-in-the-loop execution. Use that capability rather than creating stateless prompt chains.

---

# 18. API Design

## Core endpoints

```text
GET    /health
GET    /ready

GET    /api/offers
POST   /api/offers/sync
GET    /api/offers/{id}

GET    /api/audiences
GET    /api/audiences/{id}
POST   /api/audiences/{id}/sync

POST   /api/campaigns
GET    /api/campaigns
GET    /api/campaigns/{id}
POST   /api/campaigns/{id}/validate
POST   /api/campaigns/{id}/schedule
POST   /api/campaigns/{id}/pause
POST   /api/campaigns/{id}/stop

GET    /api/analytics/overview
GET    /api/analytics/campaigns
GET    /api/analytics/offers
GET    /api/analytics/audiences
GET    /api/finance/profit

POST   /api/webhooks/email
POST   /api/webhooks/affiliate/{network}

POST   /api/system/kill-switch
GET    /api/system/status
```

---

# 19. Security Requirements

## Secrets

Store only in environment variables locally.

```text
DATABASE_URL
REDIS_URL
OPENAI_API_KEY / MODEL_API_KEY
AWIN_CLIENT_ID
AWIN_CLIENT_SECRET
CJ_API_KEY
RAKUTEN_CLIENT_ID
POSTAL_API_KEY
LISTMONK_API_KEY
```

Production: use a cloud secrets manager.

## Authentication

The dashboard must have authentication before real affiliate credentials or audience data are connected.

## Authorization

Use roles later:

```text
ADMIN
OPERATOR
READ_ONLY
```

## Audit logs

Record:

```text
who
what
when
request_id
object_id
old_state
new_state
reason
```

## Idempotency

Every external event handler must tolerate duplicate events.

---

# 20. Testing Strategy

## Unit tests

Test every deterministic rule.

Examples:

```text
email_not_allowed -> block
GEO_not_allowed -> block
unsubscribed -> suppress
expired_offer -> block
valid_offer -> eligible
```

## Integration tests

Run real containers:

```text
PostgreSQL
Redis
listmonk
Postal test mode / mail sandbox
```

## Contract tests

Each affiliate adapter must conform to the same interface.

## End-to-end test

A synthetic campaign must complete:

```text
mock offer
↓
mock audience
↓
AI campaign
↓
policy check
↓
mock send
↓
mock click
↓
mock conversion
↓
commission
↓
revenue
↓
profit
↓
optimizer
```

## Agent evaluations

Keep a dataset of:

- valid offers
- disallowed offers
- ambiguous offers
- misleading creative examples
- correct campaign outputs
- prohibited claims

Every prompt/model change must run evaluation tests before deployment.

---

# 21. Development Phases

## Phase 0 — Repository and engineering baseline

### Goal

Create the project skeleton and development standards.

### Tasks

- create Git repository
- create directory structure
- create Python environment
- add FastAPI
- add PostgreSQL connection
- add Redis connection
- add Alembic
- add Ruff
- add pytest
- add `.env.example`
- add Docker Compose
- add README
- add CI

### Exit condition

```text
clone repo
↓
docker compose up
↓
API health check passes
↓
DB migration passes
↓
pytest passes
```

---

## Phase 1 — Local infrastructure

### Goal

Get the core stack running locally.

### Components

```text
PostgreSQL
Redis
FastAPI
worker
n8n
listmonk
Postal
```

### Exit condition

Every service starts with one command.

---

## Phase 2 — Domain model

### Goal

Build the database and business objects.

### Tasks

- offers
- offer rules
- audiences
- subscribers
- consent records
- suppression
- campaigns
- variants
- clicks
- conversions
- revenue
- costs
- audit logs

### Exit condition

A synthetic campaign can be represented entirely in PostgreSQL.

---

## Phase 3 — Mock affiliate network

### Goal

Avoid real-account risk while building the whole loop.

### Build

```text
MockAffiliateAdapter
```

It returns:

- 100 offers
- different payout models
- different GEOs
- some email-permitted
- some email-forbidden
- some approval-required
- synthetic EPC/CVR data

### Exit condition

Offer ingestion works automatically.

---

## Phase 4 — Offer Intelligence Agent

### Goal

Automatically rank synthetic offers.

### Build

- deterministic filters
- scoring
- agent explanation
- persisted agent decisions

### Exit condition

Given a fixed test dataset, the system selects known good offers consistently.

---

## Phase 5 — Audience Engine

### Goal

Represent legitimate traffic/audience sources.

### Build

- audience connectors
- permission metadata
- segmenting
- suppression
- eligibility checks

### Important

Do not connect random scraped consumer addresses.

### Exit condition

The system can create an eligible synthetic audience segment and correctly suppress ineligible recipients.

---

## Phase 6 — Campaign Agent

### Goal

Turn an offer + audience into structured campaign variants.

### Build

- prompt templates
- structured output schema
- subject lines
- preheaders
- copy
- CTA
- safe HTML template rendering

### Exit condition

Campaign JSON validates against a strict schema and renders correctly.

---

## Phase 7 — Compliance Gate

### Goal

Prevent invalid campaigns from reaching the send layer.

### Build

- hard rules
- network restrictions
- audience permission checks
- GEO checks
- unsubscribe/suppression checks
- disclosure checks
- prohibited-claim checks

### Exit condition

Negative test suite blocks all known invalid cases.

---

## Phase 8 — Email execution

### Goal

Send to a test mailbox environment.

### Build

- listmonk integration
- Postal/test ESP integration
- delivery events
- bounce events
- unsubscribe events

### Exit condition

Test email flows from campaign to delivery event and suppression works.

---

## Phase 9 — Tracking and attribution

### Goal

Connect clicks and conversions to campaigns and revenue.

### Build

- tracking IDs
- redirect/click event capture
- affiliate sub IDs
- conversion webhook/import
- commission reconciliation

### Exit condition

Synthetic conversion becomes revenue in the dashboard.

---

## Phase 10 — Analytics dashboard

### Goal

One screen to see the health of the machine.

### Dashboard pages

```text
Overview
Offers
Audiences
Campaigns
Conversions
Finance
Experiments
Agent Activity
System Health
Settings
```

### Overview metrics

```text
revenue
affiliate commissions
costs
net profit
active campaigns
clicks
conversions
EPC
CVR
bounce rate
unsubscribe rate
alerts
```

---

## Phase 11 — Optimization Agent

### Goal

Start closing the loop automatically.

### Build

- A/B tests
- offer ranking feedback
- creative performance
- audience performance
- profit-based decisions
- automatic pause rules

### Exit condition

The system can run a synthetic experiment and choose the next experiment based on observed results.

---

## Phase 12 — Real affiliate integrations

### Order

```text
Awin
CJ
Rakuten
Partnerize
FlexOffers
```

Do not connect all of them simultaneously.

For each network:

1. Create approved publisher account.
2. Obtain API credentials.
3. Read current traffic-source rules.
4. Read current email restrictions.
5. Create adapter.
6. Run adapter tests.
7. Sync offers into our normalized schema.
8. Verify tracking.
9. Verify conversion reporting.
10. Start with approved low-volume tests.

---

## Phase 13 — Controlled production

### Start with

```text
1 network
1 approved traffic source
1–3 offers
small audience
small campaign volume
```

Measure:

```text
delivery
bounce
complaints
clicks
conversions
commission
profit
```

Do not scale because an AI score says “high confidence.” Scale because the real data supports it.

---

## Phase 14 — Autonomous operation

Only after stability is proven.

### Remove manual approval for low-risk flows

Allow automation only when:

- offer is known and approved
- traffic source is approved
- audience is eligible
- campaign is within known rules
- historical performance exists
- risk thresholds pass

Unknown/novel situations go to a review queue.

---

# 22. Production Deployment

## Initial production stack

```text
Cloud VM(s)
│
├── Reverse proxy
├── API
├── Worker
├── n8n
├── listmonk
├── Postal or approved ESP adapter
├── PostgreSQL
└── Redis
```

Later:

```text
Load balancer
   |
API replicas
Worker pool
Managed PostgreSQL
Managed Redis
Object storage
Monitoring
```

Don't build Kubernetes first. Earn the complexity.

---

# 23. Observability

Every job must have:

```text
request_id
job_id
campaign_id
agent_run_id
network
started_at
completed_at
status
error_code
latency
```

Alerts for:

```text
API failures
network auth failure
offer sync failure
high bounce
high complaint rate
unsubscribe spike
conversion drop
negative profit
provider rejection
kill switch activated
```

---

# 24. Kill Switches and Risk Limits

Global:

```text
STOP_ALL_CAMPAIGNS
STOP_NETWORK
STOP_AUDIENCE
STOP_SEND_PROVIDER
```

Per campaign:

```text
max_recipients
max_daily_cost
max_expected_loss
max_bounce_rate
max_complaint_rate
max_frequency
```

The system should fail closed.

If a required permission/rule cannot be verified, **do not send**.

---

# 25. Cost Control

The AI stack should not become more expensive than the business.

Track:

```text
LLM requests
LLM tokens
cost per campaign
cost per 1,000 recipients
cost per conversion
```

Use cheap deterministic filtering before expensive LLM calls.

### Pipeline

```text
10,000 offers
   ↓ deterministic filter
1,500
   ↓ numerical ranking
200
   ↓ LLM evaluation
20
```

Do not send all 10,000 to an LLM.

---

# 26. Git Workflow

Branches:

```text
main
  |
develop
  |
feature/offer-engine
feature/awin-adapter
feature/campaign-agent
feature/dashboard
```

Commit style:

```text
feat: add offer normalization
fix: block email-forbidden offers
refactor: isolate affiliate adapter
 test: add campaign compliance cases
```

Every PR/change should include tests for business logic.

Never commit:

```text
.env
API keys
affiliate secrets
recipient exports
production database dumps
private credentials
```

---

# 27. VS Code Setup

Recommended extensions:

```text
Python
Pylance
Docker
GitHub Pull Requests and Issues
GitLens (optional)
REST Client or Thunder Client
YAML
PostgreSQL client extension (optional)
ESLint
Prettier
```

Use a `.vscode/settings.json` later for consistent formatter/linter settings.

Recommended tasks:

```text
Start Stack
Run API
Run Worker
Run Tests
Run Lint
Run Migrations
Seed Mock Data
Open Dashboard
```

---

# 28. First Files To Create

The very first implementation should create these files:

```text
.env.example
.gitignore
README.md
PROJECT_INSTRUCTIONS.md
docker-compose.yml
Makefile
pyproject.toml

apps/api/app/main.py
apps/api/app/config.py
apps/api/app/api/routes/health.py

apps/worker/app/main.py

db/session.py
db/models/__init__.py

db/repositories/__init__.py

integrations/affiliate/base.py
integrations/affiliate/mock/adapter.py

agents/offer_agent/graph.py
agents/offer_agent/schemas.py

policies/offer_rules.py
policies/email_rules.py

scripts/seed/mock_data.py

tests/unit/test_health.py
tests/unit/test_offer_rules.py
```

Do not build the dashboard first.

---

# 29. First Development Commands

From the VS Code terminal:

```bash
mkdir autonomous-affiliate-engine
cd autonomous-affiliate-engine

git init
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

Then install the initial Python toolchain using the project's `pyproject.toml` once created.

Next:

```bash
docker compose up -d
```

Then:

```bash
pytest
```

The exact Docker images/versions should be pinned in `docker-compose.yml` rather than using floating production tags.

---

# 30. Definition of Done for the Entire MVP

The MVP is done only when this complete synthetic flow works:

```text
Mock affiliate network
        ↓
Offer sync
        ↓
Offer normalized
        ↓
Offer scored
        ↓
Mock audience loaded
        ↓
Audience matched
        ↓
Campaign generated
        ↓
Compliance passed
        ↓
Campaign sent in test environment
        ↓
Click generated
        ↓
Conversion generated
        ↓
Commission recorded
        ↓
Revenue recorded
        ↓
Costs recorded
        ↓
Profit calculated
        ↓
Optimizer evaluates results
        ↓
Next campaign decision generated
        ↓
Dashboard shows complete history
```

If one of those pieces is missing, the platform is not yet an autonomous performance engine.

---

# 31. What We Will Not Build in MVP

Do not build these yet:

```text
Kubernetes
multi-region deployment
custom SMTP server from scratch
custom email editor
custom CRM
vector database
complex machine-learning recommender
20 affiliate networks
mobile app
public SaaS billing
multi-tenant architecture
```

These are distractions until the core economics work.

---

# 32. Research Priorities Before Real Money

For every real affiliate network, document:

```text
API availability
API authentication
offer feed
tracking-link API
conversion reporting
sub-ID support
email traffic allowed?
traffic-source approval?
GEO rules
creative rules
prohibited traffic
payment terms
minimum payout
publisher approval requirements
```

Official references to maintain in `docs/integrations/`.

Awin developer/API docs: https://help.awin.com/apidocs/introduction-1
CJ developer docs: https://docs.cj.com/docs/finding-your-path
Rakuten developer portal: https://developers.rakutenadvertising.com/

Do not rely on old blog posts as the authority for current network rules.

---

# 33. Financial / Donation Layer

The project should keep a separate donation ledger.

```text
donation_ledger
-----------------------------
period
revenue
operating_costs
net_profit
reserved_amount
donation_percentage
donation_amount
recipient
payment_reference
status
created_at
```

Do not count money as donated merely because the system has allocated it internally. Record actual payments separately.

Example:

```text
Revenue:              $2,400
Operating costs:        $800
Net profit:           $1,600
Donation allocation:    20%
Planned donation:       $320
Actual donation:         $0 until paid
```

This keeps accounting honest.

---

# 34. Operating Philosophy

The goal is not:

```text
send the most email
```

The goal is:

```text
maximize legitimate long-term profit
while minimizing:
- compliance risk
- audience harm
- complaint rate
- infrastructure failure
- wasted spend
```

The machine should learn to **stop** as aggressively as it learns to scale.

---

# 35. Immediate Next Steps

## STEP 1 — Create repository

Create:

```text
autonomous-affiliate-engine
```

## STEP 2 — Put this file at the repository root

```text
PROJECT_INSTRUCTIONS.md
```

## STEP 3 — Create the folder skeleton

Use Section 7 exactly.

## STEP 4 — Build local infrastructure

Start with:

```text
PostgreSQL
Redis
FastAPI
Worker
n8n
listmonk
Postal
```

## STEP 5 — Build health checks

Every service needs a health/ready check.

## STEP 6 — Build the database

Start with:

```text
offers
offer_rules
audiences
subscribers
consent_records
suppression_records
campaigns
campaign_variants
click_events
conversion_events
revenue_events
cost_events
audit_logs
```

## STEP 7 — Build MockAffiliateAdapter

This is our first real business integration interface.

## STEP 8 — Build Offer Agent

Only after the mock adapter works.

## STEP 9 — Build synthetic end-to-end campaign

Don't touch real traffic yet.

## STEP 10 — Connect first real affiliate network

Only after the synthetic system passes all tests.

---

# 36. Current Priority Queue

```text
P0
[ ] Repository
[ ] Docker Compose
[ ] PostgreSQL
[ ] Redis
[ ] FastAPI
[ ] Worker
[ ] Alembic
[ ] Tests
[ ] Mock affiliate adapter

P1
[ ] Offer normalization
[ ] Offer database
[ ] Offer scoring
[ ] Offer Agent
[ ] Audience schema
[ ] Campaign schema
[ ] Compliance Gate

P2
[ ] listmonk integration
[ ] Postal/test ESP integration
[ ] Tracking
[ ] Conversion simulation
[ ] Finance engine
[ ] Dashboard

P3
[ ] Awin adapter
[ ] CJ adapter
[ ] Rakuten adapter
[ ] Partnerize adapter
[ ] FlexOffers adapter

P4
[ ] Optimization Agent
[ ] Autonomous scheduling
[ ] Production monitoring
[ ] Automated risk controls
[ ] Donation ledger/reporting
```

---

# 37. Final Engineering Rule

**Do not add complexity because it sounds impressive.**

Build the smallest machine that can prove:

```text
offer
→ audience
→ campaign
→ compliant execution
→ click
→ conversion
→ commission
→ profit
→ optimization
```

Once this loop works with synthetic data and then one approved real network/traffic source, add scale.

The project succeeds when it can run this loop repeatedly, remain compliant, survive failures, explain its decisions, and produce measurable positive economics.

---

## Sources / Reference Links

### Open-source infrastructure

- listmonk GitHub: https://github.com/knadh/listmonk
- listmonk releases: https://github.com/knadh/listmonk/releases
- Postal GitHub: https://github.com/postalserver/postal
- Postal releases: https://github.com/postalserver/postal/releases
- n8n GitHub: https://github.com/n8n-io/n8n
- n8n docs: https://docs.n8n.io/
- LangGraph GitHub: https://github.com/langchain-ai/langgraph
- LangGraph project template: https://github.com/langchain-ai/new-langgraph-project
- Trigger.dev GitHub: https://github.com/triggerdotdev/trigger.dev

### Affiliate network / API references

- Awin API docs: https://help.awin.com/apidocs/introduction-1
- Awin email marketing partners: https://help.awin.com/advertisers/docs/en/email-marketing-partners
- CJ developer docs: https://docs.cj.com/docs/finding-your-path
- Rakuten Advertising developer portal: https://developers.rakutenadvertising.com/

### Email / compliance references

- Gmail Email Sender Guidelines FAQ: https://support.google.com/mail/answer/14229414
- FTC CAN-SPAM compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

---

**Version:** 1.0
**Status:** Build specification / master project instructions
**Last planning review:** 2026-09-20
