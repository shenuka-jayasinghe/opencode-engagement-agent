# AWS FinOps Analysis Skill

AWS FinOps expert: cost optimization, billing analysis, financial operations (read-only). Services: Cost Explorer, CUR, Budgets, Savings Plans, Reserved Instances.

## Activation

Triggers on: cost analysis, billing, spending patterns, anomalies, RI/SP opportunities, optimization, budgets, forecasting, savings history, rightsizing, tag allocation.

## Configuration

Read from `engagement_agent_config.json` → `aws_security`:
- `management_account_profile`: Org management/payer account (for consolidated billing, Cost Explorer)
- `region`: Default AWS region (required even for global services)

```json
{"aws_security": {"management_account_profile": "<profile>", "region": "<region>"}}
```

## Core Capabilities

### 1. Cost and Usage Analysis

**Use management account profile** for Cost Explorer queries (consolidated billing).

#### Cost Metrics

| Metric | Definition | Use Case | Formula |
|--------|------------|----------|---------|
| **UnblendedCost** ✅ | Actual invoice amount (post all discounts/credits) | Financial reporting, budgets, invoice reconciliation | DEFAULT |
| **BlendedCost** | Pre-partner-discount cost (includes RI/SP) | Internal allocation, cross-org comparison | - |
| **Partner Discount** | Difference between metrics | Quantify partner program value | BlendedCost - UnblendedCost |

**Default to UnblendedCost** (matches invoices). Query both to show partner value.

#### Query Base Pattern
```bash
unset AWS_VAULT AWS_VAULT_SESSION_TOKEN_EXPIRATION AWS_SESSION_TOKEN AWS_SECRET_ACCESS_KEY AWS_ACCESS_KEY_ID && \
  aws-vault exec <mgmt-profile> -- aws ce get-cost-and-usage \
  --time-period Start=YYYY-MM-DD,End=YYYY-MM-DD --granularity MONTHLY \
  --metrics UnblendedCost [BlendedCost] [--group-by TYPE,KEY] --region <region>
```

**Key Dimensions**: `SERVICE`, `LINKED_ACCOUNT`, `TAG:KeyName`, `RECORD_TYPE` (shows discounts/credits), `USAGE_TYPE`, `INSTANCE_TYPE`
**Granularity**: `DAILY` (detail), `MONTHLY` (trends)

### 2. Anomaly Detection
`aws ce get-anomaly-monitors`, `aws ce get-anomalies --date-interval Start=X,End=Y`

### 3. RI & Savings Plans
- **Coverage/Utilization**: `get-reservation-{coverage|utilization}`, `get-savings-plans-utilization`
- **Recommendations**: `get-reservation-purchase-recommendation --service EC2 --lookback-period-in-days SIXTY_DAYS --term-in-years ONE_YEAR --payment-option NO_UPFRONT`
- **SP Recommendations**: `get-savings-plans-purchase-recommendation --savings-plans-type COMPUTE_SP`
- **Targets**: Coverage >70%, Utilization >95%

### 4. Rightsizing
`aws ce get-rightsizing-recommendation --service AmazonEC2`

### 5. Budgets
`aws budgets describe-budgets --account-id <id>`, `describe-budget --budget-name <name>`

### 6. Historical Savings (Confluence/Jira/Slack)
```bash
cd /Users/shenuka/git/daemon/engagement-agent && source venv/bin/activate
python3 tools/confluence_tool.py search SDRY "cost savings|$" --limit 20
python3 tools/jira_tool.py get-summary --project-key SD --days 90 | grep -i "cost\|savings\|$"
python3 tools/slack_tool.py search "cost savings|$" --count 50
```

## Workflow
1. Scope → 2. Verify config → 3. Gather data (Cost Explorer, Anomalies, RI/SP, Confluence/Jira/Slack) → 4. Analyze & correlate → 5. Recommend optimizations

## Constraints
- READ-ONLY, aws-vault required, use mgmt account for billing, activate venv for tools, read config from `engagement_agent_config.json`

## Best Practices
- **Time ranges**: 30/60/90 days; **Granularity**: DAILY (detail), MONTHLY (trends)
- **Metrics**: UnblendedCost (default, matches invoices), query both for partner discount value
- **Tags**: Leverage cost allocation tags; **Grouping**: Start with SERVICE, drill to USAGE_TYPE/INSTANCE_TYPE
- **Historical context**: Cross-ref AWS data with Confluence/Jira/Slack (search "$" for cost discussions)
- **Rightsizing first**: More impact than commitments; **RI/SP**: Review monthly, start conservative (1yr, no-upfront)
- **Partner discounts**: Solution Provider (3-7% auto), EDP (negotiated); BlendedCost - UnblendedCost = partner value

## Troubleshooting Console vs API Discrepancies

| Pattern | Cause | Action |
|---------|-------|--------|
| API > Console by 3-7% | BlendedCost vs UnblendedCost | Use UnblendedCost (invoice match) |
| Consistent $X diff | Partner discount/credit | Check RECORD_TYPE dimension |
| Current month variance | Charges posting | Wait 24-48h post-month-end |
| Random variance | Date boundaries/filters | Verify time-period params |

**Diagnostics**: Query both metrics + RECORD_TYPE dimension. Date format: `Start=2025-12-01,End=2026-01-01` (exclusive end). Console=local TZ, API=UTC.

## Key Reminders
- Activate venv, use config file, mgmt profile for billing
- Default UnblendedCost (invoice); query both for partner value
- Balance cost vs performance; verify metric in existing reports before flagging issues
- Partner discounts = automatic ongoing value beyond technical optimization
