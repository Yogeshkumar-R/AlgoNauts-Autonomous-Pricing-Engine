# AWS Deployment Guide - Manual Operator Control

This runbook is intentionally **manual-first**.
From now on, **you execute every command**. No background agent, bot, or automation should deploy, update, or delete infrastructure unless you explicitly run it.

## Control Policy

- All infra/app changes are command-by-command and operator-approved.
- No unattended deploy scripts.
- No automatic rollouts.
- No destructive commands (`delete-stack`, `sam delete`, table drops) without explicit manual confirmation.

---

## Prerequisites

1. AWS CLI configured for your account:
```bash
aws configure
# Region: us-east-1
# Output: json
```

2. SAM CLI installed:
```bash
sam --version
```

3. Python 3.11+ installed.

4. Bedrock model access enabled in **us-east-1** for:
- `anthropic.claude-haiku-4-5-20251001-v1:0`

---

## Step 1: Deploy IAM Stack (Manual)

From `infrastructure`:

```bash
cd D:\Projects\AI for Bharath\AlgoNauts-Autonomous-Pricing-Engine\infrastructure

aws cloudformation deploy \
  --template-file team-iam-roles.yaml \
  --stack-name autonomous-pricing-roles \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

---

## Step 2: Build and Deploy Application Stack (Manual)

From `lambdas`:

```bash
cd D:\Projects\AI for Bharath\AlgoNauts-Autonomous-Pricing-Engine\lambdas

sam build
sam deploy --guided
```

Use these values during first guided deploy:
- Stack name: `autonomous-pricing-engine`
- AWS Region: `us-east-1`
- Confirm changeset before deploy: `Y`
- Allow SAM IAM role creation: `Y`
- Save configuration: `Y`

For later updates (still manual):

```bash
sam build
sam deploy
```

---

## Step 3: Verify Deployment (Manual)

```bash
aws cloudformation describe-stacks \
  --stack-name autonomous-pricing-engine \
  --region us-east-1

aws cloudformation describe-stacks \
  --stack-name autonomous-pricing-engine \
  --query "Stacks[0].Outputs" \
  --output table \
  --region us-east-1
```

Capture and store:
- API endpoint
- State machine ARN
- DynamoDB table names

---

## Step 4: Smoke Tests (Manual)

From `lambdas`:

```bash
# Seed data
sam local invoke DataSimulatorFunction -e events/market_processor_event.json

# Pricing engine test
sam local invoke PricingEngineFunction -e events/pricing_engine_event.json

# Guardrail test
sam local invoke GuardrailExecutorFunction -e events/guardrail_executor_event.json

# Monitoring test
sam local invoke MonitoringAgentFunction -e events/monitoring_agent_event.json

# Correction (Bedrock path)
sam local invoke CorrectionAgentFunction -e events/correction_agent_event.json

# AI interface test
sam local invoke AIInterfaceFunction -e events/ai_interface_query_event.json
```

If invoking deployed lambdas directly:

```bash
aws lambda invoke \
  --function-name autonomous-pricing-correction-agent \
  --region us-east-1 \
  --payload fileb://events/correction_agent_event.json \
  response.json
```

---

## Step 5: Frontend Run (Manual)

From `dashboard`:

```bash
cd D:\Projects\AI for Bharath\AlgoNauts-Autonomous-Pricing-Engine\dashboard
pip install -r requirements.txt
streamlit run app.py
```

Set `API_BASE` in your `.env` to the deployed API URL before running.

---

## Change Management (Operator-Only)

Before any deploy:

```bash
git status
git diff
sam validate
```

Deploy only after you review those outputs.

---

## Rollback (Manual)

If a deploy fails:

```bash
aws cloudformation describe-stack-events \
  --stack-name autonomous-pricing-engine \
  --region us-east-1 \
  --max-items 30
```

Then fix and redeploy manually. Do not run delete commands unless you explicitly decide to.

---

## Notes

- This guide replaces any prior assumption of auto-managed deployment.
- Operating model is now: **you approve, you execute, you verify**.
