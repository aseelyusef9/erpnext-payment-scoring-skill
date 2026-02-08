# Integration Testing Plan - ERPNext Payment Scoring

## Overview
This document outlines the integration testing strategy for the Payment Scoring system with external services (ERPNext, Claude AI). Integration tests verify that our application correctly communicates with third-party systems.

---

## Test Scope

### In Scope
- **ERPNext API Integration**: Customer and invoice data retrieval
- **Claude AI Integration**: Payment risk analysis
- **End-to-End Data Flow**: From ERPNext to AI analysis to scoring
- **Error Handling**: Connection failures, API errors, timeouts
- **Configuration**: API credentials and environment setup

### Out of Scope
- UI functionality (covered in UI tests)
- Pure API logic (covered in API tests)
- ERPNext internal logic
- Claude AI internal processing

---

## Integration Points

### 1. ERPNext Integration
**Service**: `app.erpnext.client.ERPNextClient`
**External Dependency**: ERPNext server at `http://localhost:8080`

#### Test Coverage

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| TC-INT-001 | ERPNext connection test | Successfully connects to ERPNext |
| TC-INT-002 | List customers from ERPNext | Returns array of customers |
| TC-INT-003 | Get customer details | Returns customer data with all fields |
| TC-INT-004 | Get customer invoices | Returns invoices for customer |
| TC-INT-005 | Get payments for customer | Returns payment records |
| TC-INT-006 | Handle customer not found | Raises appropriate exception |
| TC-INT-007 | Handle API errors | Proper error handling and logging |
| TC-INT-008 | Handle network timeout | Timeout error caught and handled |
| TC-INT-009 | Invalid credentials | Authentication error raised |
| TC-INT-010 | API rate limiting | Handles rate limit responses |

**Test File**: `tests/integration/test_erpnext_integration.py`

---

### 2. Claude AI Integration
**Service**: `app.services.payment_ai_analyzer.PaymentAIAnalyzer`
**External Dependency**: Claude AI API (Anthropic)

#### Test Coverage

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| TC-INT-020 | AI analysis request | Successfully gets AI insights |
| TC-INT-021 | Parse AI response | Correctly extracts score and reasoning |
| TC-INT-022 | Handle AI timeout | Falls back to rule-based scoring |
| TC-INT-023 | Handle invalid API key | Proper error message |
| TC-INT-024 | Handle rate limiting | Retry logic or fallback |
| TC-INT-025 | Validate AI prompt format | Prompt contains all required data |
| TC-INT-026 | AI response parsing errors | Fallback to default scoring |
| TC-INT-027 | Skip AI when disabled | Uses rule-based only when SKIP_AI=true |

**Test File**: `tests/services/test_ai_analyzer.py`

---

### 3. End-to-End Data Flow
**Flow**: ERPNext → Data Processing → AI Analysis → Score Calculation → API Response

#### Test Coverage

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| TC-INT-040 | Complete scoring flow | Customer score calculated correctly |
| TC-INT-041 | Real customer data | Works with actual ERPNext data |
| TC-INT-042 | Mock vs Real comparison | Mock and real modes produce valid results |
| TC-INT-043 | Error propagation | Errors handled at each integration point |
| TC-INT-044 | Data transformation | ERPNext data correctly formatted for AI |
| TC-INT-045 | Response aggregation | AI + rules combined properly |

---

## Test Environment Configuration

### ERPNext Test Environment
```bash
ERPNEXT_URL=http://localhost:8080
ERPNEXT_API_KEY=your_api_key_here
ERPNEXT_API_SECRET=your_api_secret_here
```

### Claude AI Test Environment
```bash
ANTHROPIC_API_KEY=your_claude_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### Test Modes
```bash
# Integration tests with real services
USE_MOCK_DATA=false
SKIP_AI_ANALYSIS=false

# Integration tests with mocked services
USE_MOCK_DATA=true
SKIP_AI_ANALYSIS=true
```

---

## Test Execution

### Prerequisites
1. **ERPNext Running**: Ensure ERPNext server is accessible
2. **Valid Credentials**: API keys configured in `.env`
3. **Network Access**: No firewall blocking API calls
4. **Test Data**: Sample customers and invoices in ERPNext

### Running Integration Tests

```bash
# Run all integration tests
python -m pytest tests/integration/

# Run ERPNext integration tests only
python tests/integration/test_erpnext_integration.py

# Run AI analyzer tests
python tests/services/test_ai_analyzer.py

# Run with real services (requires credentials)
USE_MOCK_DATA=false python -m pytest tests/integration/

# Run with mock data (fast, no external calls)
USE_MOCK_DATA=true python -m pytest tests/integration/
```

### Skip Conditions
Tests are automatically skipped when:
- ERPNext credentials not configured
- ERPNext server not accessible
- Claude AI API key missing
- Network connectivity issues

---

## Test Data Management

### ERPNext Test Data
- **Customers**: Use existing ERPNext customers (limit=5 for tests)
- **Invoices**: Real invoice data from ERPNext
- **Payments**: Actual payment records

### Mock Data Strategy
```python
# High risk customer (for testing)
mock_high_risk_invoices = [
    # Multiple overdue invoices
    # Large outstanding amounts
]

# Low risk customer
mock_low_risk_invoices = [
    # All paid on time
    # No outstanding amounts
]
```

---

## Success Criteria

### Functional Requirements
- ✅ Successfully connects to ERPNext
- ✅ Retrieves customer data accurately
- ✅ Gets invoice and payment data
- ✅ AI integration works when enabled
- ✅ Fallback logic works when AI disabled
- ✅ Error handling prevents crashes

### Non-Functional Requirements
- ✅ Integration tests complete in < 30 seconds (with mocks)
- ✅ Real integration tests complete in < 2 minutes
- ✅ Tests can run with or without external services
- ✅ Clear skip messages when dependencies unavailable

---

## Error Scenarios Testing

### Network Errors
- Connection timeout
- Connection refused
- DNS resolution failure

### API Errors
- 401 Unauthorized (invalid credentials)
- 404 Not Found (customer/invoice missing)
- 429 Rate Limit Exceeded
- 500 Internal Server Error
- Malformed JSON response

### Data Errors
- Missing required fields
- Invalid data types
- Empty response
- Unexpected data structure

---

## Monitoring & Logging

### Test Execution Logs
```
[OK] ERPNext credentials loaded successfully
[OK] Claude AI credentials loaded successfully
[INFO] Using REAL data from ERPNext
[INFO] AI analysis enabled
[OK] Customer CUST-001 retrieved successfully
[OK] 15 invoices fetched for CUST-001
[OK] AI analysis completed in 2.3s
```

### Failure Indicators
- `[ERROR]` - Integration failure
- `[SKIP]` - Test skipped due to missing dependency
- `[WARN]` - Non-critical issue detected

---

## Known Issues & Workarounds

### Issue 1: ERPNext Connection Timeout
**Symptom**: Tests fail with timeout error  
**Workaround**: Increase timeout in `ERPNextClient` config  
**Status**: Open

### Issue 2: Claude AI Rate Limiting
**Symptom**: 429 errors during test runs  
**Workaround**: Use `SKIP_AI_ANALYSIS=true` for rapid testing  
**Status**: Working as designed

### Issue 3: Mock Data Drift
**Symptom**: Mock data doesn't match real ERPNext structure  
**Workaround**: Periodically sync mock data with production schema  
**Status**: Needs regular maintenance

---

## Future Enhancements

- [ ] Add retry logic testing
- [ ] Add circuit breaker pattern tests
- [ ] Add performance benchmarking
- [ ] Add data consistency validation
- [ ] Add webhook integration tests
- [ ] Add background job testing
- [ ] Add database transaction tests

---

## Dependencies

### Python Packages
```
requests>=2.31.0
anthropic>=0.40.0
pytest>=7.4.0
python-dotenv>=1.0.0
```

### External Services
- ERPNext v14+ (running on localhost:8080)
- Claude AI (Anthropic API)

---

## Test Maintenance Schedule

### Daily
- Monitor test execution results
- Check for flaky tests

### Weekly
- Review integration failures
- Update mock data if needed

### Monthly
- Verify credentials still valid
- Update test data sets
- Review and update test cases

### Quarterly
- Full integration test review
- Performance baseline update
- Documentation review

---

**Last Updated**: February 5, 2026  
**Test Coverage**: ~70% of integration points  
**Status**: ✅ Active  
**Critical Dependencies**: ERPNext API, Claude AI
