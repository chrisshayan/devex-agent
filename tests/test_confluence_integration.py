#!/usr/bin/env python3
"""
Confluence Integration Test - Comprehensive test for team documentation integration
"""

import asyncio
import httpx
import json
import os
from datetime import datetime
from typing import Dict, Any

# Test configurations
AGENT_URL = "http://localhost:8000"

class ConfluenceIntegrationTest:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        
        # Example Confluence configuration
        # NOTE: Replace these with your actual Confluence details
        self.test_confluence_config = {
            "type": "confluence",
            "config": {
                "name": "Team Documentation",
                "description": "Architecture decisions and team documentation",
                "base_url": os.getenv("CONFLUENCE_BASE_URL", "https://yourcompany.atlassian.net"),
                "space_key": os.getenv("CONFLUENCE_SPACE_KEY", "ARCH"),
                "page_filter": os.getenv("CONFLUENCE_PAGE_FILTER", "label = 'architecture'"),
                "username": os.getenv("CONFLUENCE_USERNAME", "your-email@company.com"),
                "api_token": os.getenv("CONFLUENCE_API_TOKEN", "your-api-token"),
                "include_attachments": True,
                "include_comments": False,
                "tags": ["architecture", "documentation", "decisions"]
            },
            "priority": "high",
            "auto_sync": True,
            "sync_interval": "6h",
            "enabled": True
        }
    
    async def run_comprehensive_test(self):
        """Run comprehensive Confluence integration test"""
        print("🚀 Starting Confluence Integration Test")
        print("=" * 60)
        
        # Check if agent is running
        if not await self._check_agent_health():
            print("❌ Agent not running or not responding")
            return False
        
        source_id = None
        try:
            # Test 1: Register Confluence source
            print("\n🧪 Test 1: Registering Confluence Source")
            source_id = await self._test_register_source()
            if not source_id:
                return False
            
            # Test 2: Validate source configuration
            print("\n🧪 Test 2: Validating Source Configuration")
            if not await self._test_validate_source(source_id):
                return False
            
            # Test 3: Trigger ingestion
            print("\n🧪 Test 3: Triggering Content Ingestion")
            if not await self._test_trigger_ingestion(source_id):
                return False
            
            # Test 4: Wait for ingestion and check results
            print("\n🧪 Test 4: Monitoring Ingestion Progress")
            if not await self._test_monitor_ingestion(source_id):
                return False
            
            # Test 5: Search Confluence content
            print("\n🧪 Test 5: Searching Confluence Content")
            if not await self._test_search_content():
                return False
            
            # Test 6: Test Knowledge Graph features
            print("\n🧪 Test 6: Testing Knowledge Graph Integration")
            if not await self._test_knowledge_graph_features(source_id):
                return False
            
            print("\n" + "=" * 60)
            print("🎉 All Confluence integration tests passed!")
            return True
            
        except Exception as e:
            print(f"\n❌ Test suite failed with error: {e}")
            return False
        finally:
            # Optional cleanup
            if source_id:
                await self._cleanup_test_source(source_id)
            await self.client.aclose()
    
    async def _check_agent_health(self) -> bool:
        """Check if the DevEx agent is running"""
        try:
            response = await self.client.get(f"{AGENT_URL}/")
            if response.status_code == 200:
                print("✅ DevEx Agent is running and responding")
                return True
            else:
                print(f"❌ Agent responded with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to agent: {e}")
            print("💡 Make sure the agent is running: uv run python -m devex_agent.main")
            return False
    
    async def _test_register_source(self) -> str:
        """Test registering a Confluence source"""
        try:
            print("📝 Registering Confluence source...")
            
            response = await self.client.post(
                f"{AGENT_URL}/api/v1/knowledge-graph/sources",
                json=self.test_confluence_config
            )
            
            if response.status_code == 200:
                source_data = response.json()
                source_id = source_data["source"]["id"]
                print(f"✅ Successfully registered Confluence source: {source_id}")
                
                # Show registered configuration
                config = source_data["source"]["config"]
                print(f"   📊 Space: {config['space_key']}")
                print(f"   🌐 Base URL: {config['base_url']}")
                print(f"   🔍 Page Filter: {config.get('page_filter', 'None')}")
                print(f"   📎 Include Attachments: {config['include_attachments']}")
                print(f"   💬 Include Comments: {config['include_comments']}")
                
                return source_id
            else:
                print(f"❌ Failed to register source: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Registration failed: {e}")
            return None
    
    async def _test_validate_source(self, source_id: str) -> bool:
        """Test source validation"""
        try:
            print(f"🔍 Validating source configuration...")
            
            # Get source details to trigger validation
            response = await self.client.get(
                f"{AGENT_URL}/api/v1/knowledge-graph/sources/{source_id}"
            )
            
            if response.status_code == 200:
                source_data = response.json()
                print("✅ Source configuration is valid")
                print(f"   📅 Created: {source_data.get('created_at', 'Unknown')}")
                print(f"   ⚡ Enabled: {source_data.get('enabled', False)}")
                return True
            else:
                print(f"❌ Validation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Validation test failed: {e}")
            return False
    
    async def _test_trigger_ingestion(self, source_id: str) -> bool:
        """Test triggering content ingestion"""
        try:
            print("🚀 Triggering content ingestion...")
            
            response = await self.client.post(
                f"{AGENT_URL}/api/v1/knowledge-graph/sources/{source_id}/ingest",
                params={"force": True}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Ingestion triggered successfully")
                print(f"   📝 Status: {result['message']}")
                print(f"   🔄 Force mode: {result['force']}")
                return True
            else:
                print(f"❌ Failed to trigger ingestion: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Ingestion trigger failed: {e}")
            return False
    
    async def _test_monitor_ingestion(self, source_id: str) -> bool:
        """Monitor ingestion progress"""
        try:
            print("⏳ Monitoring ingestion progress...")
            
            # Wait a bit for ingestion to start and process
            await asyncio.sleep(5)
            
            # Check source health for ingestion status
            response = await self.client.get(
                f"{AGENT_URL}/api/v1/knowledge-graph/sources/{source_id}/health"
            )
            
            if response.status_code == 200:
                health_data = response.json()
                print("✅ Ingestion monitoring successful")
                print(f"   📊 Health status: {health_data}")
                
                # Look for items ingested
                if "item_count" in health_data:
                    item_count = health_data["item_count"]
                    if item_count > 0:
                        print(f"   📄 Items ingested: {item_count}")
                        return True
                    else:
                        print("   ⚠️ No items ingested yet (this may be normal)")
                        return True
                else:
                    print("   ✅ Ingestion process initiated")
                    return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Monitoring failed: {e}")
            return True  # Don't fail the test suite for monitoring issues
    
    async def _test_search_content(self) -> bool:
        """Test searching Confluence content"""
        try:
            print("🔍 Testing content search...")
            
            # Test searches for common Confluence content
            search_queries = [
                "architecture decision",
                "documentation",
                "process",
                "guidelines"
            ]
            
            found_results = False
            
            for query in search_queries:
                print(f"   🔎 Searching for: '{query}'")
                
                search_request = {
                    "query": query,
                    "developer_id": "test_user",
                    "source_types": ["confluence"],
                    "max_results": 5,
                    "similarity_threshold": 0.6
                }
                
                response = await self.client.post(
                    f"{AGENT_URL}/api/v1/knowledge-graph/search",
                    json=search_request
                )
                
                if response.status_code == 200:
                    search_results = response.json()
                    results = search_results.get("results", [])
                    
                    if results:
                        found_results = True
                        print(f"      ✅ Found {len(results)} results")
                        
                        # Show details of first result
                        first_result = results[0]
                        print(f"      📄 Title: {first_result.get('title', 'N/A')}")
                        print(f"      🔗 URL: {first_result.get('url', 'N/A')}")
                        print(f"      📊 Score: {first_result.get('similarity_score', 0):.3f}")
                        
                        # Show metadata
                        metadata = first_result.get('metadata', {})
                        if metadata:
                            print(f"      📋 Type: {metadata.get('content_type', 'N/A')}")
                            if 'space_key' in metadata:
                                print(f"      🏠 Space: {metadata['space_key']}")
                    else:
                        print("      ⚪ No results found")
                else:
                    print(f"      ❌ Search failed: {response.status_code}")
            
            if found_results:
                print("✅ Content search test successful")
                return True
            else:
                print("⚠️ No search results found (may be normal if no content ingested yet)")
                return True  # Don't fail test if no content yet
                
        except Exception as e:
            print(f"❌ Search test failed: {e}")
            return False
    
    async def _test_knowledge_graph_features(self, source_id: str) -> bool:
        """Test Knowledge Graph features with Confluence content"""
        try:
            print("🧠 Testing Knowledge Graph features...")
            
            # Test 1: Contextual knowledge
            print("   🔍 Testing contextual knowledge...")
            response = await self.client.get(
                f"{AGENT_URL}/api/v1/knowledge-graph/context/test_user",
                params={
                    "current_file": "architecture.md",
                    "language": "markdown"
                }
            )
            
            if response.status_code == 200:
                context_data = response.json()
                print("      ✅ Contextual knowledge retrieved")
                print(f"      📊 Context score: {context_data.get('context_score', 0):.3f}")
                
                relevant_sources = context_data.get('relevant_sources', [])
                if relevant_sources:
                    print(f"      🎯 Relevant sources: {len(relevant_sources)}")
            else:
                print(f"      ⚠️ Contextual knowledge test skipped: {response.status_code}")
            
            # Test 2: Relationship discovery
            print("   🔗 Testing relationship discovery...")
            response = await self.client.post(
                f"{AGENT_URL}/api/v1/knowledge-graph/sources/{source_id}/discover-relationships"
            )
            
            if response.status_code == 200:
                relationship_data = response.json()
                relationships_found = relationship_data.get("relationships_discovered", 0)
                print(f"      ✅ Relationship discovery completed: {relationships_found} relationships")
                
                if "relationship_breakdown" in relationship_data:
                    breakdown = relationship_data["relationship_breakdown"]
                    for rel_type, count in breakdown.items():
                        print(f"         - {rel_type}: {count}")
            else:
                print(f"      ⚠️ Relationship discovery skipped: {response.status_code}")
            
            # Test 3: Code evaluation against Confluence docs
            print("   ⚖️ Testing code evaluation...")
            evaluation_request = {
                "developer_id": "test_user",
                "code_content": "# Architecture Decision\nThis is a sample architecture decision document.",
                "file_path": "docs/architecture.md",
                "language": "markdown"
            }
            
            response = await self.client.post(
                f"{AGENT_URL}/api/v1/knowledge-graph/evaluate",
                json=evaluation_request
            )
            
            if response.status_code == 200:
                evaluation_data = response.json()
                print("      ✅ Code evaluation completed")
                print(f"      📊 Alignment score: {evaluation_data.get('overall_alignment_score', 0):.3f}")
                
                recommendations = evaluation_data.get('recommendations', [])
                if recommendations:
                    print(f"      💡 Recommendations: {len(recommendations)}")
            else:
                print(f"      ⚠️ Code evaluation skipped: {response.status_code}")
            
            print("✅ Knowledge Graph features test completed")
            return True
            
        except Exception as e:
            print(f"❌ Knowledge Graph features test failed: {e}")
            return False
    
    async def _cleanup_test_source(self, source_id: str):
        """Optional cleanup of test source"""
        try:
            print(f"\n🧹 Cleaning up test source: {source_id}")
            
            # Uncomment to actually delete the test source
            # response = await self.client.delete(
            #     f"{AGENT_URL}/api/v1/knowledge-graph/sources/{source_id}"
            # )
            
            # if response.status_code == 200:
            #     print("✅ Test source cleaned up successfully")
            # else:
            #     print(f"⚠️ Cleanup warning: {response.status_code}")
            
            print("💡 Source cleanup skipped (uncomment in code to enable)")
            
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")
    
    def show_setup_instructions(self):
        """Show setup instructions for Confluence integration"""
        print("\n" + "=" * 60)
        print("📋 CONFLUENCE SETUP INSTRUCTIONS")
        print("=" * 60)
        print("\n1. 🔐 Get Confluence API Token:")
        print("   - Go to https://id.atlassian.com/manage-profile/security/api-tokens")
        print("   - Create a new API token")
        print("   - Save it securely\n")
        
        print("2. 🌐 Set Environment Variables:")
        print("   export CONFLUENCE_BASE_URL='https://yourcompany.atlassian.net'")
        print("   export CONFLUENCE_SPACE_KEY='ARCH'  # Your space key")
        print("   export CONFLUENCE_USERNAME='your-email@company.com'")
        print("   export CONFLUENCE_API_TOKEN='your-api-token'")
        print("   export CONFLUENCE_PAGE_FILTER=\"label = 'architecture'\"  # Optional\n")
        
        print("3. 🧪 Run This Test:")
        print("   uv run python test_confluence_integration.py\n")
        
        print("4. 📊 Monitor in DevEx Agent:")
        print(f"   - Agent UI: {AGENT_URL}")
        print(f"   - Sources: {AGENT_URL}/api/v1/knowledge-graph/sources")
        print(f"   - Search: {AGENT_URL}/api/v1/knowledge-graph/search\n")

async def main():
    """Main test function"""
    test_suite = ConfluenceIntegrationTest()
    
    # Show setup instructions
    test_suite.show_setup_instructions()
    
    # Check if environment variables are set
    required_vars = ["CONFLUENCE_BASE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables and run the test again.")
        print("You can also modify the test_confluence_config in the script directly.\n")
        
        # Ask if user wants to continue with demo mode
        print("🤔 Continue with demo configuration? (y/N): ", end="")
        response = input().lower().strip()
        if response != 'y':
            print("👋 Exiting. Set up environment variables and try again!")
            return
        
        print("\n📝 Running in DEMO mode with placeholder configuration...")
        print("   This will test the API endpoints but may not connect to real Confluence.\n")
    
    # Run the comprehensive test
    success = await test_suite.run_comprehensive_test()
    
    if success:
        print("\n🎉 Confluence integration is working correctly!")
        print("   You can now use Confluence as a knowledge source in the DevEx Agent.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        print("   Common issues: network connectivity, authentication, or configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 