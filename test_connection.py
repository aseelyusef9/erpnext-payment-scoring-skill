"""Test ERPNext connection using unittest."""
import unittest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.erpnext.client import ERPNextClient
from app.config import settings


class TestERPNextConnection(unittest.TestCase):
    """Test ERPNext API connection."""
    
    @classmethod
    def setUpClass(cls):
        """Set up connection details once for all tests."""
        cls.client = ERPNextClient()
        
    def test_connection(self):
        """Test ERPNext API connection and authentication."""
        print("\n" + "=" * 50)
        print("ERPNext Connection Test")
        print("=" * 50)
        
        # Show configuration
        print(f"\n✓ ERPNext URL: {settings.ERPNEXT_URL}")
        print(f"✓ API Key: {settings.ERPNEXT_API_KEY[:10]}..." if settings.ERPNEXT_API_KEY else "✗ API Key not set")
        print(f"✓ API Secret: {settings.ERPNEXT_API_SECRET[:10]}..." if settings.ERPNEXT_API_SECRET else "✗ API Secret not set")
        
        # Test connection
        print("\nTesting API connection...")
        
        try:
            result = self.client._make_request('GET', '/api/method/frappe.auth.get_logged_user')
            print(f"\n✓ Connection successful!")
            print(f"✓ Logged in as: {result.get('message')}")
            
            # Assert connection is successful
            self.assertIsNotNone(result)
            self.assertIn('message', result)
            
        except Exception as e:
            print(f"\n✗ Connection failed: {str(e)}")
            print("\n" + "=" * 50)
            print("HOW TO FIX:")
            print("=" * 50)
            print("\n1. Make sure ERPNext is running:")
            print("   Open: http://localhost:8080")
            print("   Login: Administrator / admin")
            print("\n2. Generate API keys in ERPNext:")
            print("   - Click User menu (top right)")
            print("   - Go to: My Settings")
            print("   - Scroll to: API Access section")
            print("   - Click: Generate Keys button")
            print("   - Copy the API Key and API Secret")
            print("\n3. Update .env file with the keys:")
            print("   ERPNEXT_API_KEY=your_key_here")
            print("   ERPNEXT_API_SECRET=your_secret_here")
            print("\n4. Restart your application")
            print("=" * 50)
            
            # Fail the test
            self.fail(f"Connection test failed: {str(e)}")


def run_connection_test():
    """Helper function to run connection test standalone."""
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestERPNextConnection)
    
    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run the connection test
    success = run_connection_test()
    sys.exit(0 if success else 1)
