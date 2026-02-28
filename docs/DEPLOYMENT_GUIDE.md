# AWS Deployment Guide - Autonomous Pricing Engine

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws configure
   # Enter your access key, secret key, region (recommend ap-south-1 for India)
   # Output format: json
   ```

2. **SAM CLI installed**
   ```bash
   # Windows (using pip)
   pip install aws-sam-cli

   # Verify installation
   sam --version
   ```

3. **Python 3.11+ installed**

---

## Step 1: Deploy IAM Roles for Team Members

From the `infrastructure` directory:

```bash
cd D:\Projects\AI for Bharath\AlgoNauts-Autonomous-Pricing-Engine\infrastructure

# Deploy the IAM roles stack
aws cloudformation deploy \
  --template-file team-iam-roles.yaml \
  --stack-name autonomous-pricing-roles \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-south-1
```

**Output:** This creates 3 roles:
- `autonomous-pricing-developer` - For developers (deploy, update, no delete)
- `autonomous-pricing-viewer` - Read-only access
- `autonomous-pricing-admin` - Full access (for team lead)

### For Team Members to Assume Roles

```bash
# Developer role
aws sts assume-role \
  --role-arn arn:aws:iam::<ACCOUNT_ID>:role/autonomous-pricing-developer \
  --role-session-name dev-session

# Viewer role
aws sts assume-role \
  --role-arn arn:aws:iam::<ACCOUNT_ID>:role/autonomous-pricing-viewer \
  --role-session-name viewer-session

# Admin role
aws sts assume-role \
  --role-arn arn:aws:iam::<ACCOUNT_ID>:role/autonomous-pricing-admin \
  --role-session-name admin-session
```

---

## Step 2: Enable Bedrock Access

**IMPORTANT:** You must enable Bedrock model access in the AWS Console before deploying.

1. Go to AWS Console → Amazon Bedrock
2. Navigate to "Model access" in left sidebar
3. Click "Edit" and enable:
   - Claude 3 Sonnet
   - Claude 3 Haiku (optional, for cost optimization)
4. Click "Save changes"

**Region:** Make sure you enable models in the same region you deploy (ap-south-1 recommended)

---

## Step 3: Build and Deploy Main Application

From the project root:

```bash
cd D:\Projects\AI for Bharath\AlgoNauts-Autonomous-Pricing-Engine\lambdas

# Build the SAM application
sam build

# Deploy with guided setup (first time)
sam deploy --guided

# Follow the prompts:
# - Stack name: autonomous-pricing-engine
# - Region: ap-south-1
# - Confirm changes: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to configuration: Y
```

### For Subsequent Deployments

```bash
sam build && sam deploy
```

---

## Step 4: Verify Deployment

```bash
# List deployed resources
aws cloudformation describe-stacks \
  --stack-name autonomous-pricing-engine \
  --region ap-south-1

# Get API Gateway endpoint
aws cloudformation describe-stacks \
  --stack-name autonomous-pricing-engine \
  --query 'Stacks[0].Outputs[?contains(OutputKey, `API`)].OutputValue' \
  --output text \
  --region ap-south-1

# Expected output:
# https://<api-id>.execute-api.ap-south-1.amazonaws.com
```

---

## Step 5: Test Bedrock Integration

Test that Bedrock is accessible from Lambda:

```bash
# Invoke correction agent with test event
aws lambda invoke \
  --function-name autonomous-pricing-correction-agent \
  --region ap-south-1 \
  --payload fileb://events/correction_event.json \
  response.json

# Check response
cat response.json
```

---

## Step 6: Deploy Frontend (Streamlit)

### Option A: AWS Amplify (Recommended)

```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize Amplify in frontend directory
cd frontend
amplify init

# Add hosting
amplify add hosting
# Choose: Amplify Console
# Choose: Manual deployment

# Deploy
amplify publish
```

### Option B: EC2 (Alternative)

```bash
# Launch t3.micro instance
# Install Python and dependencies
# Run Streamlit on port 8501

# Use security group allowing inbound 8501
```

---

## Architecture After Deployment

```
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Cloud (ap-south-1)                       │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  API Gateway    │───▶│  AI Interface   │                    │
│  │  (HTTP API)     │    │  Lambda         │                    │
│  └─────────────────┘    └────────┬────────┘                    │
│                                  │                              │
│                                  ▼                              │
│                    ┌──────────────────────────┐                 │
│                    │   Amazon Bedrock         │                 │
│                    │   (Claude 3 Sonnet)      │                 │
│                    └──────────────────────────┘                 │
│                                  │                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Lambda Functions (6 total)                 │   │
│  │                                                          │   │
│  │  Market Processor ──▶ Pricing Engine ──▶ Guardrail     │   │
│  │         │                  │                 │          │   │
│  │         ▼                  ▼                 ▼          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │           DynamoDB Tables                        │   │   │
│  │  │  Products │ Decisions │ Corrections             │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                                                          │   │
│  │  Monitoring Agent ──▶ Correction Agent (Bedrock)       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │  EventBridge    │    │  SQS Queue      │                    │
│  │  Event Bus      │    │  (Market Data)  │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cost Estimates (5-Day Prototype)

| Service | Estimated Cost |
|---------|---------------|
| Lambda | ~$1-2 |
| DynamoDB | ~$3-5 |
| API Gateway | ~$0.50 |
| EventBridge | ~$0.10 |
| **Bedrock** | **~$10-15** |
| S3 (if used) | ~$0.50 |
| CloudWatch | ~$2-3 |
| **TOTAL** | **~$17-25** |

---

## Troubleshooting

### Bedrock Access Denied

```
Error: AccessDeniedException when calling bedrock:InvokeModel
```

**Solution:** Enable model access in Bedrock Console (see Step 2)

### Lambda Timeout

```
Error: Task timed out after 30 seconds
```

**Solution:** Increase timeout for AI-heavy functions (already set to 60s for correction_agent)

### DynamoDB Throttling

```
Error: ProvisionedThroughputExceededException
```

**Solution:** Already using PAY_PER_REQUEST billing mode (on-demand)

---

## Next Steps After Deployment

1. ✅ Deploy backend (this guide)
2. ⬜ Build Streamlit frontend
3. ⬜ Test complete flow
4. ⬜ Create demo video
5. ⬜ Prepare PPT
6. ⬜ Submit before March 4