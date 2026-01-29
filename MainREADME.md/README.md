# ERPNext Payment Scoring Skill

AI-powered payment behavior analysis and scoring system for ERPNext customers.

## Overview

This service analyzes customer payment history from ERPNext and generates:
- Payment behavior scores (0-100)
- Risk level assessments (low/medium/high)
- Payment reliability metrics
- Actionable insights and recommendations

## Features

- 🎯 **Automated Scoring**: Calculate payment scores based on historical data
- 📊 **Risk Assessment**: Classify customers by payment risk
- 💡 **Insights Generation**: Get actionable insights about customer payment behavior
- 🔌 **ERPNext Integration**: Direct API integration with ERPNext
- 🚀 **REST API**: Easy-to-use API endpoints for integration
- 📈 **Trend Analysis**: Track payment behavior changes over time

## Project Structure

```
payment-scoring-skill/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── erpnext/             # ERPNext API client
│   ├── models/              # Data models
│   ├── services/            # Business logic
│   ├── api/                 # API endpoints
│   └── ui/                  # Optional dashboard
├── tests/                   # Test suite
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

1. **Clone the repository**
   ```bash
   cd payment-scoring-skill
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   
   Edit `.env` file with your ERPNext credentials:
   ```env
   ERPNEXT_URL=http://your-erpnext-instance.com
   ERPNEXT_API_KEY=your_api_key
   ERPNEXT_API_SECRET=your_api_secret
   ```

## Usage

### Starting the Server

```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### Health Check
```bash
GET /health
GET /health/erpnext
```

#### Get All Customer Payment Scores
```bash
GET /api/v1/customers/payment-scores?limit=100
```

#### Get High-Risk Customers
```bash
GET /api/v1/customers/high-risk
```

Returns customers with score < 50 requiring immediate follow-up.

#### Get Customer Follow-ups
```bash
GET /api/v1/customers/followups
```

Returns customers grouped by action type:
- `immediate_followup`: Score < 50
- `friendly_reminder`: Score 50-79
- `no_action`: Score 80-100

#### Get Individual Customer Score
```bash
GET /api/v1/customers/{customer_id}/score
```

Response:
```json
{
  "customer_id": "CUST-00001",
  "customer_name": "ABC Corporation",
  "score": 85.5,
  "risk_level": "low",
  "action": "None",
  "avg_payment_delay": 5.2,
  "payment_reliability": 95.0,
  "total_invoices": 50,
  "total_paid": 48,
  "total_outstanding": 15000.00,
  "overdue_count": 2,
  "insights": "Consistently pays on time with minimal delays"
}
```

#### Get Customer Insights
```bash
GET /api/v1/customers/{customer_id}/insights
```

## Testing

Run the test suite:

```bash
# Unit tests
pytest tests/unit/

# API tests
pytest tests/api/

# Integration tests (requires ERPNext connection)
pytest tests/integration/ -m integration

# All tests
pytest
```

## Scoring Algorithm

The payment score (0-100) is calculated using the business rule:

```
Score = 100 - (Overdue_Invoices × 10) - (Average_Delay_Days × 1)
```

Where:
- **Overdue_Invoices**: Count of currently unpaid and overdue invoices
- **Average_Delay_Days**: Average days past due date across all invoices

### Risk Levels and Actions

| Score Range | Risk Level | Action |
|-------------|------------|--------|
| 80–100 | Low | None |
| 50–79 | Medium | Friendly reminder |
| <50 | High | Immediate follow-up |

## Development

### Code Formatting
```bash
black app/ tests/
```

### Type Checking
```bash
mypy app/
```

### Linting
```bash
flake8 app/ tests/
```

## Configuration

All configuration is managed through environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `ERPNEXT_URL` | ERPNext instance URL | `http://localhost:8080` |
| `ERPNEXT_API_KEY` | ERPNext API key | Required |
| `ERPNEXT_API_SECRET` | ERPNext API secret | Required |
| `DEBUG` | Enable debug mode | `False` |
| `MIN_TRANSACTIONS_FOR_SCORING` | Minimum transactions needed | `3` |

## Docker Support

```bash
# Build image
docker build -t payment-scoring-skill .

# Run container
docker run -p 8000:8000 --env-file .env payment-scoring-skill
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API documentation at `/docs`

## Roadmap

- [ ] Machine learning-based scoring
- [ ] Real-time score updates
- [ ] Email notifications for risk changes
- [ ] Integration with more ERP systems
- [ ] Interactive dashboard UI
- [ ] Multi-currency support
- [ ] Historical score tracking
