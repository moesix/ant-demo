"""
Ant Demo - Kubernetes Cluster Application Showcase
Phase 1.3: CI/CD Pipeline Enhancements
Unit and Integration Tests
"""

import os
import sys
import pytest
from dotenv import load_dotenv

# Add project root to path for import resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Test imports (will be added after app.py is updated)