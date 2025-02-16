import os
import pytest
from dotenv import load_dotenv
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def load_env():
    """Load environment variables before each test"""
    load_dotenv()
    # Verify that the API key is loaded
    assert os.getenv('GEMINI_API_KEY') is not None, "GEMINI_API_KEY not found in environment variables" 