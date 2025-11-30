#!/usr/bin/env python3
"""
Script to fetch SonarQube issues for the cacao-scan project.
"""
import os
import sys
import json
import requests
from typing import Dict, List, Any

SONARQUBE_URL = "https://sonarqube.dataguaviare.com.co"
PROJECT_KEY = "cacao-scan"


def get_sonarqube_issues(token: str | None = None) -> List[Dict[str, Any]]:
    """
    Fetch all issues from SonarQube API.
    
    Args:
        token: SonarQube authentication token (optional)
    
    Returns:
        List of issues
    """
    issues_url = f"{SONARQUBE_URL}/api/issues/search"
    
    params = {
        "componentKeys": PROJECT_KEY,
        "resolved": "false",  # Only unresolved issues
        "ps": 500,  # Page size (max 500)
        "p": 1
    }
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    all_issues = []
    page = 1
    
    try:
        while True:
            params["p"] = page
            response = requests.get(issues_url, params=params, headers=headers, timeout=30)
            
            if response.status_code == 401:
                print("ERROR: Authentication required. Please provide SONARQUBE_TOKEN environment variable.")
                sys.exit(1)
            
            if response.status_code != 200:
                print(f"ERROR: Failed to fetch issues. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                sys.exit(1)
            
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
        
        return all_issues
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to SonarQube: {e}")
        sys.exit(1)


def main():
    """Main function."""
    token = os.getenv("SONARQUBE_TOKEN")
    
    if not token:
        print("WARNING: SONARQUBE_TOKEN not found. Attempting without authentication...")
        print("If this fails, set SONARQUBE_TOKEN environment variable.")
    else:
        print(f"Using token: {token[:10]}...")
    
    print(f"Fetching issues for project: {PROJECT_KEY}")
    print(f"SonarQube URL: {SONARQUBE_URL}")
    print("")
    
    try:
        issues = get_sonarqube_issues(token)
    except SystemExit:
        print("\nFailed to fetch issues. Please check your SONARQUBE_TOKEN or network connection.")
        return []
    
    print(f"\nFound {len(issues)} issues")
    
    # Group by severity and type
    by_severity = {}
    by_type = {}
    
    for issue in issues:
        severity = issue.get("severity", "UNKNOWN")
        issue_type = issue.get("type", "UNKNOWN")
        
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_type[issue_type] = by_type.get(issue_type, 0) + 1
    
    print("\nIssues by severity:")
    for severity, count in sorted(by_severity.items()):
        print(f"  {severity}: {count}")
    
    print("\nIssues by type:")
    for issue_type, count in sorted(by_type.items()):
        print(f"  {issue_type}: {count}")
    
    # Save to JSON file
    output_file = "tmp/sonarqube_issues.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(issues, f, indent=2, ensure_ascii=False)
    
    print(f"\nIssues saved to: {output_file}")
    
    # Print summary by file
    print("\nIssues by file:")
    by_file = {}
    for issue in issues:
        component = issue.get("component", "").split(":")[-1] if ":" in issue.get("component", "") else issue.get("component", "")
        by_file[component] = by_file.get(component, 0) + 1
    
    for file_path, count in sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {file_path}: {count} issues")
    
    return issues


if __name__ == "__main__":
    main()

