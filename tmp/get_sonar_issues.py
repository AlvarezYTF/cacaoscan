"""
Temporary script to fetch SonarQube issues via API
"""
import os
import requests
import json
from typing import Dict, List, Any

SONAR_URL = os.getenv("SONAR_HOST_URL", "https://sonarqube.dataguaviare.com.co")
SONAR_TOKEN = os.getenv("SONAR_TOKEN")
PROJECT_KEY = "cacao-scan"

if not SONAR_TOKEN:
    raise ValueError("SONAR_TOKEN environment variable is required")

def get_sonar_issues() -> List[Dict[str, Any]]:
    """Fetch all issues from SonarQube API"""
    url = f"{SONAR_URL}/api/issues/search"
    headers = {
        "Authorization": f"Bearer {SONAR_TOKEN}"
    }
    params = {
        "componentKeys": PROJECT_KEY,
        "resolved": "false",  # Only unresolved issues
        "ps": 500,  # Page size (max 500)
        "p": 1
    }
    
    all_issues = []
    page = 1
    
    while True:
        params["p"] = page
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
            if response.status_code == 401:
                print("Authentication failed. Check your token.")
            break
    
    return all_issues

def group_issues_by_file(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group issues by file path"""
    grouped = {}
    for issue in issues:
        component = issue.get("component", "")
        # Extract file path from component (format: project_key:path/to/file)
        if ":" in component:
            file_path = component.split(":", 1)[1]
        else:
            file_path = component
            
        if file_path not in grouped:
            grouped[file_path] = []
        grouped[file_path].append(issue)
    
    return grouped

if __name__ == "__main__":
    print("Fetching SonarQube issues...")
    issues = get_sonar_issues()
    print(f"Found {len(issues)} issues")
    
    # Group by file
    grouped = group_issues_by_file(issues)
    print(f"\nIssues grouped by {len(grouped)} files:")
    
    # Save to JSON for analysis
    output = {
        "total_issues": len(issues),
        "files_affected": len(grouped),
        "issues_by_file": grouped,
        "all_issues": issues
    }
    
    with open("tmp/sonar_issues.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\nSummary by severity:")
    severity_count = {}
    for issue in issues:
        severity = issue.get("severity", "UNKNOWN")
        severity_count[severity] = severity_count.get(severity, 0) + 1
    
    for severity, count in sorted(severity_count.items()):
        print(f"  {severity}: {count}")
    
    print("\nSummary by type:")
    type_count = {}
    for issue in issues:
        issue_type = issue.get("type", "UNKNOWN")
        type_count[issue_type] = type_count.get(issue_type, 0) + 1
    
    for issue_type, count in sorted(type_count.items()):
        print(f"  {issue_type}: {count}")
    
    print(f"\nIssues saved to tmp/sonar_issues.json")

