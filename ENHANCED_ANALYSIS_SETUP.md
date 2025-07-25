# Enhanced Analysis Setup Guide

This guide shows how to implement the enhanced code analysis that provides specific file details, line numbers, and exact issue descriptions for the IntelliJ plugin UI.

## 🎯 What This Achieves

**Before:** Generic "Found 28 security issues" with no details
**After:** Specific file paths, line numbers, issue descriptions, severity levels, and rule IDs

## 📋 Installation Steps

### 1. Install Analysis Tools

```bash
# Core analysis tools
pip install bandit pylint flake8 mypy radon vulture safety

# Optional (requires separate installation)
# Semgrep: https://semgrep.dev/docs/getting-started/
```

### 2. Update Dependencies (Already Done)

The `pyproject.toml` has been updated with the necessary analysis tools.

### 3. Install Updated Dependencies

```bash
cd /path/to/your/devex-agent
pip install -e .  # Install with new dependencies
```

## 🧪 Test the Enhanced Analysis

### Create Sample Files with Issues

```bash
python demo_enhanced_analysis.py --create-samples
```

### Run Analysis Demo

```bash
python demo_enhanced_analysis.py
```

**Expected Output:**
```
🚀 DevEx Enhanced Analysis Demo
==================================================
🔍 Running enhanced analysis...

📊 Analysis Results:
   Files analyzed: 15
   Languages: python, javascript
   Security issues: 4
   Quality issues: 12
   Tools used: bandit, pylint, flake8, mypy, radon, vulture

🔐 Security Issues (showing first 3):
   1. sample_security_issues.py:6
      Hardcoded password in dictionary
      Severity: high | Tool: bandit

   2. sample_security_issues.py:9
      subprocess call - check for execution of untrusted input
      Severity: medium | Tool: bandit

📋 Morning Brief API Response Preview:
{
  "critical_items": [
    {
      "type": "security",
      "priority": "critical",
      "title": "Security concerns detected",
      "description": "Found 4 potential security issues",
      "action_required": true,
      "count": 4,
      "files": [
        {
          "file_path": "sample_security_issues.py",
          "line_number": 6,
          "description": "Hardcoded password in dictionary",
          "severity": "high",
          "rule_id": "B105",
          "category": "security",
          "tool": "bandit"
        }
      ]
    }
  ]
}
```

## 🚀 Run Your DevEx Agent

Start your enhanced DevEx agent:

```bash
cd /path/to/your/devex-agent
python -m src.devex_agent.main
```

The morning brief endpoint will now return detailed file information that the IntelliJ plugin can display.

## 🎨 What Your UI Will Now Show

### Before (Generic):
```
🚨 Critical Items
1. 🔴 Security concerns detected
   Found 28 potential security issues
   Type: security • Priority: critical
```

### After (Detailed):
```
🚨 Critical Items
1. 🔴 Security concerns detected
   Found 28 issues
   
   📄 config.py:45 🔴
   📄 auth.py:12 🟡  
   📄 api.py:89 🔴
   ... and 25 more files
   
   Type: security • Priority: critical
   [⚡] [📄] <- Click for details
```

### Detailed View (Click 📄):
```
Critical Item: Security concerns detected
==================================================

Type: security
Priority: critical
Action Required: Yes
Issues Found: 28

Description:
Found 28 potential security issues

Affected Files:
--------------------
1. src/config.py
   Line: 45
   Issue: Hardcoded password in dictionary
   Severity: high
   Rule: B105

2. src/auth.py
   Line: 12
   Issue: Use of insecure MD5 hash function
   Severity: medium
   Rule: B303

[... continues for all files ...]
```

## 🔧 Customization Options

### Configure Analysis Tools

Edit `src/devex_agent/workflows/enhanced_code_analyzer.py`:

```python
# Adjust severity thresholds
if func["complexity"] >= 10:  # Change complexity threshold

# Modify analysis scope
python_files = python_files[:50]  # Limit files analyzed

# Add custom rules
cmd = ["bandit", "-r", str(self.project_root), "-f", "json", "-ll", "--skip", "B101"]
```

### Add More Analysis Tools

```python
# Add ESLint for JavaScript
async def _run_eslint_analysis(self) -> List[Dict[str, Any]]:
    cmd = ["eslint", "--format", "json", str(self.project_root)]
    # ... implementation

# Add SonarQube integration
async def _run_sonar_analysis(self) -> List[Dict[str, Any]]:
    # ... implementation
```

## 🚨 Troubleshooting

### Analysis Tools Not Found

```bash
# Check if tools are installed
bandit --version
pylint --version
flake8 --version

# Install missing tools
pip install bandit pylint flake8 mypy radon vulture
```

### No Issues Found

The enhanced analyzer might not find issues if:
- Your code is already very clean
- Analysis tools aren't configured for your file types
- Files are in excluded directories (`.git/`, `__pycache__/`)

Create sample files with intentional issues:
```bash
python demo_enhanced_analysis.py --create-samples
```

### Permission Errors

Some tools might need file system access:
```bash
chmod +x /path/to/analysis/tools
```

## 📈 Performance Optimization

For large codebases:

1. **Limit file scope:**
   ```python
   python_files = python_files[:100]  # Analyze only first 100 files
   ```

2. **Exclude directories:**
   ```python
   cmd = ["bandit", "-r", str(self.project_root), "-x", "tests/,docs/"]
   ```

3. **Run analysis in background:**
   ```python
   # Run analysis asynchronously
   asyncio.create_task(run_enhanced_analysis("."))
   ```

## ✅ Success Criteria

You'll know the setup is working when:

1. ✅ Demo script runs without errors
2. ✅ Morning brief shows file paths and line numbers  
3. ✅ IntelliJ plugin displays detailed file information
4. ✅ Click actions show specific issue details
5. ✅ No more horizontal scrolling in plugin UI

## 🎉 Next Steps

With this setup, your IntelliJ plugin will transform from showing generic counts to displaying actionable, specific information that developers can immediately act upon!

The enhanced analysis provides:
- **Specific file paths** and line numbers
- **Detailed issue descriptions** from professional tools
- **Severity levels** and rule IDs for prioritization
- **Multiple analysis tools** for comprehensive coverage
- **Structured data** that the UI can display beautifully 