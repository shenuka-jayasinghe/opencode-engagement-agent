# AWS Security Analysis Skill

AWS security expert: analyze, detect, improve security posture (read-only). Services: CloudTrail, Security Hub, IAM Access Analyzer, GuardDuty, Config.

## Activation

Triggers on: security analysis/audit, findings/vulnerabilities, IAM permissions/policies/access, CloudTrail events, compliance, threat detection, anomalies, resource config review.

## Configuration

Store in `engagement_agent_config.json` → `aws_security`:
- `delegated_admin_profile`: Security/Audit delegated admin (for Security Hub, GuardDuty, **CloudTrail Lake queries**)
- `management_account_profile`: Org management (for org-wide queries, discovering CloudTrail Lake event store)
- `cloudtrail_lake_event_data_store_id`: UUID only (discover via mgmt account if missing)
- `region`: AWS region

```json
{"aws_security": {"delegated_admin_profile": "<profile>", "management_account_profile": "<profile>", "cloudtrail_lake_event_data_store_id": "<uuid>", "region": "<region>"}}
```

## Core Capabilities

### 1. CloudTrail Lake (SQL-like queries, async 10-60s)

**CRITICAL: Use delegated admin profile** (has cloudtrail:StartQuery/GetQueryResults). Mgmt profile only for discovering event store ID.

#### Pattern
```bash
QUERY_ID=$(aws-vault exec <delegated-admin> -- aws cloudtrail start-query \
  --query-statement "SELECT ... FROM <store-id> WHERE eventTime > 'YYYY-MM-DD HH:MM:SS' LIMIT N" \
  --region <region> --query 'QueryId' --output text)
sleep 20  # Wait 15-30s
aws-vault exec <delegated-admin> -- aws cloudtrail get-query-results --query-id $QUERY_ID --region <region>
```

#### Common Queries
- **Failed auth**: `WHERE errorCode IN ('AccessDenied','UnauthorizedOperation','InvalidClientTokenId')`
- **Root usage**: `WHERE userIdentity.type = 'Root'`
- **Console logins**: `WHERE eventName = 'ConsoleLogin'`
- **API call freq**: `SELECT eventName, COUNT(*) ... GROUP BY eventName, userIdentity.principalId ORDER BY COUNT(*) DESC`
- **Specific account**: `WHERE recipientAccountId = '<account-id>'`

### 2. Security Hub
`aws securityhub get-findings --filters '{"RecordState":[{"Value":"ACTIVE","Comparison":"EQUALS"}],"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}]}'`
Filter by: RecordState, SeverityLabel, ComplianceStatus

### 3. IAM Access Analyzer
`list-analyzers`, `list-findings --analyzer-arn <arn>`, `get-finding --id <id>`

### 4. GuardDuty
`list-detectors`, `list-findings --detector-id <id> --finding-criteria '{"Criterion":{"severity":{"Gte":7}}}'`, `get-findings`

### 5. Config Compliance
`describe-compliance-by-config-rule`, `get-compliance-details-by-config-rule --config-rule-name <rule> --compliance-types NON_COMPLIANT`

### 6. IAM Credential Reports
`iam generate-credential-report`, wait, then `iam get-credential-report --query 'Content' --output text | base64 -d`

### 7. Organizations
`organizations list-accounts`, `describe-organization` (use mgmt profile)

## Workflow
1. Scope → 2. Verify config (prompt if missing) → 3. Select service(s) → 4. Execute queries (aws-vault) → 5. Wait (CloudTrail Lake: 15-30s) → 6. Analyze → 7. Recommend

## Constraints
- READ-ONLY, aws-vault required, **delegated admin for CloudTrail Lake** (mgmt only for discovery), async awareness (wait 15-30s), save discovered IDs to config

## Discovery
`aws cloudtrail list-event-data-stores` (mgmt profile) → extract UUID → save to config → use delegated admin for all queries

## Best Practices
- Start broad → narrow; prioritize CRITICAL/HIGH severity
- Consider business context; compare with historical data
- Cross-reference services; provide actionable insights with next steps
- Map to compliance frameworks (CIS, PCI-DSS)

## Efficiency Tips
- **CloudTrail Lake**: Delegated admin only (ReadOnly lacks cloudtrail:StartQuery); save QueryID immediately; wait 15-20s (simple) or 30-60s (complex); use `LIMIT`; cache IDs
- **Account IDs**: Get from `~/.aws/config` (sso_account_id) or `organizations list-accounts`; cache frequently-used
- **Query structure**: Always `eventTime > 'YYYY-MM-DD HH:MM:SS'`; `ORDER BY eventTime DESC`; extract UUID only from ARN (last `/` segment)
- **Error handling**: Check profile on permission errors; verify exists in `~/.aws/config`

## Key Reminders
- Activate venv, use config file, delegated admin for CloudTrail Lake (mgmt only for discovery)
- CloudTrail Lake = async (wait before results)
- Cache IDs to config; provide security/business context; explain actions
