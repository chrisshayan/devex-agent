"""
End-to-End Tests for DevEx Ambient Agent
Tests the complete workflow from file changes to morning brief generation
"""

import pytest
import asyncio
import tempfile
import os
import shutil
from pathlib import Path
import httpx
from datetime import datetime

from src.devex_agent.core.ambient_orchestrator import AmbientOrchestrator
from src.devex_agent.api.models import EventRequest


class TestE2EFileChanges:
    """End-to-end tests with real file changes simulation"""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create ambient orchestrator for testing"""
        orchestrator = AmbientOrchestrator()
        await orchestrator.initialize()
        yield orchestrator
        await orchestrator.cleanup()
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory with sample files"""
        temp_dir = tempfile.mkdtemp(prefix="devex_test_")
        project_path = Path(temp_dir)
        
        # Create sample project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / ".git").mkdir()
        
        # Create sample files
        sample_files = {
            "src/main.py": '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total

class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, item):
        self.items.append(item)
    
    def get_total(self):
        return calculate_total(self.items)
''',
            "src/utils.py": '''
import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO)

def validate_email(email):
    return "@" in email and "." in email
''',
            "tests/test_main.py": '''
import pytest
from src.main import calculate_total, ShoppingCart

def test_calculate_total():
    pass  # TODO: implement test

def test_shopping_cart():
    pass  # TODO: implement test
''',
            "README.md": '''
# Sample Project

This is a sample project for testing.
''',
            ".gitignore": '''
__pycache__/
*.pyc
.env
'''
        }
        
        for file_path, content in sample_files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content.strip())
        
        yield str(project_path)
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def developer_id(self):
        """Sample developer ID for testing"""
        return "test_developer_123"
    
    async def test_file_change_detection_and_processing(self, orchestrator, temp_project, developer_id):
        """Test that file changes are detected and processed correctly"""
        
        # Simulate file change event
        file_path = os.path.join(temp_project, "src/main.py")
        
        # Create file change event
        change_event = EventRequest(
            type="file_changed",
            source="intellij",
            developer_id=developer_id,
            project_path=temp_project,
            file_path=file_path,
            description="Modified calculate_total function",
            metadata={
                "change_type": "modification",
                "lines_added": 5,
                "lines_deleted": 2,
                "file_size": 1024,
                "language": "python"
            }
        )
        
        # Process the event
        result = await orchestrator.process_event(change_event.dict())
        
        # Verify event was processed
        assert result is not None
        assert "event_id" in result
        
        # Check that state was updated
        status = await orchestrator.get_agent_status(developer_id)
        assert status["events_count"] > 0
    
    async def test_git_commit_simulation(self, orchestrator, temp_project, developer_id):
        """Test git commit event processing"""
        
        commit_event = EventRequest(
            type="git_commit",
            source="git",
            developer_id=developer_id,
            project_path=temp_project,
            description="Added shopping cart functionality",
            metadata={
                "commit_hash": "abc123def456",
                "branch": "feature/shopping-cart",
                "files_changed": ["src/main.py", "tests/test_main.py"],
                "insertions": 15,
                "deletions": 3,
                "commit_message": "feat: implement shopping cart with tests"
            }
        )
        
        result = await orchestrator.process_event(commit_event.dict())
        
        assert result is not None
        assert "event_id" in result
        
        # Verify the commit was tracked
        status = await orchestrator.get_agent_status(developer_id)
        assert status["events_count"] > 0
    
    async def test_build_failure_simulation(self, orchestrator, temp_project, developer_id):
        """Test build failure event processing"""
        
        build_event = EventRequest(
            type="build_event",
            source="build_system",
            developer_id=developer_id,
            project_path=temp_project,
            description="Build failed with syntax error",
            metadata={
                "build_status": "failed",
                "error_type": "syntax_error",
                "error_message": "SyntaxError: invalid syntax (main.py, line 15)",
                "duration": 5.2,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        result = await orchestrator.process_event(build_event.dict())
        
        assert result is not None
        # Build failures should potentially trigger immediate notifications
        assert result.get("action_taken") in ["queued_for_processing", "immediate_analysis"]
    
    async def test_multiple_file_changes_sequence(self, orchestrator, temp_project, developer_id):
        """Test processing sequence of multiple file changes"""
        
        # Simulate a development session with multiple file changes
        events = [
            # Start working on a feature
            EventRequest(
                type="file_changed",
                source="intellij",
                developer_id=developer_id,
                project_path=temp_project,
                file_path=os.path.join(temp_project, "src/main.py"),
                description="Started refactoring calculate_total",
                metadata={"change_type": "modification", "lines_changed": 3}
            ),
            # Add tests
            EventRequest(
                type="file_changed",
                source="intellij",
                developer_id=developer_id,
                project_path=temp_project,
                file_path=os.path.join(temp_project, "tests/test_main.py"),
                description="Added unit tests for calculate_total",
                metadata={"change_type": "modification", "lines_added": 10}
            ),
            # Update utils
            EventRequest(
                type="file_changed",
                source="intellij",
                developer_id=developer_id,
                project_path=temp_project,
                file_path=os.path.join(temp_project, "src/utils.py"),
                description="Added validation utility",
                metadata={"change_type": "modification", "lines_added": 5}
            ),
            # Commit changes
            EventRequest(
                type="git_commit",
                source="git",
                developer_id=developer_id,
                project_path=temp_project,
                description="Refactored calculate_total and added tests",
                metadata={
                    "commit_hash": "def789abc123",
                    "files_changed": ["src/main.py", "tests/test_main.py", "src/utils.py"],
                    "commit_message": "refactor: improve calculate_total with better validation"
                }
            )
        ]
        
        # Process events in sequence
        results = []
        for event in events:
            result = await orchestrator.process_event(event.dict())
            results.append(result)
            # Small delay to simulate real timing
            await asyncio.sleep(0.1)
        
        # All events should be processed successfully
        assert len(results) == 4
        assert all(r is not None for r in results)
        
        # Check final status
        status = await orchestrator.get_agent_status(developer_id)
        assert status["events_count"] >= 4
    
    async def test_morning_brief_generation(self, orchestrator, temp_project, developer_id):
        """Test morning brief generation after file changes"""
        
        # First, create some events to analyze
        await self.test_multiple_file_changes_sequence(orchestrator, temp_project, developer_id)
        
        # Wait a moment for processing
        await asyncio.sleep(0.5)
        
        # Generate morning brief
        brief = await orchestrator.generate_morning_brief(developer_id)
        
        # Verify brief structure
        assert brief is not None
        assert "developer_id" in brief
        assert "summary" in brief
        assert "activity_overview" in brief
        assert "suggestions" in brief
        
        # Brief should reflect the recent activity
        assert brief["developer_id"] == developer_id
        assert len(brief.get("activity_overview", {})) > 0
        
        print(f"Generated Morning Brief:")
        print(f"Summary: {brief['summary']}")
        print(f"Suggestions: {len(brief.get('suggestions', []))} items")
    
    async def test_critical_event_immediate_processing(self, orchestrator, temp_project, developer_id):
        """Test that critical events trigger immediate processing"""
        
        # Simulate a critical error event
        critical_event = EventRequest(
            type="error_event",
            source="runtime",
            developer_id=developer_id,
            project_path=temp_project,
            description="Runtime exception in production code",
            metadata={
                "severity": "critical",
                "error_type": "RuntimeError",
                "stack_trace": "RuntimeError: Division by zero in calculate_total",
                "frequency": 10,  # Occurring frequently
                "impact": "high"
            }
        )
        
        result = await orchestrator.process_event(critical_event.dict())
        
        # Critical events should trigger immediate analysis
        assert result is not None
        assert result.get("action_taken") == "immediate_analysis"
    
    @pytest.mark.asyncio
    async def test_agent_state_persistence(self, orchestrator, temp_project, developer_id):
        """Test that agent state persists across events"""
        
        # Process initial event
        event1 = EventRequest(
            type="file_changed",
            source="intellij",
            developer_id=developer_id,
            project_path=temp_project,
            file_path=os.path.join(temp_project, "src/main.py"),
            description="Initial change"
        )
        
        await orchestrator.process_event(event1.dict())
        
        # Get initial status
        status1 = await orchestrator.get_agent_status(developer_id)
        initial_event_count = status1["events_count"]
        
        # Process another event
        event2 = EventRequest(
            type="file_changed",
            source="intellij", 
            developer_id=developer_id,
            project_path=temp_project,
            file_path=os.path.join(temp_project, "src/utils.py"),
            description="Second change"
        )
        
        await orchestrator.process_event(event2.dict())
        
        # Status should reflect both events
        status2 = await orchestrator.get_agent_status(developer_id)
        assert status2["events_count"] > initial_event_count
    
    async def test_productivity_pattern_detection(self, orchestrator, temp_project, developer_id):
        """Test detection of productivity patterns from file changes"""
        
        # Simulate productive coding session
        productive_events = [
            # Rapid file changes indicating focused work
            EventRequest(
                type="file_changed",
                source="intellij",
                developer_id=developer_id,
                project_path=temp_project,
                file_path=os.path.join(temp_project, "src/main.py"),
                description="Implementing new feature",
                metadata={"lines_added": 25, "focus_time": 45}
            ),
            EventRequest(
                type="file_changed",
                source="intellij",
                developer_id=developer_id,
                project_path=temp_project,
                file_path=os.path.join(temp_project, "tests/test_main.py"),
                description="Adding comprehensive tests",
                metadata={"lines_added": 30, "test_coverage": 85}
            ),
            EventRequest(
                type="git_commit",
                source="git",
                developer_id=developer_id,
                project_path=temp_project,
                description="Feature complete with tests",
                metadata={
                    "commit_message": "feat: complete user authentication with full test coverage",
                    "quality_score": 9.2
                }
            )
        ]
        
        # Process productive session events
        for event in productive_events:
            await orchestrator.process_event(event.dict())
            await asyncio.sleep(0.1)
        
        # Generate brief to see productivity insights
        brief = await orchestrator.generate_morning_brief(developer_id)
        
        # Should detect productive patterns
        assert brief is not None
        insights = brief.get("insights", {})
        assert "productivity_metrics" in brief or len(insights) > 0


# Integration test with HTTP API
class TestE2EAPIIntegration:
    """Test the complete API integration"""
    
    @pytest.fixture
    def api_client(self):
        """HTTP client for API testing"""
        return httpx.AsyncClient(base_url="http://localhost:8000")
    
    @pytest.mark.asyncio
    async def test_api_event_ingestion(self, api_client):
        """Test event ingestion through the API"""
        
        event_data = {
            "type": "file_changed",
            "source": "intellij",
            "developer_id": "api_test_dev",
            "project_path": "/test/project",
            "file_path": "/test/project/src/main.py",
            "description": "API test file change",
            "metadata": {"test": True}
        }
        
        # This test requires the API to be running
        # In a real test environment, you would start the API in a test server
        try:
            response = await api_client.post("/events/ingest", json=event_data)
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
        except httpx.ConnectError:
            pytest.skip("API server not running - start with 'python -m devex_agent.main'")


if __name__ == "__main__":
    # Run specific test
    pytest.main([__file__, "-v"]) 