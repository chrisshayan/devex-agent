#!/usr/bin/env python3
"""
Test Script for Phase 1 ML Functionality

Tests the CodeBERT integration and Developer Intelligence Engine
to verify that the ML capabilities are working correctly.
"""

import asyncio
import httpx
import json
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_DEVELOPER_ID = "test_developer_alice"

# Sample code snippets for testing
SAMPLE_CODE_SNIPPETS = [
    """
def calculate_user_score(user_data):
    '''Calculate user engagement score based on activity'''
    if not user_data:
        return 0.0
    
    activity_weight = 0.6
    content_weight = 0.4
    
    activity_score = user_data.get('activity_count', 0) / 100
    content_score = user_data.get('content_quality', 0) / 10
    
    return min(1.0, activity_score * activity_weight + content_score * content_weight)
    """,
    
    """
class UserValidator:
    '''Validates user input and ensures data integrity'''
    
    def __init__(self, strict_mode=True):
        self.strict_mode = strict_mode
        self.validation_rules = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^\+?1?d{9,15}$'
        }
    
    def validate_email(self, email):
        import re
        if not re.match(self.validation_rules['email'], email):
            raise ValueError("Invalid email format")
        return True
    
    def validate_user_data(self, user_data):
        required_fields = ['email', 'username', 'password']
        
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")
        
        self.validate_email(user_data['email'])
        return True
    """,
    
    """
async def fetch_user_profile(user_id, session):
    '''Fetch user profile with error handling and retries'''
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            async with session.get(f'/api/users/{user_id}') as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 404:
                    logger.warning(f"User {user_id} not found")
                    return None
                else:
                    response.raise_for_status()
                    
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error(f"All retries failed for user {user_id}: {e}")
                raise
    """,
    
    """
import unittest
from unittest.mock import Mock, patch

class TestUserService(unittest.TestCase):
    '''Test cases for user service functionality'''
    
    def setUp(self):
        self.user_service = UserService()
        self.sample_user = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com'
        }
    
    def test_user_creation_valid_data(self):
        '''Test user creation with valid data'''
        result = self.user_service.create_user(self.sample_user)
        self.assertIsNotNone(result)
        self.assertEqual(result['username'], 'testuser')
    
    @patch('user_service.database.save')
    def test_user_creation_database_error(self, mock_save):
        '''Test user creation handles database errors'''
        mock_save.side_effect = Exception("Database error")
        
        with self.assertRaises(Exception):
            self.user_service.create_user(self.sample_user)
    """
]

QUERY_CODE_EXAMPLE = """
def authenticate_user(username, password):
    user = get_user_by_username(username)
    if user and check_password(user.password, password):
        return create_session(user)
    return None
"""


class MLTester:
    """Test class for ML functionality"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_health_check(self) -> bool:
        """Test if the agent is running"""
        try:
            response = await self.client.get(f"{self.base_url}")
            if response.status_code == 200:
                logger.info("✅ Agent is running and healthy")
                return True
            else:
                logger.error(f"❌ Agent health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to agent: {e}")
            return False
    
    async def test_ml_availability(self) -> bool:
        """Test if ML capabilities are available"""
        try:
            # Try generating embeddings as a simple ML test
            response = await self.client.post(
                f"{self.base_url}/api/v1/ml/code/embeddings",
                json={"code_snippets": ["def hello(): return 'world'"]}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    logger.info("✅ ML capabilities are available and working")
                    return True
                elif result.get("status") == "unavailable":
                    logger.warning("⚠️ ML capabilities not available (dependencies missing)")
                    return False
            
            logger.error(f"❌ ML availability test failed: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"❌ ML availability test error: {e}")
            return False
    
    async def test_code_analysis(self) -> Dict[str, Any]:
        """Test developer code analysis"""
        try:
            logger.info("🔍 Testing code analysis...")
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/ml/developer/{TEST_DEVELOPER_ID}/analyze",
                json={
                    "code_snippets": SAMPLE_CODE_SNIPPETS,
                    "file_paths": ["user_service.py", "validators.py", "api_client.py", "test_user.py"]
                }
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                analysis = result.get("analysis", {})
                logger.info("✅ Code analysis completed successfully")
                logger.info(f"   - Developer: {result['developer_id']}")
                logger.info(f"   - Analysis ID: {analysis.get('analysis_id', 'N/A')}")
                logger.info(f"   - Dominant patterns: {len(analysis.get('dominant_patterns', []))}")
                logger.info(f"   - Language proficiency: {analysis.get('language_proficiency', {})}")
                return result
            else:
                logger.error(f"❌ Code analysis failed: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Code analysis test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_skill_assessment(self) -> Dict[str, Any]:
        """Test developer skill assessment"""
        try:
            logger.info("📏 Testing skill assessment...")
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/ml/developer/{TEST_DEVELOPER_ID}/skills",
                json={"code_snippets": SAMPLE_CODE_SNIPPETS}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                skills = result.get("skills", {})
                logger.info("✅ Skill assessment completed successfully")
                logger.info(f"   - Developer: {result['developer_id']}")
                logger.info(f"   - Skills assessed: {list(skills.keys())}")
                
                for skill_name, assessment in skills.items():
                    level = assessment.get('level', 0)
                    confidence = assessment.get('confidence', 0)
                    logger.info(f"   - {skill_name}: {level:.2f} (confidence: {confidence:.2f})")
                
                return result
            else:
                logger.error(f"❌ Skill assessment failed: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Skill assessment test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_code_similarity(self) -> Dict[str, Any]:
        """Test code similarity search"""
        try:
            logger.info("🔍 Testing code similarity search...")
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/ml/code/similar",
                json={
                    "query_code": QUERY_CODE_EXAMPLE,
                    "developer_id": TEST_DEVELOPER_ID,
                    "threshold": 0.5
                }
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                patterns = result.get("similar_patterns", [])
                logger.info("✅ Code similarity search completed successfully")
                logger.info(f"   - Query code: {result.get('query_code', '')}")
                logger.info(f"   - Threshold: {result.get('threshold', 0)}")
                logger.info(f"   - Similar patterns found: {len(patterns)}")
                return result
            else:
                logger.error(f"❌ Code similarity search failed: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Code similarity test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_embeddings_generation(self) -> Dict[str, Any]:
        """Test code embeddings generation"""
        try:
            logger.info("🔮 Testing embeddings generation...")
            
            test_snippets = SAMPLE_CODE_SNIPPETS[:2]  # Use first 2 snippets
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/ml/code/embeddings",
                json={"code_snippets": test_snippets}
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                embeddings = result.get("embeddings", [])
                dimension = result.get("embedding_dimension", 0)
                logger.info("✅ Embeddings generation completed successfully")
                logger.info(f"   - Snippets processed: {result.get('snippet_count', 0)}")
                logger.info(f"   - Embeddings generated: {len(embeddings)}")
                logger.info(f"   - Embedding dimension: {dimension}")
                
                # Verify embedding structure
                if embeddings:
                    first_embedding = embeddings[0]
                    logger.info(f"   - First embedding preview: [{first_embedding[0]:.4f}, {first_embedding[1]:.4f}, ...]")
                
                return result
            else:
                logger.error(f"❌ Embeddings generation failed: {result}")
                return result
                
        except Exception as e:
            logger.error(f"❌ Embeddings generation test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all ML tests and return comprehensive results"""
        logger.info("🚀 Starting comprehensive ML functionality test...")
        
        results = {
            "test_run_id": f"ml_test_{asyncio.get_event_loop().time()}",
            "timestamp": "2024-01-15T10:00:00Z",
            "tests": {}
        }
        
        # Test 1: Health check
        health_ok = await self.test_health_check()
        results["tests"]["health_check"] = {"passed": health_ok}
        
        if not health_ok:
            logger.error("❌ Agent not running - stopping tests")
            return results
        
        # Test 2: ML availability
        ml_available = await self.test_ml_availability()
        results["tests"]["ml_availability"] = {"passed": ml_available}
        
        if not ml_available:
            logger.warning("⚠️ ML not available - skipping ML-specific tests")
            return results
        
        # Test 3: Code analysis
        analysis_result = await self.test_code_analysis()
        results["tests"]["code_analysis"] = {
            "passed": analysis_result.get("status") == "success",
            "result": analysis_result
        }
        
        # Test 4: Skill assessment
        skills_result = await self.test_skill_assessment()
        results["tests"]["skill_assessment"] = {
            "passed": skills_result.get("status") == "success",
            "result": skills_result
        }
        
        # Test 5: Code similarity
        similarity_result = await self.test_code_similarity()
        results["tests"]["code_similarity"] = {
            "passed": similarity_result.get("status") == "success",
            "result": similarity_result
        }
        
        # Test 6: Embeddings generation
        embeddings_result = await self.test_embeddings_generation()
        results["tests"]["embeddings_generation"] = {
            "passed": embeddings_result.get("status") == "success",
            "result": embeddings_result
        }
        
        # Calculate overall success
        passed_tests = sum(1 for test in results["tests"].values() if test["passed"])
        total_tests = len(results["tests"])
        
        results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "success" if passed_tests == total_tests else "partial" if passed_tests > 0 else "failed"
        }
        
        logger.info(f"📊 Test Summary: {passed_tests}/{total_tests} tests passed")
        logger.info(f"   Overall Status: {results['summary']['overall_status']}")
        
        return results
    
    async def cleanup(self):
        """Cleanup test resources"""
        await self.client.aclose()


async def main():
    """Main test execution"""
    print("\n" + "="*60)
    print("🧪 DevEx Ambient Agent - Phase 1 ML Testing")
    print("="*60)
    
    tester = MLTester()
    
    try:
        # Run comprehensive tests
        results = await tester.run_comprehensive_test()
        
        # Print detailed results
        print("\n📋 Detailed Test Results:")
        print("-" * 40)
        
        for test_name, test_result in results["tests"].items():
            status = "✅ PASS" if test_result["passed"] else "❌ FAIL"
            print(f"{test_name:20} | {status}")
        
        print("\n📊 Summary:")
        print(f"Success Rate: {results['summary']['success_rate']:.1%}")
        print(f"Overall Status: {results['summary']['overall_status'].upper()}")
        
        # Save results to file
        with open("ml_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Full results saved to: ml_test_results.json")
        
        if results['summary']['overall_status'] == 'success':
            print("\n🎉 All ML tests passed! Phase 1 implementation is working correctly.")
        elif results['summary']['overall_status'] == 'partial':
            print("\n⚠️ Some tests failed. Check the logs for details.")
        else:
            print("\n❌ Most tests failed. Check agent status and dependencies.")
            
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        print(f"\n💥 Test execution error: {e}")
    
    finally:
        await tester.cleanup()
    
    print("\n" + "="*60)


if __name__ == "__main__":
    print("📝 Instructions:")
    print("1. Make sure the DevEx Ambient Agent is running:")
    print("   uv run python -m devex_agent.main")
    print("2. Run this test script:")
    print("   uv run python test_ml_phase1.py")
    print("\n🔄 Starting tests in 3 seconds...")
    
    import time
    time.sleep(3)
    
    asyncio.run(main()) 