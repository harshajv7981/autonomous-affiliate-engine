# Autonomous Affiliate Engine --- Project Instructions

## 1. Project Goal

Build a private, coding-first, highly automated affiliate
performance-marketing engine.

The system should: 1. Discover and normalize affiliate offers. 2.
Identify legitimate, permissioned audience/traffic sources. 3. Match
offers to audiences. 4. Generate campaign creatives. 5. Run
deterministic compliance checks. 6. Execute approved campaigns through
email infrastructure. 7. Track clicks, conversions, commissions,
revenue, and costs. 8. Optimize future campaigns using performance data.
9. Provide a dashboard. 10. Eventually support a configurable donation
ledger based on distributable net profit.

**Development and simulation should cost \$0 whenever practical.**

Do not assume production-scale email delivery, domains, servers,
audience acquisition, affiliate approval, or paid AI APIs can remain
free forever.

------------------------------------------------------------------------

## 2. Business Model

This is NOT an email-marketing agency and NOT a SaaS product for
clients.

It is an internal affiliate-performance system:

``` text
Affiliate Networks / Advertisers
              ↓
        Offer Adapters
              ↓
        Offer Database
              ↓
      Offer Intelligence
              ↓
     Audience / Traffic
              ↓
       Matching Engine
              ↓
       Campaign Engine
              ↓
       Compliance Gate
              ↓
     Email/List Platform
              ↓
        Email Delivery
              ↓
        Legitimate Users
              ↓
      Clicks / Conversions
              ↓
       Commission Data
              ↓
        Analytics Engine
              ↓
      Optimization Engine
              ↺
```

Never build or use: - random scraped consumer email lists - purchased
spam lists - fake clicks or conversions - click farms - deceptive
claims - methods intended to bypass affiliate restrictions or email
safeguards

Use legitimate, permissioned, contractually allowed traffic and audience
sources.

------------------------------------------------------------------------

## 3. \$0 Development Strategy

Use local/self-hosted components wherever practical:

  Function              Initial implementation
  --------------------- ------------------------------
  IDE                   VS Code
  Source control        Git + GitHub
  Backend               Python + FastAPI
  Database              PostgreSQL
  Cache/queue           Redis
  Workflow automation   n8n self-hosted
  Agent orchestration   LangGraph
  Local AI              Ollama + suitable open model
  List management       listmonk
  Mail infrastructure   Postal
  Frontend              React/Next.js
  Charts                Recharts/ECharts
  Metrics               Prometheus
  Monitoring            Grafana
  Logs                  Loki
  Containers            Docker Compose
  Tests                 pytest
  Affiliate data        Mock network first

Free software does not mean production operations are free. Future costs
may include a domain, VPS/cloud server, email delivery, reputation
management, legitimate traffic acquisition, affiliate-network
requirements, paid LLM APIs, and storage.

Do not incur those costs until the software and economics justify them.

------------------------------------------------------------------------

## 4. Development-First Architecture

The first complete system must run locally:

``` text
Mock Affiliate Network
        ↓
Offer Engine
        ↓
PostgreSQL
        ↓
Matching Engine
        ↓
Campaign Engine
        ↓
Compliance Gate
        ↓
listmonk
        ↓
Postal / Email Simulator
        ↓
Click + Conversion Simulator
        ↓
Analytics Engine
        ↓
Optimization Engine
        ↺
```

------------------------------------------------------------------------

## 5. Do Not Start With Real Traffic

The first version uses simulation:

-   100 mock affiliate offers
-   10 mock audience segments
-   1,000 synthetic subscribers
-   simulated deliveries
-   simulated opens
-   simulated clicks
-   simulated conversions
-   simulated commissions
-   simulated costs

The first milestone is this complete loop:

``` text
Offer
 ↓
Eligibility
 ↓
Audience match
 ↓
Campaign
 ↓
Compliance
 ↓
Send
 ↓
Click
 ↓
Conversion
 ↓
Commission
 ↓
Revenue
 ↓
Optimization
```

Only after this works reliably should real affiliate accounts and real
traffic be integrated.

------------------------------------------------------------------------

## 6. Repository Structure

``` text
autonomous-affiliate-engine/
│
├── apps/
│   ├── api/
│   ├── worker/
│   └── dashboard/
│
├── agents/
│   ├── offer_agent/
│   ├── audience_agent/
│   ├── campaign_agent/
│   ├── compliance_agent/
│   └── optimizer_agent/
│
├── integrations/
│   ├── mock_network/
│   ├── awin/
│   ├── cj/
│   ├── rakuten/
│   ├── partnerize/
│   └── flexoffers/
│
├── domain/
│   ├── offers/
│   ├── audiences/
│   ├── campaigns/
│   ├── conversions/
│   └── finance/
│
├── infrastructure/
│   ├── docker/
│   ├── postgres/
│   ├── redis/
│   ├── listmonk/
│   └── postal/
│
├── simulator/
├── tests/
├── docs/
├── docker-compose.yml
├── .env.example
├── README.md
└── Makefile
```

------------------------------------------------------------------------

## 7. Technology Rules

### Backend

-   Python
-   FastAPI
-   Pydantic
-   SQLAlchemy
-   Alembic
-   pytest

### Database

PostgreSQL.

### Queue/cache

Redis.

### Workflow automation

Use n8n for orchestration and integrations. Keep core business logic in
version-controlled application code rather than burying it inside
workflows.

### Agent orchestration

Use LangGraph for stateful agent workflows where it adds value.

Do not make every function an AI agent.

### AI

Initial target:

``` text
Application
    ↓
Ollama
    ↓
Local open model
```

Paid model APIs may later be added behind a provider abstraction.

### Frontend

React/Next.js.

### Monitoring

Prometheus + Grafana + Loki.

------------------------------------------------------------------------

## 8. AI vs Deterministic Software

This is a hard architecture rule.

### Deterministic software handles

-   unsubscribe checks
-   suppression lists
-   offer eligibility
-   GEO restrictions
-   traffic-source restrictions
-   email permission
-   required disclosures
-   frequency limits
-   duplicate prevention
-   authentication/authorization
-   accounting calculations
-   audit logging
-   kill switch

### AI handles

-   offer analysis
-   campaign positioning
-   subject-line generation
-   creative variants
-   audience/offer reasoning after deterministic filtering
-   performance interpretation
-   experiment ideas
-   optimization recommendations

AI must not be the final authority for hard compliance rules.

------------------------------------------------------------------------

## 9. Compliance Gate

Every campaign must pass deterministic checks before execution.

Example:

``` python
if not offer.email_allowed:
    block("EMAIL_NOT_ALLOWED")

if not offer.geo_allowed:
    block("GEO_NOT_ALLOWED")

if not audience.email_allowed:
    block("AUDIENCE_NOT_APPROVED")

if subscriber.unsubscribed:
    block("SUPPRESSED")

if not campaign.has_unsubscribe:
    block("MISSING_UNSUBSCRIBE")

if not campaign.has_sender_identity:
    block("MISSING_SENDER_IDENTITY")
```

Campaign lifecycle:

``` text
DISCOVERED
→ ELIGIBLE
→ MATCHED
→ GENERATING
→ QA
→ COMPLIANCE
→ SCHEDULED
→ SENDING
→ RUNNING
→ ANALYZING
→ OPTIMIZING
→ COMPLETED
```

Any hard failure becomes `BLOCKED`.

------------------------------------------------------------------------

## 10. Emergency Kill Switch

Implement this before real traffic is connected.

``` text
SYSTEM_ACTIVE = false
```

When disabled: - no campaign can start - workers cannot send - scheduled
campaigns pause - retries stop - dashboard shows the system as halted

The kill switch must not depend on an LLM.

------------------------------------------------------------------------

## 11. Affiliate Network Integration

Use an adapter architecture:

``` text
Awin Adapter
CJ Adapter
Rakuten Adapter
Partnerize Adapter
FlexOffers Adapter
Mock Adapter
        ↓
Common Offer Interface
        ↓
Offer Database
```

Common offer fields:

``` python
class Offer:
    id: str
    network: str
    external_id: str
    name: str
    advertiser: str
    category: str
    description: str
    payout: float
    payout_type: str
    geo: list[str]
    allowed_traffic: list[str]
    email_allowed: bool
    email_approval_required: bool
    epc: float | None
    conversion_rate: float | None
    tracking_url: str
    terms_url: str
    status: str
    last_updated: datetime
```

Initial integration order:

1.  Mock network
2.  Awin
3.  CJ Affiliate
4.  Rakuten Advertising
5.  Partnerize
6.  FlexOffers

Real access depends on account approval, API access, offer terms, and
traffic permissions.

------------------------------------------------------------------------

## 12. Offer Intelligence

First use deterministic filters:

``` sql
SELECT *
FROM offers
WHERE email_allowed = TRUE
AND status = 'active'
AND 'US' = ANY(geo)
ORDER BY epc DESC;
```

Then use AI only on the smaller eligible set.

Potential scoring inputs: - payout - EPC - conversion rate - GEO fit -
audience fit - traffic restrictions - email permission - offer
freshness - historical performance

Never rank an ineligible offer as a valid candidate merely because an AI
model likes it.

------------------------------------------------------------------------

## 13. Audience Intelligence

The audience system must NOT be a random-email scraping system.

Support legitimate sources such as: - owned permission-based audiences -
approved newsletter/publisher relationships - approved traffic
inventory - compliant paid acquisition funnels - other contractually
permitted audience sources

Audience fields:

``` text
id
name
source
provider
geo
category
size
consent_model
consent_verified
email_allowed
status
created_at
```

Subscriber fields:

``` text
id
audience_id
email
country
attributes
consent_source
consent_timestamp
status
unsubscribed_at
```

Use listmonk for subscriber/list/blocklist operations instead of
unnecessarily rebuilding list management.

------------------------------------------------------------------------

## 14. Campaign Engine

Input:

``` text
Offer
+
Audience
+
GEO
+
Allowed traffic
+
Campaign objective
```

Output: - subject - preheader - HTML - CTA - tracking URL - disclosure -
campaign metadata - variants

Generate multiple variants for testing.

The campaign must pass QA and deterministic compliance before sending.

------------------------------------------------------------------------

## 15. Email Infrastructure

Development:

``` text
listmonk
    ↓
Postal
    ↓
local/test environment
```

Production requires separate evaluation of: - domain - DNS - SPF -
DKIM - DMARC - TLS - sender reputation - bounce handling - complaint
handling - unsubscribe/suppression - applicable commercial-email laws -
affiliate-program restrictions

Do not promise inbox placement or bypass spam/promotions filtering.

------------------------------------------------------------------------

## 16. Event Simulator

Create configurable simulated data.

Example:

``` text
10000 recipients
9700 delivered
2900 opens
380 clicks
14 conversions
$420 commission
```

Configurable parameters:

``` text
delivery_rate
open_rate
click_rate
conversion_rate
payout
unsubscribe_rate
bounce_rate
```

Support multiple campaign types so the optimizer can be tested.

------------------------------------------------------------------------

## 17. Tracking Model

Track at minimum:

``` text
message_sent
message_delivered
message_bounced
message_opened
message_clicked
conversion
commission
revenue
cost
unsubscribe
complaint
```

Each event should contain:

``` text
event_id
timestamp
campaign_id
subscriber_id / privacy-safe identifier
offer_id
source
metadata
```

Do not store unnecessary personal data.

------------------------------------------------------------------------

## 18. Financial Model

Core equation:

``` text
Gross Revenue
- Traffic Cost
- Email Infrastructure Cost
- AI/API Cost
- Hosting Cost
- Other Operating Costs
= Net Contribution
```

Primary optimization metric:

**Net contribution per 1,000 eligible recipients**

Secondary metrics:

``` text
CTR
CVR
EPC
Revenue per recipient
Profit per click
Profit per conversion
ROI
Unsubscribe rate
Bounce rate
Complaint rate
```

Do not optimize purely for opens or clicks if they reduce actual
contribution.

------------------------------------------------------------------------

## 19. Optimization Engine

Allowed decisions:

``` text
SCALE
PAUSE
KILL
TEST
REDUCE
RETRY
```

Example:

``` text
Campaign A
CTR = 3.9%
CVR = 3.7%
Positive contribution
→ candidate for scale

Campaign B
CTR = 0.8%
CVR = 0.5%
Negative contribution
→ candidate for pause
```

The optimizer must always respect hard eligibility and compliance
constraints.

------------------------------------------------------------------------

## 20. Dashboard

### Overview

-   Revenue
-   Net Contribution
-   Conversions
-   CTR
-   CVR
-   EPC
-   ROI

### Offers

-   Offer
-   Network
-   Payout
-   EPC
-   CVR
-   Status
-   Revenue

### Campaigns

-   Campaign
-   Audience
-   Offer
-   Recipients
-   CTR
-   CVR
-   Revenue
-   Cost
-   Net Contribution
-   Status

### Experiments

-   Experiment
-   Variant
-   Sample
-   CTR
-   CVR
-   Revenue
-   Contribution
-   Status

### System

-   Agent health
-   Queue depth
-   Failed jobs
-   Database health
-   Email health
-   Kill switch

------------------------------------------------------------------------

## 21. Database Tables

Initial tables:

``` text
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

------------------------------------------------------------------------

## 22. Donation Ledger

Donation automation is a later-stage feature.

Do not donate based on gross revenue.

Use:

``` text
Gross Revenue
- Operating Costs
- Required Reserves
- Taxes / Accounting Obligations
= Distributable Profit
```

Then apply a configurable donation percentage.

Example only:

``` text
Net profit: $1,700
Donation allocation: 20%
Donation: $340
```

Ledger:

``` text
period
gross_revenue
operating_cost
net_profit
donation_percentage
donation_amount
recipient
payment_reference
status
```

Do not automate real donations until accounting, reserves, and business
cash flow are reliable.

------------------------------------------------------------------------

## 23. Security

Never commit: - API keys - affiliate credentials - SMTP credentials -
database passwords - JWT secrets - private keys

Use `.env` and `.env.example`.

Add `.env` to `.gitignore`.

Use least-privilege credentials.

Add authentication before exposing the API/dashboard publicly.

------------------------------------------------------------------------

## 24. Testing Strategy

### Unit tests

-   offer filtering
-   offer scoring
-   eligibility
-   compliance rules
-   financial calculations
-   event processing
-   optimizer decisions

### Integration tests

-   API → PostgreSQL
-   API → Redis
-   API → listmonk
-   network adapter → normalized offer
-   campaign → tracking

### End-to-end test

Prove:

``` text
Mock Offer
 ↓
Audience
 ↓
Campaign
 ↓
Compliance
 ↓
Send
 ↓
Click
 ↓
Conversion
 ↓
Commission
 ↓
Revenue
 ↓
Optimizer
```

------------------------------------------------------------------------

## 25. Development Phases

### Phase 0 --- Architecture

Freeze: - data model - event model - interfaces - adapter structure -
compliance boundaries

No real accounts.

### Phase 1 --- Local Infrastructure

Install: - Docker - PostgreSQL - Redis - n8n - FastAPI - listmonk -
Postal - React

### Phase 2 --- Mock Affiliate Network

Build: - 100 offers - offer API - normalization - database

### Phase 3 --- Audience Simulator

Build: - 10 audiences - 1,000 synthetic subscribers -
consent/suppression records

### Phase 4 --- Campaign Engine

Build: - offer/audience matching - creative generation - variants -
tracking links

### Phase 5 --- Compliance Engine

Build: - eligibility rules - suppression - unsubscribe - GEO
restrictions - traffic restrictions - disclosures - kill switch

### Phase 6 --- Event Simulator

Build: - delivery - clicks - conversions - commissions

### Phase 7 --- Analytics

Build: - campaign metrics - revenue - costs - net contribution - EPC -
ROI

### Phase 8 --- Optimization

Build: - A/B testing - offer selection - audience selection - creative
selection - pause/scale rules

### Phase 9 --- Dashboard

Build: - overview - offers - campaigns - experiments - system health

### Phase 10 --- Real Integrations

Only now connect real affiliate networks and legitimate traffic sources.

------------------------------------------------------------------------

## 26. First Success Milestone

Success is not "the AI agent works."

Success is one complete simulated campaign automatically completing:

``` text
Offer discovered
        ↓
Offer approved
        ↓
Audience matched
        ↓
Campaign generated
        ↓
Compliance passed
        ↓
Campaign executed
        ↓
Click recorded
        ↓
Conversion recorded
        ↓
Commission recorded
        ↓
Revenue calculated
        ↓
Optimizer evaluates result
        ↓
Dashboard updated
```

Then run thousands of simulations.

------------------------------------------------------------------------

## 27. Economic Milestones

Do not begin by assuming \$10,000/month.

Use measurement milestones:

``` text
$10/day
↓
$50/day
↓
$100/day
↓
$300/day
```

These are targets, not guarantees.

If economics are negative at small scale, scaling will generally scale
the losses too.

------------------------------------------------------------------------

## 28. Coding Rules

1.  Write production-quality Python.
2.  Use type hints.
3.  Use Pydantic models at API boundaries.
4.  Separate domain logic from infrastructure.
5.  Keep integrations behind adapters.
6.  Write tests before risky refactors.
7.  Use migrations for database changes.
8.  Never hard-code secrets.
9.  Log important agent decisions.
10. Make important operations idempotent.
11. Prefer deterministic code over unnecessary AI.
12. Keep AI providers replaceable.
13. Keep affiliate networks replaceable.
14. Keep email infrastructure replaceable.
15. Never allow an LLM to bypass the compliance gate.

------------------------------------------------------------------------

## 29. Git Workflow

Branches:

``` text
main
develop
feature/offer-engine
feature/audience-engine
feature/campaign-engine
feature/compliance
feature/analytics
feature/optimizer
feature/dashboard
```

Commit format:

``` text
feat: add offer normalization
fix: prevent duplicate conversion events
test: add compliance eligibility tests
refactor: separate network adapter interface
docs: update local setup
```

------------------------------------------------------------------------

## 30. Environment Variables

Example:

``` env
APP_ENV=development

DATABASE_URL=postgresql://...
REDIS_URL=redis://...

LISTMONK_URL=http://...
LISTMONK_API_KEY=...

POSTAL_URL=http://...

LLM_PROVIDER=ollama
OLLAMA_URL=http://...

SYSTEM_ACTIVE=true
```

Never put real credentials in GitHub.

------------------------------------------------------------------------

## 31. Do Not Build Yet

Do not build these during the first milestone:

-   real paid traffic
-   large-scale real email sending
-   complex multi-cloud deployment
-   Kubernetes
-   expensive vector databases
-   custom ML training
-   complex SMTP optimization
-   dozens of affiliate integrations
-   autonomous financial transfers
-   public SaaS features
-   client management
-   sales CRM
-   manual outreach tooling

First prove the core loop.

------------------------------------------------------------------------

## 32. MVP Definition of Done

-   [ ] Docker environment starts.
-   [ ] PostgreSQL runs.
-   [ ] Redis runs.
-   [ ] FastAPI runs.
-   [ ] Mock affiliate API works.
-   [ ] 100 mock offers load.
-   [ ] Offer normalization works.
-   [ ] Eligibility rules work.
-   [ ] Audience simulator works.
-   [ ] Synthetic subscribers exist.
-   [ ] Campaign generation works.
-   [ ] Compliance gate works.
-   [ ] Kill switch works.
-   [ ] Email execution can be simulated.
-   [ ] Click events are recorded.
-   [ ] Conversion events are recorded.
-   [ ] Commission events are recorded.
-   [ ] Revenue is calculated.
-   [ ] Costs are calculated.
-   [ ] Net contribution is calculated.
-   [ ] Optimizer makes testable decisions.
-   [ ] Dashboard displays results.
-   [ ] Automated tests pass.
-   [ ] Full end-to-end test passes.
-   [ ] No real traffic is required.

------------------------------------------------------------------------

## 33. First Commands

``` bash
git clone <your-repository-url>
cd autonomous-affiliate-engine

cp .env.example .env

docker compose up -d

docker compose ps

pytest

uvicorn apps.api.main:app --reload
```

Exact commands may change as implementation progresses.

------------------------------------------------------------------------

## 34. Engineering Priority

Always prioritize:

``` text
1. Correctness
2. Compliance
3. Testability
4. Observability
5. Economic measurement
6. Automation
7. AI sophistication
8. Scale
```

Do not reverse this order.

A sophisticated autonomous system that loses money or violates
traffic/email rules is not successful.

------------------------------------------------------------------------

## 35. Final Principle

**Build the machine before buying traffic.**

**Prove the economics before scaling.**

**Keep every expensive dependency replaceable.**

**Use AI for reasoning, not deterministic controls.**

**Keep the first complete implementation runnable locally for \$0.**
