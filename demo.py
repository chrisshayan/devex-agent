#!/usr/bin/env python3
"""
DevEx Ambient Agent - Quick Demo
Simple demonstration of the ambient agent capabilities
"""

import asyncio
import json
import httpx
from datetime import datetime

async def demo_devex_agent():
    """Demonstrate the DevEx Ambient Agent"""
    
    print("🎯 DevEx Ambient Agent - Quick Demo")
    print("=" * 40)
    
    # Test API connectivity
    print("\n1️⃣ Testing Agent Connectivity...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/")
            if response.status_code == 200:
                print("   ✅ Agent is running and accessible")
                data = response.json()
                print(f"   📡 Status: {data.get('status', 'unknown')}")
            else:
                print(f"   ❌ Agent returned status: {response.status_code}")
                return
    except Exception as e:
        print(f"   ❌ Cannot connect to agent: {e}")
        print("   💡 Make sure to start the agent first: python -m devex_agent.main")
        return
    
    # Demo developer ID
    developer_id = "demo_user"
    
    # Send some sample events
    print(f"\n2️⃣ Sending Sample Development Events for '{developer_id}'...")
    
    events = [
        {
            "type": "file_changed",
            "source": "demo",
            "developer_id": developer_id,
            "project_path": "/demo/project",
            "file_path": "/demo/project/src/main.py",
            "description": "Refactored user authentication logic",
            "metadata": {
                "lines_added": 25,
                "lines_deleted": 12,
                "language": "python",
                "complexity": "medium"
            }
        },
        {
            "type": "git_commit",
            "source": "git",
            "developer_id": developer_id,
            "project_path": "/demo/project",
            "description": "Improved authentication security",
            "metadata": {
                "commit_hash": "demo123abc",
                "branch": "feature/auth-improvement",
                "files_changed": ["src/main.py", "tests/test_auth.py"],
                "commit_message": "feat: add multi-factor authentication support"
            }
        },
        {
            "type": "build_event",
            "source": "ci_cd",
            "developer_id": developer_id,
            "project_path": "/demo/project",
            "description": "Build completed successfully",
            "metadata": {
                "build_status": "success",
                "duration": 4.2,
                "tests_passed": 15,
                "coverage": 87.5
            }
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for i, event in enumerate(events, 1):
            try:
                response = await client.post("http://localhost:8000/events/ingest", json=event)
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Event {i}: {event['type']} - {event['description']}")
                    print(f"      Action: {result.get('action_taken', 'queued')}")
                else:
                    print(f"   ❌ Event {i} failed: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Error sending event {i}: {e}")
            
            # Small delay between events
            await asyncio.sleep(0.5)
    
    # Check agent status
    print(f"\n3️⃣ Checking Agent Status...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8000/status/{developer_id}")
            if response.status_code == 200:
                status = response.json()
                print(f"   📊 Events Processed: {status.get('events_count', 0)}")
                print(f"   🔄 Agent Status: {status.get('status', 'unknown')}")
                print(f"   👀 Monitoring: {status.get('is_monitoring', False)}")
            else:
                print(f"   ❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting status: {e}")
    
    # Generate morning brief
    print(f"\n4️⃣ Generating Morning Brief...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://localhost:8000/brief/morning/{developer_id}")
            if response.status_code == 200:
                brief = response.json()
                print(f"   📋 Morning Brief Generated Successfully!")
                print(f"   📝 Summary: {brief.get('summary', 'No summary available')}")
                
                # Show critical items
                critical_items = brief.get('critical_items', [])
                if critical_items:
                    print(f"   🚨 Critical Items ({len(critical_items)}):")
                    for item in critical_items[:3]:
                        print(f"      • {item.get('title', 'N/A')} (Priority: {item.get('priority', 'unknown')})")
                
                # Show suggestions  
                suggestions = brief.get('suggestions', [])
                if suggestions:
                    print(f"   💡 Suggestions ({len(suggestions)}):")
                    for suggestion in suggestions[:3]:
                        print(f"      • {suggestion.get('title', 'N/A')}")
                
                # Show activity overview
                activity = brief.get('activity_overview', {})
                if activity:
                    print(f"   📈 Activity Overview:")
                    for key, value in activity.items():
                        print(f"      • {key}: {value}")
                        
            else:
                print(f"   ❌ Failed to generate brief: {response.status_code}")
                response_text = response.text
                if response_text:
                    print(f"   📄 Response: {response_text}")
    except Exception as e:
        print(f"   ❌ Error generating brief: {e}")
    
    print(f"\n🎉 Demo Complete!")
    print("=" * 40)
    print("💡 Next Steps:")
    print("   1. Try the manual test runner: python tests/manual_test_runner.py")
    print("   2. Install the IntelliJ plugin for real-time monitoring")
    print("   3. Integrate with your actual development workflow")
    print("   4. Check the comprehensive README.md for more details")

if __name__ == "__main__":
    print("🚀 Starting DevEx Ambient Agent Demo")
    print("Make sure the agent is running first: python -m devex_agent.main")
    print()
    
    try:
        asyncio.run(demo_devex_agent())
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("💡 Ensure the ambient agent is running: python -m devex_agent.main") 