"""
Process SonarQube issues and create a summary
"""
import json
from collections import defaultdict

with open("tmp/sonar_issues.json", "r", encoding="utf-8") as f:
    data = json.load(f)

issues = data["all_issues"]

print("\n=== SONARQUBE ISSUES SUMMARY ===\n")
print(f"Total issues: {len(issues)}\n")

# Group by file
by_file = defaultdict(list)
for issue in issues:
    component = issue.get("component", "")
    if ":" in component:
        file_path = component.split(":", 1)[1]
    else:
        file_path = component
    by_file[file_path].append(issue)

# Print summary
for file_path, file_issues in sorted(by_file.items()):
    print(f"\n📄 {file_path} ({len(file_issues)} issues)")
    for issue in file_issues:
        rule = issue.get("rule", "UNKNOWN")
        severity = issue.get("severity", "UNKNOWN")
        issue_type = issue.get("type", "UNKNOWN")
        line = issue.get("line", "N/A")
        message = issue.get("message", "No message")
        print(f"  - Line {line}: [{severity}] {issue_type} | {rule}")
        print(f"    {message[:100]}")

# Save organized summary
summary = {
    "total": len(issues),
    "by_file": {}
}

for file_path, file_issues in sorted(by_file.items()):
    summary["by_file"][file_path] = []
    for issue in file_issues:
        summary["by_file"][file_path].append({
            "rule": issue.get("rule"),
            "severity": issue.get("severity"),
            "type": issue.get("type"),
            "line": issue.get("line"),
            "message": issue.get("message"),
            "key": issue.get("key")
        })

with open("tmp/issues_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"\n\n✅ Summary saved to tmp/issues_summary.json")

