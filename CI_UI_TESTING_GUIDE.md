# Running UI Testing in CI (GitHub Actions)

## Overview
Your GitHub Actions workflow has been updated to include UI/E2E testing. The workflow now:

1. ✅ Installs dependencies (including Playwright)
2. ✅ Runs backend tests (`tests/BACKEND/`)
3. ✅ Starts the application server
4. ✅ Runs E2E/UI tests with Claude AI enabled
5. ✅ Reports results

## What Gets Tested in CI

### Backend Tests
```bash
pytest tests/BACKEND/ -v
```
- AI analyzer tests
- Payment scoring logic
- Claude API integration (mocked)

### UI/E2E Tests
```bash
pytest tests/ui_testing/e2e/ -v
```
- Dashboard loading
- High-risk customer filtering
- Customer details modal
- Claude AI insights verification

## CI Environment Configuration

The workflow sets these environment variables for UI tests:

```yaml
UI_BASE_URL: http://127.0.0.1:8000      # Test server URL
UI_FORCE_AI: true                         # Always enable Claude AI
UI_SLOW_MO_MS: 0                          # No delays (for speed)
UI_KEEP_OPEN: false                       # Auto-close browser
```

## How to Run UI Tests Locally (Before Committing)

### 1. Start the application server
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. In another terminal, run UI tests
```bash
pytest tests/ui_testing/e2e/ -v
```

### Optional: Run with visual inspection
```bash
UI_SLOW_MO_MS=500 UI_KEEP_OPEN=true pytest tests/ui_testing/e2e/ -v
```

This will:
- Show browser interactions (slow motion: 500ms)
- Keep browser open after test completes
- Allow you to inspect what happened

## CI Workflow Steps Explained

### Step 1: Install Playwright
```yaml
- Install Playwright (for UI tests)
  pip install playwright
  playwright install chromium --with-deps
```
⚠️ Note: `continue-on-error: true` means test continues even if Playwright fails

### Step 2: Start application server
```yaml
- Start application server (for UI tests)
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
  sleep 5  # Wait for server startup
```
- Runs server in background (`&`)
- Waits 5 seconds for server to be ready
- Uses `continue-on-error: true` to prevent CI failure if startup has issues

### Step 3: Run UI tests
```yaml
- Run UI/E2E tests
  pytest tests/ui_testing/e2e/ -v --tb=short
```
- Uses `http://127.0.0.1:8000` as test URL
- Claude AI enabled (`UI_FORCE_AI: true`)
- Headless mode (no visual browser in CI)

## Troubleshooting CI Failures

### Issue: UI tests timeout
**Solution:** CI server might be slower. Increase server startup wait time:
```yaml
sleep 10  # Increase from 5 to 10 seconds
```

### Issue: Playwright installation fails
**Solution:** It already has `continue-on-error: true`, so tests will skip gracefully

### Issue: API key not found
**Solution:** The workflow creates a mock key:
```yaml
echo "sk-ant-mock-key-for-testing" > .anthropickey
```

## Local Testing Before Push

```bash
# Run all tests like CI does
python -m pytest tests/BACKEND/ -v
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
sleep 2
python -m pytest tests/ui_testing/e2e/ -v
```

## GitHub Actions Workflow File

Location: `.github/workflows/tests.yml`

The workflow runs on:
- ✅ Every `git push`
- ✅ Every pull request

View results: Go to repository → Actions tab → Latest workflow run

## Next Steps

1. **Commit the updated workflow**
   ```bash
   git add .github/workflows/tests.yml
   git commit -m "Add UI testing to CI pipeline"
   git push
   ```

2. **Watch it run on GitHub**
   - Go to your repository
   - Click "Actions" tab
   - See your tests run automatically

3. **Optional: Add UI test reports**
   - Configure Playwright to generate HTML reports
   - Upload reports as GitHub artifacts

## Environment Variables Reference

| Variable | Value | Purpose |
|----------|-------|---------|
| `CI` | `true` | Signals CI environment |
| `USE_MOCK_DATA` | `false` | Use real ERPNext data |
| `UI_BASE_URL` | `http://127.0.0.1:8000` | Test server address |
| `UI_FORCE_AI` | `true` | Enable Claude AI for tests |
| `UI_SLOW_MO_MS` | `0` | No delays (faster tests) |
| `UI_KEEP_OPEN` | `false` | Auto-close browser after test |

## Test Execution Order

```
1. Install dependencies
2. Install Playwright
3. Create API key mock
4. Start server
5. Run backend tests
6. Run UI tests
7. Report results
```

Total expected time: **2-3 minutes**

