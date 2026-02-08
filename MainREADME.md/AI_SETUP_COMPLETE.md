# 🤖 AI-Powered Payment Scoring - Setup Complete!

## What Changed

Your system now uses **Claude AI** for intelligent payment risk analysis instead of rigid mathematical formulas.

### ✅ Completed Updates:

1. **AI Analyzer Created** ([payment_ai_analyzer.py](app/services/payment_ai_analyzer.py))
   - Replaces formula-based scoring with AI reasoning
   - Uses Claude Sonnet 4 for analysis
   - Includes fallback handling if AI is unavailable

2. **API Endpoints Updated** (app/api/customers.py)
   - `/api/v1/customers/{id}/score` - AI-driven scoring
   - `/api/v1/customers/payment-scores` - AI for all customers
   - `/api/v1/customers/high-risk` - AI risk assessment
   - `/api/v1/customers/followups` - AI-determined actions

3. **Dependencies Installed**
   - Added `anthropic>=0.40.0` package
   - Claude API client configured

---

## 🔑 Setup Your Claude API Key

### Step 1: Get API Key from Anthropic

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to: **API Keys**
4. Click: **Create Key**
5. Copy your API key

### Step 2: Add API Key to Project

**Option A: Create `.anthropickey` file** (Recommended)

```bash
cd c:/Users/USER/erpnext-payment-scoring-skill
echo "your-api-key-here" > .anthropickey
```

**Option B: Use Environment Variable**

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Step 3: Test AI Connection

```bash
python -c "from app.services.claude_client import get_claude_client; client = get_claude_client(); print('✓ Claude API connected!')"
```

---

## 🧪 Test AI-Driven Scoring

### 1. Start the Application

```bash
cd c:/Users/USER/erpnext-payment-scoring-skill
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Create High-Risk Test Customer

```bash
python create_test_customers.py
```

Choose option **1** for High Risk customer.

### 3. Test AI Analysis

```bash
# Replace CUSTOMER-ID with the ID from step 2
curl http://localhost:8000/api/v1/customers/CUSTOMER-ID/score
```

**Expected AI Response:**

```json
{
  "customer_id": "High Risk Customer 1234",
  "customer_name": "High Risk Customer 1234",
  "score": 25,
  "risk_level": "high",
  "action": "Immediate follow-up",
  "avg_payment_delay": 28.33,
  "payment_reliability": 16.67,
  "total_invoices": 6,
  "total_paid": 1,
  "total_outstanding": 27500.00,
  "overdue_count": 5,
  "insights": "Customer shows severe payment issues with 83% of invoices overdue and consistent late payments averaging 28 days. Outstanding balance of $27,500 requires immediate credit review and collection action."
}
```

---

## 📊 How AI Analysis Works

### Input Data (Aggregated Metrics):

```json
{
  "customer_name": "Example Corp",
  "total_invoices": 10,
  "invoices_paid_count": 4,
  "overdue_invoices": 6,
  "avg_payment_delay_days": 25.5,
  "payment_reliability_percent": 40.0,
  "total_outstanding_amount": 15000.00
}
```

### AI Processing:

- Claude analyzes payment patterns
- Considers:
  - Payment reliability vs industry norms
  - Severity of delays
  - Outstanding balance risk
  - Payment trend trajectory
- Uses business reasoning (not formulas)

### Output (Structured JSON):

```json
{
  "payment_score": 35,
  "risk_level": "High",
  "recommended_action": "Immediate follow-up",
  "insights": "Business-friendly explanation..."
}
```

---

## 🛡️ Fallback Behavior

If Claude API fails:

```json
{
  "score": 50,
  "risk_level": "medium",
  "action": "Friendly reminder",
  "insights": "AI analysis unavailable. Using fallback assessment."
}
```

---

## 🎯 Risk Assessment Criteria

**High Risk (Score < 50):**
- Payment reliability < 40%
- 3+ overdue invoices
- Average delay > 20 days
- High outstanding balance

**Medium Risk (Score 50-79):**
- Payment reliability 40-70%
- 1-2 overdue invoices
- Average delay 7-20 days
- Moderate outstanding

**Low Risk (Score ≥ 80):**
- Payment reliability > 70%
- 0-1 overdue invoices
- Average delay < 7 days
- Low outstanding

---

## 📝 Configuration

### Model Settings

File: [payment_ai_analyzer.py](app/services/payment_ai_analyzer.py#L12)

```python
MODEL_NAME = "claude-sonnet-4-20250514"  # Current model
```

### Temperature Setting

```python
temperature=0.2  # Low for consistent, reliable results
```

### Analysis Prompt

File: [analysis_prompt](app/services/analysis_prompt)

Contains detailed instructions for Claude on how to analyze payment behavior.

---

## 🚀 Next Steps

1. **Add your API key** to `.anthropickey`
2. **Restart the application**
3. **Create test customers** with different risk profiles
4. **Test AI scoring** via API or dashboard
5. **Compare AI insights** vs old formula-based scoring

---

## 💡 Benefits of AI-Driven Scoring

✅ **Contextual Analysis** - Understands business context
✅ **Natural Language Insights** - Human-readable explanations
✅ **Flexible Reasoning** - Adapts to complex scenarios
✅ **No Rigid Formulas** - Mimics credit analyst thinking
✅ **Explainable Results** - Clear reasoning for decisions

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

```bash
pip install anthropic
```

### "API key not found"

Create `.anthropickey` file:
```bash
echo "sk-ant-..." > .anthropickey
```

### "Rate limit exceeded"

Add delay between requests or upgrade your Anthropic plan.

### AI returns unexpected format

Check [analysis_prompt](app/services/analysis_prompt) - AI instructions might need tuning.

---

**Your system is now powered by Claude AI! 🚀**
