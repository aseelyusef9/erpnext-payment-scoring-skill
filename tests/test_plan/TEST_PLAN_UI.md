# UI Testing Plan - ERPNext Payment Scoring Dashboard

## Overview
This document outlines the UI testing strategy for the Payment Scoring Dashboard. Tests are built using Playwright and cover component-level and end-to-end user workflows.

---

## Test Scope

### In Scope
- **Dashboard UI Components**: Tables, filters, search, cards
- **Customer Details Page**: Score display, invoice list, AI insights
- **User Workflows**: Manager reviewing high-risk customers
- **Browser Compatibility**: Chromium, Firefox (WebKit planned)
- **Responsive Design**: Desktop, Tablet, Mobile resolutions
- **Visual Elements**: Buttons, icons, loading states

### Out of Scope
- Backend API logic (covered in API tests)
- Authentication/authorization
- Data creation/modification
- Print/export functionality

---

## Test Architecture

### Test Levels

#### 1. Component Tests
**Purpose**: Test individual UI components in isolation  
**Speed**: Fast (with mock data)  
**Location**: `tests/ui_testing/component/`

#### 2. End-to-End Tests
**Purpose**: Test complete user workflows  
**Speed**: Slower (real data + AI)  
**Location**: `tests/ui_testing/e2e/`

### Test Infrastructure

**Framework**: Playwright (Python)  
**Base Class**: `UITestBase` (tests/ui_testing/conftest.py)  
**Page Objects**: `tests/ui_testing/pages/`
- `dashboard_page.py` - Dashboard interactions
- `customer_details_page.py` - Customer detail page
- `base_page.py` - Common page functionality

**Browser Factory**: `BrowserFactory.py` - Multi-browser support

---

## Environment Configuration

### Environment Variables

```bash
# Browser Configuration
BROWSER=chromium                # Options: chromium, firefox, webkit
HEADLESS=true                   # Options: true, false
SCREEN_WIDTH=1920              # Viewport width
SCREEN_HEIGHT=1080             # Viewport height
UI_SLOW_MO_MS=400              # Slow motion delay (ms)

# Server Configuration
UI_BASE_URL=http://localhost:8000
UI_SKIP_SERVER=false           # Skip starting server if already running
UI_HEALTH_PATH=/health

# Test Mode
USE_MOCK_DATA=true             # Use mock data for fast tests
SKIP_AI_ANALYSIS=true          # Skip Claude AI for component tests
UI_FORCE_AI=false              # Force AI analysis in tests
```

### Test Modes

#### Fast Mode (Component Tests)
```bash
USE_MOCK_DATA=true
SKIP_AI_ANALYSIS=true
HEADLESS=true
UI_SLOW_MO_MS=0
```

#### Visual Mode (Debugging)
```bash
USE_MOCK_DATA=true
SKIP_AI_ANALYSIS=true
HEADLESS=false
UI_SLOW_MO_MS=200
```

#### Full E2E Mode
```bash
USE_MOCK_DATA=false
SKIP_AI_ANALYSIS=false
HEADLESS=true
UI_SLOW_MO_MS=400
```

---

## Component Tests

**File**: `tests/ui_testing/component/test_dashboard_components.py`  
**Purpose**: Verify individual UI elements work correctly  
**Test Class**: `TestDashboardComponents`

### Test Cases

| Test Case | Description | Verification |
|-----------|-------------|--------------|
| TC-UI-C001 | Dashboard loads | Page title, URL, main elements visible |
| TC-UI-C002 | High Risk tab filter | Clicking filter shows high-risk customers only |
| TC-UI-C003 | Medium Risk tab filter | Filter works correctly |
| TC-UI-C004 | Low Risk tab filter | Filter works correctly |
| TC-UI-C005 | Search functionality | Search box filters customer list |
| TC-UI-C006 | View Details button | Button visible and clickable |
| TC-UI-C007 | Customer table loads | Table displays with rows |
| TC-UI-C008 | Stats cards display | Total, Low, Medium, High risk cards visible |
| TC-UI-C009 | Loading state | "Loading customers..." shown during fetch |
| TC-UI-C010 | Empty state | Proper message when no results |

### Execution
```bash
# Run component tests
python tests/ui_testing/component/test_dashboard_components.py

# Run with pytest
pytest tests/ui_testing/component/

# Debug mode (visible browser)
HEADLESS=false python tests/ui_testing/component/test_dashboard_components.py
```

**Expected Duration**: ~7 minutes (with mock data)

---

## End-to-End Tests

**File**: `tests/ui_testing/e2e/test_manager_high_risk_flow.py`  
**Purpose**: Test complete user workflows  
**Test Class**: `TestManagerHighRiskFlowWithFixtures`

### User Story
```
As a Credit Manager
I want to review high-risk customers
So that I can take action on payment delays
```

### Test Workflow

#### TC-UI-E001: Manager High-Risk Flow
**Steps**:
1. Navigate to dashboard
2. Click "High Risk" tab
3. Verify high-risk customers displayed
4. Search for specific customer
5. Click "View Details"
6. Verify customer detail page loads
7. Check payment score displayed
8. Verify invoices table shows data
9. Check AI analysis section (if enabled)
10. Verify action recommendations visible

**Expected Results**:
- Dashboard loads successfully
- Filters work correctly
- Customer details page shows accurate data
- Score matches risk level (0-39 = High Risk)
- AI insights displayed (when enabled)
- All UI elements functional

### Execution
```bash
# Run E2E tests with real data
USE_MOCK_DATA=false python tests/ui_testing/e2e/test_manager_high_risk_flow.py

# Run with AI analysis
USE_MOCK_DATA=false SKIP_AI_ANALYSIS=false python tests/ui_testing/e2e/

# Debug mode
HEADLESS=false python tests/ui_testing/e2e/test_manager_high_risk_flow.py
```

**Expected Duration**: ~10-15 minutes (with real ERPNext + AI)

---

## Page Object Model

### DashboardPage
**File**: `tests/ui_testing/pages/dashboard_page.py`

**Methods**:
- `open()` - Navigate to dashboard
- `verify_page_loaded()` - Confirm page loaded
- `filter_high_risk()` - Click High Risk tab
- `filter_medium_risk()` - Click Medium Risk tab
- `filter_low_risk()` - Click Low Risk tab
- `search_customer(name)` - Search for customer
- `get_rows_count()` - Get number of table rows
- `first_customer_name()` - Get first customer name
- `first_row_text()` - Get first row content
- `click_view_details(row)` - Click View Details button

### CustomerDetailsPage
**File**: `tests/ui_testing/pages/customer_details_page.py`

**Methods**:
- `verify_page_loaded()` - Confirm details page loaded
- `get_score()` - Get payment score value
- `get_risk_level()` - Get risk level text
- `get_customer_name()` - Get customer name
- `verify_invoices_visible()` - Check invoices section
- `verify_ai_analysis_visible()` - Check AI insights section

---

## Browser Support

### Currently Tested Browsers
- ✅ **Chromium** (Chrome, Edge, Brave) - Default and fully tested
- ✅ **Firefox** - Tested in CI/CD pipeline (see `.github/workflows/ui-testing.yaml`)

### Planned Support
- ⏳ **WebKit** (Safari) - BrowserFactory supports it, but not in CI matrix yet

### Configuration
```bash
# Run on Chromium (default)
python tests/ui_testing/component/test_dashboard_components.py

# Run on Firefox
BROWSER=firefox python tests/ui_testing/component/test_dashboard_components.py

```

### CI/CD Browser Matrix
GitHub Actions workflow tests both browsers:
- Chromium + 3 resolutions (desktop, tablet, mobile)
- Firefox + 3 resolutions (desktop, tablet, mobile)

---

## Viewport Testing

### Tested Resolutions (CI/CD)
- ✅ **Desktop**: 1920x1080 (default)
- ✅ **Tablet**: 768x1024
- ✅ **Mobile**: 375x667

### Additional Supported Resolutions
- **Laptop**: 1366x768 (custom)
- **Custom**: Any width/height via environment variables

### Configuration
```bash
# Test on specific resolution
SCREEN_WIDTH=1366 SCREEN_HEIGHT=768 python tests/ui_testing/component/

# Test on tablet (CI resolution)
SCREEN_WIDTH=768 SCREEN_HEIGHT=1024 python tests/ui_testing/component/

# Test on mobile (CI resolution)
SCREEN_WIDTH=375 SCREEN_HEIGHT=667 python tests/ui_testing/component/
```

### CI/CD Viewport Matrix
GitHub Actions tests multiple resolutions:
```yaml
matrix:
  resolution:
    - { name: 'desktop', width: 1920, height: 1080 }
    - { name: 'tablet', width: 768, height: 1024 }
    - { name: 'mobile', width: 375, height: 667 }
```

---

## Test Execution

### Running All UI Tests
```bash
# All UI tests
pytest tests/ui_testing/

# Component tests only
pytest tests/ui_testing/component/

# E2E tests only
pytest tests/ui_testing/e2e/

# Specific test
pytest tests/ui_testing/component/test_dashboard_components.py::TestDashboardComponents::test_dashboard_loads
```

### Debugging Failed Tests

#### Visual Debugging
```bash
HEADLESS=false UI_SLOW_MO_MS=1000 python tests/ui_testing/component/test_dashboard_components.py
```

#### Screenshot on Failure
Tests automatically capture screenshots on failure (TODO: implement)

#### Video Recording
Playwright can record test execution (TODO: implement)

---

## Success Criteria

### Functional
- ✅ All UI elements render correctly
- ✅ All interactions work as expected
- ✅ Data displays accurately
- ✅ Navigation functions properly
- ✅ Filters and search work correctly

### Non-Functional
- ✅ Component tests run in < 10 minutes
- ✅ E2E tests run in < 20 minutes
- ✅ Tests pass consistently (> 95% success rate)
- ✅ No flaky tests
- ✅ Tests work across Chromium and Firefox
- ✅ Tests work across desktop, tablet, and mobile viewports

---

## Known Issues

### Issue 1: Server Startup Time
**Symptom**: Tests wait for server to start  
**Impact**: Adds 5-10 seconds to test execution  
**Workaround**: Use `UI_SKIP_SERVER=true` if server already running  
**Status**: Expected behavior

### Issue 2: AI Analysis Timeout
**Symptom**: E2E tests timeout waiting for AI  
**Impact**: Test failures in slow networks  
**Workaround**: Use `SKIP_AI_ANALYSIS=true` or increase timeout  
**Status**: Known limitation

### Issue 3: Browser Window Size (Fixed)
**Symptom**: Browser doesn't fit screen  
**Impact**: Visual testing difficult  
**Workaround**: Set `no_viewport=True` when `HEADLESS=false`  
**Status**: ✅ Fixed

---

## Test Data Strategy

### Mock Data Mode
**File**: Server generates mock data automatically  
**Customers**: 10-15 mock customers  
**Risk Distribution**: Mix of low, medium, high risk  
**Speed**: Fast (no API calls)

### Real Data Mode
**Source**: Live ERPNext instance  
**Customers**: Real customer data  
**Risk Calculation**: Full AI + rule-based scoring  
**Speed**: Slower (API calls + AI analysis)

---

## Future Enhancements

### High Priority
- [ ] Screenshot capture on test failure
- [ ] Video recording for E2E tests
- [ ] Parallel test execution (locally)
- [ ] Accessibility testing (ARIA labels, keyboard nav)
- [ ] WebKit/Safari in CI pipeline

### Medium Priority
- [ ] Performance testing (page load times)
- [ ] Visual regression testing
- [ ] Test reporting dashboard
- [ ] Local multi-browser/viewport matrix runner

### Low Priority
- [ ] Print layout testing
- [ ] Export functionality tests
- [ ] Multi-language support tests
- [ ] Theme/dark mode testing

---

## Maintenance

### Regular Tasks
**Weekly**:
- Review test execution results
- Fix flaky tests
- Update page objects if UI changed

**Monthly**:
- Update mock data
- Review test coverage
- Optimize slow tests

**Quarterly**:
- Full regression test run
- Browser compatibility check
- Performance baseline update

### Update Triggers
- UI component changes
- New features added
- Bug fixes deployed
- User workflow changes

---

## Reporting

### Test Execution Report
```
======================================================================
UI Test Results - February 5, 2026
======================================================================

Component Tests:
- test_dashboard_loads ......................... PASSED (2.3s)
- test_high_risk_tab_filters ................... PASSED (1.8s)
- test_search_component ........................ PASSED (2.1s)
- test_view_details_button_exists .............. PASSED (1.5s)

Total: 4 passed in 418.67s

E2E Tests:
- test_manager_high_risk_flow .................. PASSED (12.5s)

Total: 1 passed in 12.50s

Overall: 5/5 tests passed (100%)
======================================================================
```

---

**Last Updated**: February 5, 2026  
**Test Coverage**: Component: 80%, E2E: 60%  
**Status**: ✅ Active  
**Framework**: Playwright + Python + unittest
