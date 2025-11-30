#!/usr/bin/env python3
"""
Temporary script to fetch SonarQube issues from the API
"""
import requests
import json
import base64
from typing import Dict, List, Any

SONAR_HOST = "https://sonarqube.dataguaviare.com.co"
PROJECT_KEY = "cacao-scan"
TOKEN = "sqa_da5bebb853ae97d3ab6cc94837519b3beee05b32"

def fetch_sonar_issues() -> List[Dict[str, Any]]:
    """Fetch all issues from SonarQube API"""
    url = f"{SONAR_HOST}/api/issues/search"
    
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{TOKEN}:'.encode()).decode()}"
    }
    
    all_issues = []
    page = 1
    page_size = 500
    
    while True:
        params = {
            "componentKeys": PROJECT_KEY,
            "resolved": "false",
            "ps": page_size,
            "p": page
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            issues = data.get("issues", [])
            if not issues:
                break
                
            all_issues.extend(issues)
            
            # Check if there are more pages
            paging = data.get("paging", {})
            if paging.get("pageIndex", 0) * paging.get("pageSize", 0) >= paging.get("total", 0):
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues: {e}")
            break
    
    return all_issues

if __name__ == "__main__":
    print("Fetching SonarQube issues...")
    issues = fetch_sonar_issues()
    
    # Group by severity and type
    by_severity = {}
    by_type = {}
    
    for issue in issues:
        severity = issue.get("severity", "UNKNOWN")
        issue_type = issue.get("type", "UNKNOWN")
        
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[issue_type] = by_type.get(issue_type, 0) + 1
    
    print(f"\nTotal issues found: {len(issues)}")
    print(f"\nBy severity: {by_severity}")
    print(f"By type: {by_type}")
    
    # Save to file
    with open("tmp_sonar_issues.json", "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    
    print("\nIssues saved to tmp_sonar_issues.json")
    
    # Print summary by file
    files = {}
    for issue in issues:
        file_path = issue.get("component", "").replace(f"{PROJECT_KEY}:", "")
        if file_path not in files:
            files[file_path] = []
        files[file_path].append({
            "key": issue.get("key"),
            "severity": issue.get("severity"),
            "type": issue.get("type"),
            "rule": issue.get("rule"),
            "message": issue.get("message"),
            "line": issue.get("line")
        })
    
    print(f"\nFiles with issues: {len(files)}")
    for file_path, file_issues in sorted(files.items(), key=lambda x: len(x[1]), reverse=True)[:20]:
        print(f"  {file_path}: {len(file_issues)} issues")

