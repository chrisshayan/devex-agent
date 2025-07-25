#!/usr/bin/env python3
"""
Manual Test Runner for DevEx Ambient Agent
Simulates real developer workflow and tests end-to-end functionality
"""

import asyncio
import json
import time
import tempfile
import os
from pathlib import Path
import httpx
from datetime import datetime

# API base URL - adjust if running on different port
API_BASE_URL = "http://localhost:8000"

class DevExTestRunner:
    """Manual test runner for end-to-end testing"""
    
    def __init__(self, developer_id="manual_test_dev"):
        self.developer_id = developer_id
        self.client = httpx.AsyncClient(base_url=API_BASE_URL)
        self.project_path = None
    
    async def setup_test_project(self):
        """Create a temporary test project"""
        temp_dir = tempfile.mkdtemp(prefix="devex_manual_test_")
        self.project_path = temp_dir
        project_path = Path(temp_dir)
        
        print(f"📁 Created test project at: {temp_dir}")
        
        # Create project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / ".git").mkdir()
        
        # Create sample files
        files = {
            "src/main.py": '''
def calculate_tax(amount, rate=0.1):
    """Calculate tax for given amount"""
    return amount * rate

def process_order(items):
    """Process a customer order"""
    total = 0
    for item in items:
        total += item['price']
    
    tax = calculate_tax(total)
    return {
        'subtotal': total,
        'tax': tax,
        'total': total + tax
    }

class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.orders = []
    
    def add_order(self, order):
        self.orders.append(order)
''',
            "src/utils.py": '''
import re
import logging

def validate_email(email):
    """Validate email format"""
    pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'
    return bool(re.match(pattern, email))

def setup_logging(level=logging.INFO):
    """Setup application logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"
''',
            "tests/test_main.py": '''
import pytest
from src.main import calculate_tax, process_order, Customer

def test_calculate_tax():
    assert calculate_tax(100) == 10.0
    assert calculate_tax(50, 0.2) == 10.0

def test_process_order():
    items = [{'price': 10.0}, {'price': 20.0}]
    result = process_order(items)
    assert result['subtotal'] == 30.0
    assert result['tax'] == 3.0
    assert result['total'] == 33.0

def test_customer():
    customer = Customer("John Doe", "john@example.com")
    assert customer.name == "John Doe"
    assert customer.email == "john@example.com"
    assert len(customer.orders) == 0
''',
            "README.md": '''
# E-Commerce Order Processing

A simple order processing system for testing DevEx Ambient Agent.

## Features
- Tax calculation
- Order processing
- Customer management
- Email validation

## Testing
Run tests with: `python -m pytest tests/`
'''
        }
        
        for file_path, content in files.items():
            full_path = project_path / file_path
            full_path.write_text(content.strip())
        
        print(f"✅ Created {len(files)} test files")
        return temp_dir
    
    async def send_event(self, event_type, description, file_path=None, metadata=None):
        """Send an event to the ambient agent"""
        event_data = {
            "type": event_type,
            "source": "manual_test",
            "developer_id": self.developer_id,
            "project_path": self.project_path,
            "file_path": file_path,
            "description": description,
            "metadata": metadata or {}
        }
        
        try:
            response = await self.client.post("/events/ingest", json=event_data)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Event sent: {event_type} - {description}")
                print(f"   Action: {result.get('action_taken', 'queued')}")
                return result
            else:
                print(f"❌ Failed to send event: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error sending event: {e}")
            return None
    
    async def check_agent_status(self):
        """Check the current agent status"""
        try:
            response = await self.client.get(f"/status/{self.developer_id}")
            if response.status_code == 200:
                status = response.json()
                print(f"📊 Agent Status:")
                print(f"   Events: {status.get('events_count', 0)}")
                print(f"   Status: {status.get('status', 'unknown')}")
                print(f"   Monitoring: {status.get('is_monitoring', False)}")
                return status
            else:
                print(f"❌ Failed to get status: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return None
    
    async def get_morning_brief(self):
        """Get the morning brief for the developer"""
        try:
            response = await self.client.get(f"/brief/morning/{self.developer_id}")
            if response.status_code == 200:
                brief = response.json()
                print(f"📋 Morning Brief Generated:")
                print(f"   Summary: {brief.get('summary', 'No summary')}")
                print(f"   Critical Items: {len(brief.get('critical_items', []))}")
                print(f"   Suggestions: {len(brief.get('suggestions', []))}")
                
                # Print suggestions if any
                for i, suggestion in enumerate(brief.get('suggestions', [])[:3]):
                    print(f"   💡 Suggestion {i+1}: {suggestion.get('title', 'N/A')}")
                
                return brief
            else:
                print(f"❌ Failed to get brief: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting brief: {e}")
            return None
    
    async def simulate_development_session(self):
        """Simulate a realistic development session"""
        print("\n🚀 Starting Development Session Simulation")
        print("=" * 50)
        
        # 1. Start working - file changes
        await self.send_event(
            "file_changed",
            "Started working on tax calculation refactoring",
            file_path=os.path.join(self.project_path, "src/main.py"),
            metadata={
                "change_type": "modification",
                "lines_changed": 5,
                "language": "python"
            }
        )
        
        await asyncio.sleep(2)
        
        # 2. Add validation
        await self.send_event(
            "file_changed",
            "Added better email validation",
            file_path=os.path.join(self.project_path, "src/utils.py"),
            metadata={
                "change_type": "modification",
                "lines_added": 8,
                "function_added": "validate_email"
            }
        )
        
        await asyncio.sleep(1)
        
        # 3. Update tests
        await self.send_event(
            "file_changed",
            "Added unit tests for new validation",
            file_path=os.path.join(self.project_path, "tests/test_main.py"),
            metadata={
                "change_type": "modification",
                "lines_added": 15,
                "test_coverage": 85
            }
        )
        
        await asyncio.sleep(1)
        
        # 4. Build success
        await self.send_event(
            "build_event",
            "Build completed successfully",
            metadata={
                "build_status": "success",
                "duration": 3.2,
                "tests_passed": 8,
                "warnings": 0
            }
        )
        
        await asyncio.sleep(1)
        
        # 5. Git commit
        await self.send_event(
            "git_commit",
            "Improved tax calculation and validation",
            metadata={
                "commit_hash": "a1b2c3d4e5f6",
                "branch": "feature/better-validation",
                "files_changed": ["src/main.py", "src/utils.py", "tests/test_main.py"],
                "commit_message": "refactor: improve tax calculation with better validation"
            }
        )
        
        print("\n📊 Development Session Complete")
        await self.check_agent_status()
        
        print("\n⏳ Waiting a moment for processing...")
        await asyncio.sleep(3)
    
    async def simulate_problem_scenario(self):
        """Simulate a scenario with problems that need attention"""
        print("\n⚠️  Simulating Problem Scenario")
        print("=" * 40)
        
        # 1. Build failure
        await self.send_event(
            "build_event",
            "Build failed with syntax error",
            metadata={
                "build_status": "failed",
                "error_type": "syntax_error",
                "error_message": "SyntaxError: invalid syntax (main.py, line 42)",
                "duration": 0.8
            }
        )
        
        await asyncio.sleep(1)
        
        # 2. Runtime error
        await self.send_event(
            "error_event",
            "Runtime exception in production",
            metadata={
                "severity": "high",
                "error_type": "ValueError",
                "stack_trace": "ValueError: negative tax rate not allowed",
                "frequency": 5
            }
        )
        
        await asyncio.sleep(1)
        
        # 3. Test failures
        await self.send_event(
            "test_event",
            "Unit tests failing",
            metadata={
                "test_status": "failed",
                "tests_failed": 3,
                "tests_passed": 5,
                "failure_reason": "assertion_error"
            }
        )
        
        print("\n📊 Problem Scenario Complete")
        await self.check_agent_status()
    
    async def run_comprehensive_test(self):
        """Run a comprehensive end-to-end test"""
        print("🔬 DevEx Ambient Agent - Comprehensive Test")
        print("=" * 60)
        
        # Setup
        await self.setup_test_project()
        
        # Test API connectivity
        print("\n🔌 Testing API Connectivity...")
        try:
            response = await self.client.get("/")
            if response.status_code == 200:
                print("✅ API is running and accessible")
            else:
                print(f"❌ API returned status: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Cannot connect to API: {e}")
            print("💡 Make sure to start the agent with: python -m devex_agent.main")
            return
        
        # Initial status check
        print("\n📊 Initial Agent Status:")
        await self.check_agent_status()
        
        # Simulate normal development
        await self.simulate_development_session()
        
        # Generate morning brief
        print("\n📋 Generating Morning Brief...")
        brief = await self.get_morning_brief()
        
        # Simulate problems
        await self.simulate_problem_scenario()
        
        # Final status and brief
        print("\n📋 Final Morning Brief (with problems)...")
        await self.get_morning_brief()
        
        print("\n✅ Comprehensive test complete!")
        print(f"📁 Test project created at: {self.project_path}")
        print("🧹 You can manually clean up the test directory when done")
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.client.aclose()


async def main():
    """Main test runner"""
    runner = DevExTestRunner()
    
    try:
        await runner.run_comprehensive_test()
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    print("🔬 DevEx Ambient Agent - Manual Test Runner")
    print("This script will test the complete system end-to-end")
    print("\nMake sure the agent is running first:")
    print("  python -m devex_agent.main")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}") 