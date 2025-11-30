#!/usr/bin/env python3
"""
Script to analyze and organize SonarQube issues for correction.
"""
import json
from collections import defaultdict
from typing import Dict, List, Any

def analyze_issues():
    """Analyze issues and organize them for correction."""
    with open("tmp/sonarqube_issues.json", "r", encoding="utf-8") as f:
        issues = json.load(f)
    
    # Group by file and rule
    by_file = defaultdict(lambda: defaultdict(list))
    by_rule = defaultdict(list)
    by_severity_type = defaultdict(lambda: defaultdict(int))
    
    for issue in issues:
        component = issue.get("component", "")
        file_path = component.split(":")[-1] if ":" in component else component
        rule = issue.get("rule", "UNKNOWN")
        severity = issue.get("severity", "UNKNOWN")
        issue_type = issue.get("type", "UNKNOWN")
        line = issue.get("line", 0)
        message = issue.get("message", "")
        
        by_file[file_path][rule].append({
            "line": line,
            "message": message,
            "severity": severity,
            "type": issue_type,
            "key": issue.get("key", "")
        })
        
        by_rule[rule].append(issue)
        by_severity_type[severity][issue_type] += 1
    
    # Print summary
    print("=" * 80)
    print("SONARQUBE ISSUES ANALYSIS")
    print("=" * 80)
    print(f"\nTotal issues: {len(issues)}")
    print("\nBy Severity and Type:")
    for severity in ["BLOCKER", "CRITICAL", "MAJOR", "MINOR"]:
        if severity in by_severity_type:
            print(f"\n  {severity}:")
            for issue_type, count in by_severity_type[severity].items():
                print(f"    {issue_type}: {count}")
    
    # Top issues by rule
    print("\n\nTop 20 Rules (most common issues):")
    rule_counts = {rule: len(issues_list) for rule, issues_list in by_rule.items()}
    for rule, count in sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {rule}: {count} issues")
    
    # Issues by file (top 30)
    print("\n\nTop 30 Files with most issues:")
    file_counts = {file_path: sum(len(issues_list) for issues_list in rules.values()) 
                   for file_path, rules in by_file.items()}
    for file_path, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:30]:
        print(f"  {file_path}: {count} issues")
        # Show rule breakdown for top files
        if count >= 5:
            for rule, issues_list in sorted(by_file[file_path].items(), 
                                          key=lambda x: len(x[1]), reverse=True)[:3]:
                print(f"    - {rule}: {len(issues_list)} issues")
    
    # Save organized issues by file
    organized = {}
    for file_path, rules in by_file.items():
        organized[file_path] = {}
        for rule, issues_list in rules.items():
            organized[file_path][rule] = sorted(issues_list, key=lambda x: x["line"])
    
    with open("tmp/sonarqube_issues_organized.json", "w", encoding="utf-8") as f:
        json.dump(organized, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nOrganized issues saved to: tmp/sonarqube_issues_organized.json")
    
    # Create correction plan
    print("\n\nCORRECTION PLAN:")
    print("=" * 80)
    
    # Priority 1: BLOCKER and CRITICAL
    blocker_critical = [i for i in issues if i.get("severity") in ["BLOCKER", "CRITICAL"]]
    if blocker_critical:
        print("\n1. PRIORITY 1: BLOCKER & CRITICAL issues")
        by_file_priority = defaultdict(list)
        for issue in blocker_critical:
            component = issue.get("component", "")
            file_path = component.split(":")[-1] if ":" in component else component
            by_file_priority[file_path].append(issue)
        
        for file_path, file_issues in sorted(by_file_priority.items()):
            print(f"\n   {file_path}: {len(file_issues)} issues")
            for issue in sorted(file_issues, key=lambda x: x.get("line", 0)):
                print(f"     Line {issue.get('line')}: {issue.get('rule')} - {issue.get('message')}")
    
    # Priority 2: MAJOR
    major = [i for i in issues if i.get("severity") == "MAJOR"]
    if major:
        print(f"\n2. PRIORITY 2: MAJOR issues ({len(major)} total)")
        by_file_major = defaultdict(list)
        for issue in major:
            component = issue.get("component", "")
            file_path = component.split(":")[-1] if ":" in component else component
            by_file_major[file_path].append(issue)
        
        print(f"   Files with MAJOR issues: {len(by_file_major)}")
        for file_path, count in sorted(by_file_major.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"     {file_path}: {len(count)} issues")
    
    # Priority 3: MINOR
    minor = [i for i in issues if i.get("severity") == "MINOR"]
    if minor:
        print(f"\n3. PRIORITY 3: MINOR issues ({len(minor)} total)")
        print(f"   Will be corrected after BLOCKER, CRITICAL, and MAJOR issues")

if __name__ == "__main__":
    analyze_issues()

