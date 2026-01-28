# Migration Guide: Formula → AI-Powered Scoring

## Overview

The payment scoring system has been migrated from **formula-based calculations** to **AI-powered analysis** using Claude AI.

---

## What Changed

### Before (Formula-Based) ❌

```python
from app.services import ScoringService, InsightsService

scoring_service = ScoringService()
insights_service = InsightsService()

# Calculate score using formula
score = scoring_service.calculate_customer_score(customer, invoices, payments)
# Formula: 100 - (Overdue × 10) - (AvgDelay × 1)

# Generate rule-based insights
insights = insights_service.generate_insights(score, invoices)
score.insights = insights
```

**Problems:**
- Rigid mathematical formula
- No context consideration
- Fixed thresholds (50, 80)
- Template-based insights
- Not adaptive to patterns

---

### After (AI-Powered) ✅

```python
from app.services import PaymentAIAnalyzer

ai_analyzer = PaymentAIAnalyzer()

# AI analyzes payment behavior
score = ai_analyzer.analyze_customer(customer, invoices)
# Claude AI uses reasoning, not formulas
```

**Benefits:**
- Intelligent reasoning
- Contextual analysis
- Adaptive risk assessment
- Natural language insights
- Explainable decisions

---

## File Status

### 🗑️ Deprecated (Kept for Reference)

| File | Status | Reason |
|------|--------|--------|
| `app/services/scoring.py` | ⚠️ DEPRECATED | Replaced by AI |
| `app/services/insights.py` | ⚠️ DEPRECATED | AI generates insights |

**Not deleted because:**
- Referenced in unit tests
- Useful as historical reference
- May be used for comparison/validation

### ✅ Active (Production)

| File | Purpose |
|------|---------|
| `app/services/payment_ai_analyzer.py` | AI-powered analysis |
| `app/services/claude_client.py` | Claude API client |
| `app/services/analysis_prompt` | AI prompt template |

---

## API Changes

### Endpoints (No Breaking Changes)

All endpoints remain the same, but now use AI internally:

```bash
# These still work exactly the same
GET /api/v1/customers/{id}/score
GET /api/v1/customers/payment-scores
GET /api/v1/customers/high-risk
GET /api/v1/customers/followups
```

**Response format:** Unchanged
**Performance:** 2-5 seconds per customer (AI API call)

---

## Configuration Required

### 1. API Key Setup

Create `.anthropickey` file in project root:
```bash
sk-ant-api03-YOUR_API_KEY_HERE
```

File is already in `.gitignore` ✓

### 2. Install Dependencies

```bash
pip install anthropic>=0.40.0
```

Already in `requirements.txt` ✓

---

## How AI Works

### Input Preparation

The AI analyzer still calculates basic metrics:

```python
customer_data = {
    "customer_name": "Example Corp",
    "total_invoices": 10,
    "invoices_paid_count": 6,
    "overdue_invoices": 3,
    "avg_payment_delay_days": 15.5,
    "payment_reliability_percent": 60.0,
    "total_outstanding_amount": 12500.00
}
```

### AI Analysis

Claude AI receives this data and:
1. **Analyzes patterns** - Not just numbers
2. **Applies business context** - Understanding payment behavior
3. **Makes judgment calls** - Like a credit analyst
4. **Explains reasoning** - In plain language

### Output

```json
{
  "customer_name": "Example Corp",
  "payment_score": 55,
  "risk_level": "Medium",
  "recommended_action": "Friendly reminder",
  "insights": "Customer shows moderate payment delays with 30% of invoices overdue. While not critical, consistent follow-up is recommended to prevent escalation."
}
```

---

## Testing

### Test AI Analysis

```bash
python test_ai_analysis.py
```

### Run Application

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Should see:
```
✓ AI-powered scoring enabled (Claude AI)
```

---

## Rollback (If Needed)

If you need to temporarily go back to formulas:

1. **Restore imports** in `app/api/customers.py`:
```python
from app.services import ScoringService, InsightsService
scoring_service = ScoringService()
insights_service = InsightsService()
```

2. **Add fallback logic**:
```python
try:
    ai_analyzer = PaymentAIAnalyzer()
except Exception:
    ai_analyzer = None
    
# Then use:
if ai_analyzer:
    score = ai_analyzer.analyze_customer(customer, invoices)
else:
    score = scoring_service.calculate_customer_score(customer, invoices, payments)
```

---

## Performance Considerations

### AI Analysis Time
- **Single customer**: 2-5 seconds
- **10 customers**: 20-50 seconds
- **100 customers**: 3-8 minutes

### Optimization Strategies

1. **Use Mock Data for Testing**:
```python
# In .env
USE_MOCK_DATA=True
```

2. **Cache Results** (Future):
```python
# Cache AI results for 1 hour
@cache(ttl=3600)
def get_customer_score(customer_id):
    return ai_analyzer.analyze_customer(...)
```

3. **Async Processing** (Future):
```python
# Queue AI analysis jobs
task = analyze_customer.delay(customer_id)
```

---

## Cost Considerations

Claude API calls cost approximately:
- **Input tokens**: ~100-200 per customer
- **Output tokens**: ~100-150 per customer
- **Cost**: ~$0.003 per customer analysis

For 1000 customers: ~$3.00

---

## Support

### Issues?

1. Check `.anthropickey` file exists and is valid
2. Verify `anthropic` package is installed
3. Check logs for AI errors
4. Fall back to formulas temporarily if needed

### Questions?

See:
- `app/services/payment_ai_analyzer.py` - Implementation
- `app/services/analysis_prompt` - AI instructions
- `CLEANUP_NOTES.md` - Deprecated code info

---

## Summary

✅ **Migration Complete**
- All production endpoints use AI
- Old formula code deprecated but kept
- No breaking API changes
- Better risk assessment
- Natural language insights

🚀 **Ready for Production**
