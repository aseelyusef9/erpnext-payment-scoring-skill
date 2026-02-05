# API Testing Plan - ERPNext Payment Scoring

## Overview
This document outlines the testing strategy for the Payment Scoring API endpoints. The API provides customer risk scoring, invoice analysis, and payment behavior insights.

---

## Test Scope

### In Scope
- **Customer Endpoints**: List, retrieve, and score customers
- **Health Check Endpoint**: System health verification
- **API Response Validation**: Status codes, data structure, error handling
- **Mock Testing**: Using TestClient for isolated API tests
- **Authentication**: API key validation and security

### Out of Scope
- ERPNext integration (covered in integration tests)
- UI interactions (covered in UI tests)
- Performance/load testing
- Database operations

---

## API Endpoints Under Test

### 1. Health Check API
**Endpoint**: `GET /health`
**Purpose**: Verify system is running

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| TC-API-001 | Health check returns 200 | Status: 200, contains status field |
| TC-API-002 | Health check response structure | JSON with health info |

---

### 2. Customer List API
**Endpoint**: `GET /api/v1/customers`
**Purpose**: Retrieve list of customers

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| TC-API-010 | List all customers | Status: 200, returns array |
| TC-API-011 | Empty customer list | Status: 200, returns empty array |
| TC-API-012 | Customer data structure | Each customer has required fields |
| TC-API-013 | Pagination support | Limit/offset parameters work |
| TC-API-014 | Error handling | 500 on backend failure |

**Test File**: `tests/api/test_customers_api.py::TestCustomerAPI::test_list_customers`

---

### 3. Customer Score API
**Endpoint**: `GET /api/v1/customers/{customer_id}/score`
**Purpose**: Get payment risk score for specific customer

| Test Case | Description | Expected Result |
|-----------|-------------|-----------------|
| TC-API-020 | Get valid customer score | Status: 200, score 0-100 |
| TC-API-021 | Score with mock data | Returns calculated score |
| TC-API-022 | Score with AI analysis | Returns AI-generated insights |
| TC-API-023 | Customer not found | Status: 404, error message |
| TC-API-024 | Invalid customer ID | Status: 400 or 404 |
| TC-API-025 | No invoices available | Returns score with 0 invoices |
| TC-API-026 | Response structure validation | Contains score, risk_level, invoices, analysis |
| TC-API-027 | Risk level classification | LOW/MEDIUM/HIGH based on score |
| TC-API-028 | AI analysis when enabled | Contains AI insights |
| TC-API-029 | Mock mode behavior | Skips AI when mock enabled |

**Test File**: `tests/api/test_customers_api.py::TestCustomerAPI::test_get_customer_score`

---

## Test Data Strategy

### Mock Data
- **Customer Records**: CUST-001, CUST-002, CUST-003
- **Invoice Records**: Various statuses (Paid, Overdue, Unpaid)
- **Payment Patterns**: On-time, late, mixed

### Test Scenarios
1. **High Risk Customer**
   - Multiple overdue invoices
   - Large outstanding amounts
   - Poor payment history

2. **Medium Risk Customer**
   - Some delayed payments
   - Moderate outstanding balance
   - Mixed payment behavior

3. **Low Risk Customer**
   - All payments on time
   - No overdue invoices
   - Good payment history

---

## Test Environment

### Prerequisites
- FastAPI TestClient configured
- Mock ERPNext client
- Environment variables:
  - `USE_MOCK_DATA=True` for isolated testing
  - `SKIP_AI_ANALYSIS=True` for fast tests

### Dependencies
- `pytest` or `unittest`
- `FastAPI TestClient`
- `unittest.mock` for mocking

---

## Test Execution

### Running API Tests
```bash
# Run all API tests
python -m pytest tests/api/

# Run specific test class
python -m pytest tests/api/test_customers_api.py::TestCustomerAPI

# Run with coverage
python -m pytest tests/api/ --cov=app.api --cov-report=html

# Run as standalone
python tests/api/test_customers_api.py
```

---

## Success Criteria

### Functional
- ✅ All endpoints return correct HTTP status codes
- ✅ Response data structure matches API specification
- ✅ Error handling works correctly
- ✅ Mock mode bypasses external dependencies

### Non-Functional
- ✅ API tests run in < 5 seconds
- ✅ Tests are isolated (no external dependencies)
- ✅ All tests pass consistently
- ✅ Code coverage > 80% for API layer

---

## Known Issues / Limitations

1. **Mock Dependencies**: Tests use mocked ERPNext client, may not catch integration issues
2. **AI Testing**: Claude AI calls are mocked in unit tests
3. **Authentication**: API key validation not fully tested in current suite

---

## Future Enhancements

- [ ] Add authentication/authorization tests
- [ ] Add rate limiting tests
- [ ] Add input validation tests for all parameters
- [ ] Add API versioning tests
- [ ] Add concurrent request handling tests
- [ ] Add API response time assertions

---

## Test Maintenance

### Review Schedule
- After each API endpoint change
- Before each release
- Monthly review of test coverage

### Update Triggers
- New API endpoint added
- Endpoint behavior changed
- New error conditions discovered
- API schema updated

---

**Last Updated**: February 5, 2026  
**Test Coverage**: ~85% of API endpoints  
**Status**: ✅ Active
