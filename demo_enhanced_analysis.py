#!/usr/bin/env python3
"""
Demo script to test the enhanced code analysis
Shows how detailed file information is generated for the UI
"""

import asyncio
import json
import sys
from pathlib import Path
from src.devex_agent.workflows.enhanced_code_analyzer import run_enhanced_analysis

async def demo_enhanced_analysis():
    """Demo the enhanced analysis capabilities"""
    print("🚀 DevEx Enhanced Analysis Demo")
    print("=" * 50)
    
    try:
        # Run enhanced analysis on current project
        print("🔍 Running enhanced analysis...")
        results = await run_enhanced_analysis(".")
        
        print(f"\n📊 Analysis Results:")
        print(f"   Files analyzed: {results['total_files_analyzed']}")
        print(f"   Languages: {', '.join(results['languages_detected'])}")
        print(f"   Security issues: {len(results['security_issues'])}")
        print(f"   Quality issues: {len(results['quality_issues'])}")
        print(f"   Tools used: {', '.join(results['analysis_tools_used'])}")
        
        # Show sample security issues
        print(f"\n🔐 Security Issues (showing first 3):")
        for i, issue in enumerate(results['security_issues'][:3], 1):
            print(f"   {i}. {issue['file_path']}:{issue.get('line_number', '?')}")
            print(f"      {issue['description']}")
            print(f"      Severity: {issue['severity']} | Tool: {issue['tool']}")
            print()
        
        # Show sample quality issues
        print(f"🔧 Quality Issues (showing first 3):")
        for i, issue in enumerate(results['quality_issues'][:3], 1):
            print(f"   {i}. {issue['file_path']}:{issue.get('line_number', '?')}")
            print(f"      {issue['description']}")
            print(f"      Severity: {issue['severity']} | Tool: {issue['tool']}")
            print()
        
        # Show what the morning brief API would return
        print("📋 Morning Brief API Response Preview:")
        morning_brief_preview = {
            "critical_items": [],
            "suggestions": []
        }
        
        # Create security critical item
        if results['security_issues']:
            critical_security = [i for i in results['security_issues'] if i.get("severity") in ["critical", "high"]]
            if critical_security:
                morning_brief_preview["critical_items"].append({
                    "type": "security",
                    "priority": "critical",
                    "title": "Security concerns detected",
                    "description": f"Found {len(results['security_issues'])} potential security issues",
                    "action_required": True,
                    "count": len(results['security_issues']),
                    "files": results['security_issues'][:5]  # Show first 5 for demo
                })
        
        # Create quality suggestion
        if results['quality_issues']:
            morning_brief_preview["suggestions"].append({
                "type": "quality",
                "title": "Address code quality issues",
                "description": f"Found {len(results['quality_issues'])} potential quality concerns",
                "priority": "medium",
                "action": "quality_review",
                "files": results['quality_issues'][:5]  # Show first 5 for demo
            })
        
        print(json.dumps(morning_brief_preview, indent=2))
        
        print(f"\n✅ Demo complete! The IntelliJ plugin UI can now display:")
        print(f"   • Specific file paths and line numbers")
        print(f"   • Issue descriptions and severity levels") 
        print(f"   • Rule IDs and analysis tool information")
        print(f"   • Expandable file lists with detailed breakdowns")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print(f"💡 Make sure you have the analysis tools installed:")
        print(f"   pip install bandit pylint flake8 mypy radon vulture")
        print(f"   # Note: safety and semgrep require separate installation")
        return False
    
    return True

def create_sample_files_for_testing():
    """Create sample Python files with security and quality issues for testing"""
    print("📁 Creating sample files for testing...")
    
    # Create a sample file with security issues
    sample_security_file = Path("sample_security_issues.py")
    sample_security_file.write_text('''
import os
import subprocess

# Security issue: hardcoded password
PASSWORD = "admin123"

def unsafe_command(user_input):
    # Security issue: command injection
    os.system(f"ls {user_input}")

def sql_query(user_id):
    # Security issue: SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query

# Security issue: insecure random
import random
session_token = random.randint(1000, 9999)
''')
    
    # Create a sample file with quality issues
    sample_quality_file = Path("sample_quality_issues.py")
    sample_quality_file.write_text('''
def complexFunction(a,b,c,d,e,f):
    # Quality issue: too many parameters, no type hints
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            return a + b + c + d + e + f
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0

# Quality issues: unused variables, long lines
unused_variable = "this is not used anywhere in the code and makes the code messy"
very_long_line_that_exceeds_recommended_length = "this line is way too long and should be broken up according to PEP 8 style guidelines for better readability"

class badClassName:  # Quality issue: bad naming convention
    pass
''')
    
    print(f"   Created: {sample_security_file}")
    print(f"   Created: {sample_quality_file}")
    print(f"   These files contain intentional issues for testing")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-samples":
        create_sample_files_for_testing()
        print(f"\n🧪 Run the demo again without --create-samples to analyze the sample files")
    else:
        asyncio.run(demo_enhanced_analysis()) 