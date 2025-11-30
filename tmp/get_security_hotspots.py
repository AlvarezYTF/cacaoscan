#!/usr/bin/env python3
"""
Script to fetch Security Hotspots from SonarQube API using issues endpoint.
"""
import os
import sys
import json
import requests
from typing import Dict, List, Any

SONARQUBE_URL = "https://sonarqube.dataguaviare.com.co"
PROJECT_KEY = "cacao-scan"
TOKEN = "sqa_da5bebb853ae97d3ab6cc94837519b3beee05b32"


def get_security_hotspots_via_issues(token: str) -> List[Dict[str, Any]]:
    """
    Fetch Security Hotspots using the issues/search endpoint with type filter.
    
    Args:
        token: SonarQube authentication token
    
    Returns:
        List of security hotspots
    """
    issues_url = f"{SONARQUBE_URL}/api/issues/search"
    
    # Use token as username with Basic auth (SonarQube format)
    headers = {}
    if token:
        # Try basic auth: token as username, empty password
        import base64
        auth_string = f"{token}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        headers["Authorization"] = f"Basic {encoded_auth}"
    
    params = {
        "componentKeys": PROJECT_KEY,
        "types": "SECURITY_HOTSPOT",  # Filter by security hotspots
        "resolved": "false",
        "ps": 500,
        "p": 1
    }
    
    all_hotspots = []
    page = 1
    
    try:
        while True:
            params["p"] = page
            response = requests.get(issues_url, params=params, headers=headers, timeout=30)
            
            print(f"Request URL: {response.url}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 401:
                print("ERROR: Authentication failed. Status 401")
                print(f"Response: {response.text[:500]}")
                sys.exit(1)
            
            if response.status_code == 403:
                print("ERROR: Insufficient privileges. Status 403")
                print(f"Response: {response.text[:500]}")
                # Try without auth to see what happens
                print("\nTrying alternative approach: using token in query param...")
                params_with_token = params.copy()
                params_with_token["token"] = token
                response = requests.get(issues_url, params=params_with_token, timeout=30)
                print(f"Alternative Status: {response.status_code}")
                if response.status_code == 200:
                    print("Success with token in query param!")
                    data = response.json()
                    hotspots = data.get("issues", [])
                    if not hotspots:
                        break
                    all_hotspots.extend(hotspots)
                    paging = data.get("paging", {})
                    if paging.get("pageIndex", 0) * paging.get("pageSize", 0) >= paging.get("total", 0):
                        break
                    page += 1
                    continue
                else:
                    sys.exit(1)
            
            if response.status_code != 200:
                print(f"ERROR: Failed to fetch hotspots. Status code: {response.status_code}")
                print(f"Response: {response.text[:500]}")
                sys.exit(1)
            
            data = response.json()
            hotspots = data.get("issues", [])
            
            if not hotspots:
                break
            
            all_hotspots.extend(hotspots)
            
            # Check if there are more pages
            paging = data.get("paging", {})
            if paging.get("pageIndex", 0) * paging.get("pageSize", 0) >= paging.get("total", 0):
                break
            
            page += 1
        
        return all_hotspots
    
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to connect to SonarQube: {e}")
        sys.exit(1)


def main():
    """Main function."""
    print(f"Fetching Security Hotspots for project: {PROJECT_KEY}")
    print(f"SonarQube URL: {SONARQUBE_URL}")
    print("")
    
    try:
        hotspots = get_security_hotspots_via_issues(TOKEN)
    except SystemExit:
        print("\nFailed to fetch hotspots. Please check your token or network connection.")
        return []
    
    print(f"\nFound {len(hotspots)} security hotspots")
    
    if len(hotspots) == 0:
        print("\nNo security hotspots found. This could mean:")
        print("  1. There are no security hotspots in the project")
        print("  2. The token doesn't have permission to access security hotspots")
        print("  3. Security hotspots are stored separately and need different API endpoint")
        return []
    
    # Group by vulnerability probability and rule
    by_rule = {}
    by_severity = {}
    
    for hotspot in hotspots:
        rule = hotspot.get("rule", "UNKNOWN")
        severity = hotspot.get("severity", "UNKNOWN")
        
        by_rule[rule] = by_rule.get(rule, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
    
    print("\nHotspots by rule:")
    for rule, count in sorted(by_rule.items(), key=lambda x: x[1], reverse=True):
        print(f"  {rule}: {count}")
    
    print("\nHotspots by severity:")
    for severity, count in sorted(by_severity.items(), key=lambda x: x[1], reverse=True):
        print(f"  {severity}: {count}")
    
    # Save to JSON file
    output_file = "tmp/security_hotspots.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(hotspots, f, indent=2, ensure_ascii=False)
    
    print(f"\nHotspots saved to: {output_file}")
    
    # Print summary by file
    print("\nHotspots by file:")
    by_file = {}
    for hotspot in hotspots:
        component = hotspot.get("component", "")
        if ":" in component:
            component = component.split(":")[-1]
        by_file[component] = by_file.get(component, 0) + 1
    
    for file_path, count in sorted(by_file.items(), key=lambda x: x[1], reverse=True):
        print(f"  {file_path}: {count} hotspots")
    
    # Print first few hotspots as examples
    print("\nFirst 5 hotspots details:")
    for i, hotspot in enumerate(hotspots[:5], 1):
        print(f"\n{i}. Rule: {hotspot.get('rule', 'N/A')}")
        print(f"   Component: {hotspot.get('component', 'N/A')}")
        print(f"   Line: {hotspot.get('line', 'N/A')}")
        print(f"   Message: {hotspot.get('message', 'N/A')[:100]}")
    
    return hotspots


if __name__ == "__main__":
    main()
