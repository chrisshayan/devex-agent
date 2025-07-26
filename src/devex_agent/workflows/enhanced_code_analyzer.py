"""
Enhanced Code Analyzer - Real security and quality analysis with specific file details
Provides detailed analysis using bandit, pylint, flake8, and other professional tools
"""

# Standard library imports
import asyncio
import json
import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import performance utilities and gitignore filter
try:
    from ..knowledge_graph.utils.performance import cached, timed
    from ..knowledge_graph.utils.gitignore_filter import create_gitignore_filter
    PERFORMANCE_UTILS_AVAILABLE = True
except ImportError:
    # Fallback for when knowledge graph utils aren't available
    PERFORMANCE_UTILS_AVAILABLE = False

    def cached(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    def timed(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

class EnhancedCodeAnalyzer:
    """Enhanced code analyzer with real security and quality tools"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.supported_languages = {
            ".py": "python",
            ".js": "javascript", 
            ".ts": "typescript",
            ".java": "java",
            ".kt": "kotlin"
        }
        
        # Initialize gitignore filter if available
        if PERFORMANCE_UTILS_AVAILABLE:
            try:
                self.gitignore_filter = create_gitignore_filter(self.project_root)
                logger.info(f"🚫 Enhanced analysis will respect {self.gitignore_filter.get_exclusion_stats()['total_patterns']} gitignore patterns")
            except Exception as e:
                logger.warning(f"Failed to initialize gitignore filter: {e}")
                self.gitignore_filter = None
        else:
            self.gitignore_filter = None
    
    async def analyze_project_security(self) -> List[Dict[str, Any]]:
        """Run comprehensive security analysis using multiple tools in parallel"""
        logger.info("🚀 Running security analysis tools in parallel...")
        
        # Run all security analysis tools in parallel
        security_tasks = [
            self._run_bandit_analysis(),
            self._run_safety_analysis(),
            self._run_semgrep_analysis()
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*security_tasks, return_exceptions=True)
        
        # Flatten and collect results
        security_issues = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Security analysis task {i} failed: {result}")
            elif isinstance(result, list):
                security_issues.extend(result)
        
        logger.info(f"✅ Parallel security analysis complete: {len(security_issues)} issues found")
        return security_issues
    
    async def analyze_project_quality(self) -> List[Dict[str, Any]]:
        """Run comprehensive code quality analysis in parallel"""
        logger.info("🚀 Running quality analysis tools in parallel...")
        
        # Run all quality analysis tools in parallel with controlled concurrency
        quality_tasks = [
            self._run_pylint_analysis(),
            self._run_flake8_analysis(),
            self._run_mypy_analysis(),
            self._run_complexity_analysis(),
            self._run_dead_code_analysis()
        ]
        
        # Execute tasks concurrently with limited concurrency to avoid overwhelming the system
        semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent analysis tools
        
        async def bounded_task(task):
            async with semaphore:
                return await task
        
        bounded_tasks = [bounded_task(task) for task in quality_tasks]
        results = await asyncio.gather(*bounded_tasks, return_exceptions=True)
        
        # Flatten and collect results
        quality_issues = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Quality analysis task {i} failed: {result}")
            elif isinstance(result, list):
                quality_issues.extend(result)
        
        logger.info(f"✅ Parallel quality analysis complete: {len(quality_issues)} issues found")
        return quality_issues
    
    async def _run_bandit_analysis(self) -> List[Dict[str, Any]]:
        """Run Bandit security analysis for Python files"""
        try:
            # Apply gitignore filtering if available
            if self.gitignore_filter:
                # Get Python files that should be analyzed
                python_files = []
                for py_file in self.project_root.rglob("*.py"):
                    if not self.gitignore_filter.should_exclude(py_file):
                        python_files.append(str(py_file))
                
                if not python_files:
                    logger.info("🚫 No Python files to analyze after gitignore filtering")
                    return []
                
                # Run Bandit on specific files
                cmd = ["bandit"] + python_files + ["-f", "json", "-ll"]
            else:
                # Fallback to scanning the entire directory
                cmd = ["bandit", "-r", str(self.project_root), "-f", "json", "-ll"]
            
            result = await self._run_command(cmd)
            
            if result.returncode != 0 and result.returncode != 1:  # Bandit returns 1 if issues found
                logger.warning(f"Bandit returned code {result.returncode}: {result.stderr}")
                return []
            
            if not result.stdout or not result.stdout.strip():
                logger.debug("Bandit returned empty output")
                return []
            
            # Try to parse JSON, with better error handling
            try:
                bandit_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.warning(f"Bandit returned invalid JSON: {e}")
                logger.debug(f"Bandit stdout: {result.stdout[:200]}...")
                return []
            
            issues = []
            
            for result_item in bandit_data.get("results", []):
                issue = {
                    "file_path": self._make_relative_path(result_item["filename"]),
                    "line_number": result_item["line_number"],
                    "description": result_item["issue_text"],
                    "severity": self._map_bandit_severity(result_item["issue_severity"]),
                    "rule_id": result_item["test_id"],
                    "category": "security",
                    "tool": "bandit",
                    "more_info": result_item.get("more_info", "")
                }
                issues.append(issue)
            
            logger.info(f"🔍 Bandit found {len(issues)} security issues")
            return issues
            
        except Exception as e:
            logger.error(f"Bandit analysis failed: {e}")
            return []
    
    async def _run_safety_analysis(self) -> List[Dict[str, Any]]:
        """Run Safety analysis for dependency vulnerabilities"""
        try:
            # Look for requirements files
            req_files = list(self.project_root.rglob("requirements*.txt"))
            req_files.extend(list(self.project_root.rglob("pyproject.toml")))
            
            if not req_files:
                logger.debug("No requirements files found for Safety analysis")
                return []
            
            cmd = ["safety", "check", "--json"]
            result = await self._run_command(cmd, cwd=self.project_root)
            
            if result.returncode not in [0, 64]:  # Safety returns 64 if vulnerabilities found
                logger.warning(f"Safety returned code {result.returncode}: {result.stderr}")
                return []
            
            if not result.stdout or not result.stdout.strip():
                logger.debug("Safety returned empty output - no vulnerabilities found")
                return []
            
            # Try to parse JSON, with better error handling
            try:
                safety_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.warning(f"Safety returned invalid JSON: {e}")
                logger.debug(f"Safety stdout: {result.stdout[:200]}...")
                return []
            
            issues = []
            
            for vuln in safety_data:
                issue = {
                    "file_path": "dependencies",
                    "line_number": None,
                    "description": f"Vulnerability in {vuln['package_name']} {vuln['installed_version']}: {vuln['advisory']}",
                    "severity": "high",
                    "rule_id": vuln["vulnerability_id"],
                    "category": "dependency",
                    "tool": "safety"
                }
                issues.append(issue)
            
            logger.info(f"🔍 Safety found {len(issues)} dependency vulnerabilities")
            return issues
            
        except Exception as e:
            logger.error(f"Safety analysis failed: {e}")
            return []
    
    async def _run_semgrep_analysis(self) -> List[Dict[str, Any]]:
        """Run Semgrep analysis for security patterns"""
        try:
            cmd = ["semgrep", "--config=auto", "--json", str(self.project_root)]
            result = await self._run_command(cmd)
            
            if result.returncode != 0:
                logger.debug(f"Semgrep returned non-zero: {result.returncode}")
                # Continue anyway as Semgrep might return non-zero with findings
            
            if not result.stdout:
                return []
            
            semgrep_data = json.loads(result.stdout)
            issues = []
            
            for finding in semgrep_data.get("results", []):
                issue = {
                    "file_path": self._make_relative_path(finding["path"]),
                    "line_number": finding["start"]["line"],
                    "description": finding["extra"]["message"],
                    "severity": finding["extra"]["severity"],
                    "rule_id": finding["check_id"],
                    "category": "security",
                    "tool": "semgrep"
                }
                issues.append(issue)
            
            logger.info(f"🔍 Semgrep found {len(issues)} security patterns")
            return issues
            
        except Exception as e:
            logger.error(f"Semgrep analysis failed: {e}")
            return []
    
    async def _run_pylint_analysis(self) -> List[Dict[str, Any]]:
        """Run Pylint analysis for code quality"""
        try:
            # Find Python files with gitignore filtering
            python_files = []
            for py_file in self.project_root.rglob("*.py"):
                if not self.gitignore_filter or not self.gitignore_filter.should_exclude(py_file):
                    python_files.append(py_file)
            
            if not python_files:
                logger.info("🚫 No Python files to analyze after gitignore filtering")
                return []
            
            # Limit to a reasonable number of files to avoid overwhelming pylint
            python_files = python_files[:50]
            logger.info(f"🔍 Running Pylint on {len(python_files)} Python files")
            
            cmd = ["pylint", "--output-format=json", "--disable=C0111,C0103"] + [str(f) for f in python_files]
            result = await self._run_command(cmd)
            
            # Pylint returns non-zero when issues are found, that's normal
            if not result.stdout or not result.stdout.strip():
                logger.debug("Pylint returned empty output")
                return []
            
            # Try to parse JSON, with better error handling
            try:
                pylint_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.warning(f"Pylint returned invalid JSON: {e}")
                logger.debug(f"Pylint stdout: {result.stdout[:200]}...")
                return []
            
            issues = []
            
            for msg in pylint_data:
                if msg["type"] in ["error", "warning", "refactor", "convention"]:
                    issue = {
                        "file_path": self._make_relative_path(msg["path"]),
                        "line_number": msg["line"],
                        "description": msg["message"],
                        "severity": self._map_pylint_severity(msg["type"]),
                        "rule_id": msg["message-id"],
                        "category": "quality",
                        "tool": "pylint"
                    }
                    issues.append(issue)
            
            logger.info(f"🔍 Pylint found {len(issues)} quality issues")
            return issues
            
        except Exception as e:
            logger.error(f"Pylint analysis failed: {e}")
            return []
    
    async def _run_flake8_analysis(self) -> List[Dict[str, Any]]:
        """Run Flake8 analysis for Python style"""
        try:
            cmd = ["flake8", "--format=json", str(self.project_root)]
            result = await self._run_command(cmd)
            
            if result.returncode != 0:
                logger.warning(f"Flake8 returned code {result.returncode}: {result.stderr}")
            
            if not result.stdout or not result.stdout.strip():
                logger.debug("Flake8 returned empty output - no style issues found")
                return []
            
            # Flake8 JSON output is one object per line
            issues = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        issue = {
                            "file_path": self._make_relative_path(data["filename"]),
                            "line_number": data["line_number"],
                            "description": data["text"],
                            "severity": "medium",
                            "rule_id": data["code"],
                            "category": "style",
                            "tool": "flake8"
                        }
                        issues.append(issue)
                    except json.JSONDecodeError as e:
                        continue
            
            logger.info(f"🔍 Flake8 found {len(issues)} style issues")
            return issues
            
        except Exception as e:
            logger.error(f"Flake8 analysis failed: {e}")
            return []
    
    async def _run_mypy_analysis(self) -> List[Dict[str, Any]]:
        """Run MyPy analysis for type checking"""
        try:
            cmd = ["mypy", str(self.project_root), "--show-error-codes", "--no-error-summary"]
            result = await self._run_command(cmd)
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line and 'error:' in line:
                        try:
                            # Parse mypy output: file.py:line: error: message [error-code]
                            parts = line.split(':', 3)
                            if len(parts) >= 4:
                                file_path = parts[0]
                                line_num = int(parts[1])
                                message = parts[3].strip()
                                
                                issue = {
                                    "file_path": self._make_relative_path(file_path),
                                    "line_number": line_num,
                                    "description": message,
                                    "severity": "medium",
                                    "rule_id": "type-check",
                                    "category": "typing",
                                    "tool": "mypy"
                                }
                                issues.append(issue)
                        except (ValueError, IndexError):
                            continue
            
            logger.info(f"🔍 MyPy found {len(issues)} type issues")
            return issues
            
        except Exception as e:
            logger.error(f"MyPy analysis failed: {e}")
            return []
    
    async def _run_complexity_analysis(self) -> List[Dict[str, Any]]:
        """Run complexity analysis using Radon"""
        try:
            cmd = ["radon", "cc", str(self.project_root), "--json", "--min", "C"]
            result = await self._run_command(cmd)
            
            if not result.stdout:
                return []
            
            radon_data = json.loads(result.stdout)
            issues = []
            
            for file_path, functions in radon_data.items():
                for func in functions:
                    if func["complexity"] >= 10:  # High complexity threshold
                        issue = {
                            "file_path": self._make_relative_path(file_path),
                            "line_number": func["lineno"],
                            "description": f"High complexity function '{func['name']}' (complexity: {func['complexity']})",
                            "severity": "medium" if func["complexity"] < 15 else "high",
                            "rule_id": "complexity",
                            "category": "complexity",
                            "tool": "radon"
                        }
                        issues.append(issue)
            
            logger.info(f"🔍 Radon found {len(issues)} complexity issues")
            return issues
            
        except Exception as e:
            logger.error(f"Complexity analysis failed: {e}")
            return []
    
    async def _run_dead_code_analysis(self) -> List[Dict[str, Any]]:
        """Run dead code analysis using Vulture"""
        try:
            cmd = ["vulture", str(self.project_root), "--min-confidence", "80"]
            result = await self._run_command(cmd)
            
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if ':' in line and ('unused' in line or 'unreachable' in line):
                        try:
                            # Parse vulture output
                            parts = line.split(':', 2)
                            if len(parts) >= 3:
                                file_path = parts[0]
                                line_num = int(parts[1])
                                message = parts[2].strip()
                                
                                issue = {
                                    "file_path": self._make_relative_path(file_path),
                                    "line_number": line_num,
                                    "description": message,
                                    "severity": "low",
                                    "rule_id": "dead-code",
                                    "category": "quality",
                                    "tool": "vulture"
                                }
                                issues.append(issue)
                        except (ValueError, IndexError):
                            continue
            
            logger.info(f"🔍 Vulture found {len(issues)} dead code issues")
            return issues
            
        except Exception as e:
            logger.error(f"Dead code analysis failed: {e}")
            return []
    
    async def _run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a command asynchronously with better error handling"""
        try:
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.project_root
            )
            stdout, stderr = await process.communicate()
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            if process.returncode != 0:
                logger.debug(f"Command {cmd[0]} returned {process.returncode}, stderr: {stderr_str[:200]}")
            
            return subprocess.CompletedProcess(
                cmd, process.returncode, stdout_str, stderr_str
            )
        except FileNotFoundError:
            logger.warning(f"Command not found: {cmd[0]} - tool may not be installed")
            return subprocess.CompletedProcess(cmd, 127, "", f"Command not found: {cmd[0]}")
        except Exception as e:
            logger.error(f"Command failed: {' '.join(cmd)}: {e}")
            return subprocess.CompletedProcess(cmd, 1, "", str(e))
    
    def _make_relative_path(self, file_path: str) -> str:
        """Convert absolute path to relative path from project root"""
        try:
            path = Path(file_path)
            if path.is_absolute():
                return str(path.relative_to(self.project_root))
            return file_path
        except ValueError:
            return file_path
    
    def _map_bandit_severity(self, severity: str) -> str:
        """Map Bandit severity to our standard levels"""
        mapping = {
            "HIGH": "critical",
            "MEDIUM": "high", 
            "LOW": "medium"
        }
        return mapping.get(severity.upper(), "medium")
    
    def _map_pylint_severity(self, msg_type: str) -> str:
        """Map Pylint message types to severity levels"""
        mapping = {
            "error": "high",
            "warning": "medium",
            "refactor": "low",
            "convention": "low"
        }
        return mapping.get(msg_type, "medium")

# Integration function for existing workflow
async def run_enhanced_analysis(project_root: str = ".") -> Dict[str, Any]:
    """Run enhanced analysis and return results in the expected format"""
    analyzer = EnhancedCodeAnalyzer(project_root)
    
    # Run both security and quality analysis
    security_issues = await analyzer.analyze_project_security()
    quality_issues = await analyzer.analyze_project_quality()
    
    return {
        "total_files_analyzed": len(set(
            issue["file_path"] for issue in security_issues + quality_issues 
            if issue["file_path"] != "dependencies"
        )),
        "security_issues": security_issues,
        "quality_issues": quality_issues,
        "languages_detected": list(analyzer.supported_languages.values()),
        "analysis_tools_used": ["bandit", "safety", "semgrep", "pylint", "flake8", "mypy", "radon", "vulture"]
    } 