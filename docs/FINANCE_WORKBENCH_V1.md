# Finance Workbench V1

Finance Workbench adds an evidence-first analysis layer to SBRateBot without
changing the live crawler, scheduler, dashboard API, or rate-update workflow.

## Goal

Every important financial number and conclusion should be traceable:

```text
raw source
  -> source locator
  -> evidence item
  -> calculation
  -> claim
  -> Excel / Word / PowerPoint output
```

The system must be able to answer:

- Where did this number come from?
- What was the as-of date?
- Which row/record and field supplied it?
- Which formula transformed it?
- Which assumptions were applied?
- Which final sentence or chart used it?

## SBRateBot source trace

For the existing deposit-rate snapshots, V1 records:

- source file: `data/latest_rates.json` or `data/previous_rates.json`
- bank
- product
- registration/snapshot date
- field path such as `top_12m`
- original value
- product URL when available
- unit

This creates an auditable link between an AI summary and the underlying rate
record.

## Simulation vs actual

`build_scaled_benchmark()` provides a like-for-like comparison when a
simulation was built on one OPB and the actual purchase/portfolio is smaller.

Example:

```text
simulation OPB 750.8
actual OPB     317.1
scale ratio    0.4223
```

Each simulated cash-flow line can be multiplied by the same ratio to create a
comparison benchmark. This is explicitly recorded as an assumption, not treated
as a guaranteed forecast.

Actual differences in product mix, prepayment, delinquency, fees and timing
still require separate analysis.

## Firm template layer

V1 defines contracts for:

- Excel finance model
- Word research note
- PowerPoint executive one-pager

Every contract requires source trace and human approval.

No existing company template is committed to this public repository. Future
company-template integration should happen only in an approved private/internal
environment.

## Safety / governance

Finance Workbench V1:

- does not make lending, eligibility, pricing or credit decisions
- does not invent missing figures
- does not remove source references
- does not silently alter assumptions
- does not auto-overwrite approved Office files
- requires a human approval step for decision-support outputs

## Current rollout

This commit is contract-only.

It does not modify:

- `crawler/fsb.py`
- `scheduler.py`
- `.github/workflows/rate_update.yml`
- `app.py`
- the live dashboard

Next safe integration:

1. generate source-trace JSON for selected dashboard facts
2. expose a read-only evidence endpoint
3. attach evidence IDs to AI market summaries
4. add export adapters for approved Excel/PPT templates
5. only then allow report-generation automation
