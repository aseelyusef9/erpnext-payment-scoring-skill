"""
Create high-risk test customers in ERPNext via API.
"""
from app.erpnext.client import ERPNextClient
from datetime import datetime, timedelta
import random

def create_high_risk_customer():
    """Create a customer with overdue invoices to simulate high risk."""
    client = ERPNextClient()
    
    # Create customer
    customer_name = f"High Risk Customer {random.randint(1000, 9999)}"
    print(f"\n1. Creating customer: {customer_name}")
    
    customer = client.create_customer(
        customer_name=customer_name,
        customer_type="Company"
    )
    customer_id = customer.get("name")
    print(f"   ✓ Customer created: {customer_id}")
    
    # Get fiscal year info
    fiscal_year = client.get_active_fiscal_year()
    if not fiscal_year:
        print("   ✗ No active fiscal year found!")
        return
    
    print(f"\n2. Creating overdue invoices...")
    
    # Create multiple overdue invoices
    invoices_to_create = [
        {"days_ago": 45, "due_days_ago": 30, "amount": 5000},
        {"days_ago": 35, "due_days_ago": 20, "amount": 3000},
        {"days_ago": 30, "due_days_ago": 15, "amount": 7000},
        {"days_ago": 25, "due_days_ago": 10, "amount": 4500},
        {"days_ago": 20, "due_days_ago": 5, "amount": 2000},
        {"days_ago": 15, "due_days_ago": 0, "amount": 6000},
    ]
    
    for idx, invoice_data in enumerate(invoices_to_create, 1):
        posting_date = (datetime.now() - timedelta(days=invoice_data["days_ago"])).strftime("%Y-%m-%d")
        due_date = (datetime.now() - timedelta(days=invoice_data["due_days_ago"])).strftime("%Y-%m-%d")
        
        try:
            invoice = client.create_sales_invoice(
                customer=customer_id,
                posting_date=posting_date,
                due_date=due_date,
                items=[{
                    "item_code": "Sample Item",  # Use an existing item from your ERPNext
                    "qty": 1,
                    "rate": invoice_data["amount"]
                }]
            )
            print(f"   ✓ Invoice {idx}: {invoice.get('name')} - ${invoice_data['amount']} (Due: {due_date})")
        except Exception as e:
            print(f"   ✗ Failed to create invoice {idx}: {str(e)}")
    
    print(f"\n3. High-risk customer setup complete!")
    print(f"   Customer ID: {customer_id}")
    print(f"   Total Invoices: {len(invoices_to_create)}")
    print(f"   Overdue Invoices: {len([i for i in invoices_to_create if i['due_days_ago'] > 0])}")
    print(f"\n4. Test the score:")
    print(f"   curl http://localhost:8000/api/v1/customers/{customer_id}/score")
    
    return customer_id

def create_medium_risk_customer():
    """Create a customer with some overdue invoices (medium risk)."""
    client = ERPNextClient()
    
    customer_name = f"Medium Risk Customer {random.randint(1000, 9999)}"
    print(f"\n1. Creating customer: {customer_name}")
    
    customer = client.create_customer(
        customer_name=customer_name,
        customer_type="Company"
    )
    customer_id = customer.get("name")
    print(f"   ✓ Customer created: {customer_id}")
    
    # Create mix of paid and overdue invoices
    invoices_to_create = [
        {"days_ago": 30, "due_days_ago": 15, "amount": 3000},
        {"days_ago": 20, "due_days_ago": 5, "amount": 2000},
        {"days_ago": 10, "due_days_ago": -5, "amount": 1500},  # Not yet due
    ]
    
    print(f"\n2. Creating invoices...")
    for idx, invoice_data in enumerate(invoices_to_create, 1):
        posting_date = (datetime.now() - timedelta(days=invoice_data["days_ago"])).strftime("%Y-%m-%d")
        due_date = (datetime.now() - timedelta(days=invoice_data["due_days_ago"])).strftime("%Y-%m-%d")
        
        try:
            invoice = client.create_sales_invoice(
                customer=customer_id,
                posting_date=posting_date,
                due_date=due_date,
                items=[{
                    "item_code": "Sample Item",
                    "qty": 1,
                    "rate": invoice_data["amount"]
                }]
            )
            print(f"   ✓ Invoice {idx}: {invoice.get('name')} - ${invoice_data['amount']}")
        except Exception as e:
            print(f"   ✗ Failed to create invoice {idx}: {str(e)}")
    
    print(f"\n3. Medium-risk customer setup complete!")
    print(f"   Customer ID: {customer_id}")
    print(f"\n4. Test the score:")
    print(f"   curl http://localhost:8000/api/v1/customers/{customer_id}/score")
    
    return customer_id

if __name__ == "__main__":
    print("=" * 60)
    print("Create Test Customers with Different Risk Levels")
    print("=" * 60)
    
    choice = input("\nCreate which type?\n1. High Risk (score < 50)\n2. Medium Risk (score 50-79)\n3. Both\n\nChoice (1/2/3): ").strip()
    
    try:
        if choice == "1":
            create_high_risk_customer()
        elif choice == "2":
            create_medium_risk_customer()
        elif choice == "3":
            print("\n--- Creating High Risk Customer ---")
            high_risk_id = create_high_risk_customer()
            print("\n\n--- Creating Medium Risk Customer ---")
            medium_risk_id = create_medium_risk_customer()
            print(f"\n\n{'='*60}")
            print("Both customers created successfully!")
            print(f"{'='*60}")
        else:
            print("Invalid choice!")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nMake sure:")
        print("1. ERPNext is running (http://localhost:8080)")
        print("2. API keys are configured in .env")
        print("3. An item named 'Sample Item' exists in ERPNext")
