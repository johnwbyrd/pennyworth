# Cost Analysis

## Assumptions
- **LLM:** Claude (or similar low-cost Bedrock model)
- **Monthly Usage:** 1,000 queries per month
- **Average Input/Output Size:** 2,000 input tokens, 1,000 output tokens per query
- **Lambda Memory:** 1 GB, average duration 5 seconds per invocation
- **API Gateway:** HTTP API
- **DynamoDB:** On-demand, minimal storage
- **CloudWatch:** Default log retention, minimal custom metrics

## AWS Service Costs (2024)

### 1. **AWS Lambda**
- **Free tier:** 1M requests and 400,000 GB-seconds per month
- **Pricing:** $0.20 per 1M requests, $0.0000166667 per GB-second
- **Calculation:**
  - 1,000 invocations × 5 sec × 1 GB = 5,000 GB-seconds
  - 5,000 GB-seconds is well below the free tier
  - **Cost:** $0 (within free tier)

### 2. **API Gateway (HTTP API)**
- **Pricing:** $1.00 per 1M requests (first 300M), $0.09/GB data out
- **Calculation:**
  - 1,000 requests × $1.00/1,000,000 = $0.001
  - Data out: Assume 10 KB per response × 1,000 = 10 MB = 0.01 GB × $0.09 = $0.0009
  - **Cost:** ~$0.002 (rounding up)

### 3. **DynamoDB**
- **Pricing:** $1.25 per million write request units, $0.25 per million read request units, $0.25/GB-month storage
- **Calculation:**
  - Assume 2 reads and 1 write per query: 2,000 reads, 1,000 writes
  - Reads: 2,000 × $0.25/1,000,000 = $0.0005
  - Writes: 1,000 × $1.25/1,000,000 = $0.00125
  - Storage: Negligible (<1 MB)
  - **Cost:** ~$0.002

### 4. **CloudWatch Logs**
- **Pricing:** $0.50 per GB ingested, $0.03 per GB-month stored (first 5 GB free for 3 months)
- **Calculation:**
  - Assume 1 KB log per invocation: 1,000 KB = 1 MB = 0.001 GB
  - Ingestion: 0.001 GB × $0.50 = $0.0005
  - Storage: Negligible (within free tier)
  - **Cost:** ~$0.001

### 5. **Bedrock Model (Claude or Cheaper)**
- **Claude Instant (2024):** $1.63 per 1M input tokens, $5.51 per 1M output tokens
- **Calculation:**
  - Input: 1,000 queries × 2,000 tokens = 2,000,000 tokens
  - Output: 1,000 queries × 1,000 tokens = 1,000,000 tokens
  - Input cost: 2 × $1.63 = $3.26
  - Output cost: 1 × $5.51 = $5.51
  - **Total Bedrock cost:** $8.77

## **Summary Table**
| Service         | Monthly Cost (est.) |
|----------------|---------------------|
| Lambda         | $0 (free tier)      |
| API Gateway    | $0.002              |
| DynamoDB       | $0.002              |
| CloudWatch     | $0.001              |
| Bedrock (Claude Instant) | $8.77     |
| **Total**      | **$8.78**           |

## **Notes and Optimization Tips**
- **Bedrock model cost dominates**; all other AWS costs are negligible at this scale.
- **CloudWatch**: Costs can rise if you log large payloads or keep logs long-term. Set log retention to 7 days or less to minimize storage costs.
- **Lambda**: If you exceed the free tier, costs are still very low for this usage pattern.
- **API Gateway**: Data transfer costs are negligible unless you return very large responses.
- **DynamoDB**: Remains negligible unless you store large amounts of metadata or usage data.
- **If you use a cheaper model (e.g., Titan)**, costs can be even lower (Titan: ~$0.50–$0.70/month for this usage).

## **Conclusion**
For 1,000 queries per month using Claude Instant or a similar Bedrock model, your total AWS bill will be **under $9/month**, with almost all of that cost coming from the Bedrock model itself. All other infrastructure costs are effectively negligible at this scale. 