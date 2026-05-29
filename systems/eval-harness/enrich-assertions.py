#!/usr/bin/env python3
"""
Analyze and enrich assertion files with missing checks.
Adds file_exists, file_min_bytes, and file_contains checks based on workflow patterns.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Derive IES_ROOT from this script's location
IES_ROOT = Path(__file__).resolve().parents[2]
ASSERTIONS_DIR = IES_ROOT / "systems" / "eval-harness" / "assertions"

# Standard patterns for common workflow types
WORKFLOW_PATTERNS = {
    "daily-review": {
        "output_paths": ["reviews/daily/*.md", "memory/working/daily-review-*.md"],
        "content_patterns": ["(?i)(today|task|priority|tomorrow|completed|wins)"],
        "min_bytes": 300
    },
    "weekly-review": {
        "output_paths": ["memory/working/weekly-review-*.md"],
        "content_patterns": ["(?i)(wins|rocks|delegation|week|review)"],
        "min_bytes": 1000
    },
    "morning-briefing": {
        "output_paths": ["reviews/daily/*-morning-briefing.md", "memory/working/morning-briefing-*.md"],
        "content_patterns": ["(?i)(calendar|priority|meeting|today)"],
        "min_bytes": 500
    },
    "default": {
        "output_paths": ["memory/working/{name}-*.md"],
        "content_patterns": ["(?i)(complete|done|finished|output|result)"],
        "min_bytes": 200
    }
}

def analyze_assertion_file(assertion_file: Path):
    """Analyze an assertion file and identify missing checks."""
    try:
        with open(assertion_file, "r") as f:
            data = json.load(f)

        name = data.get("name", "unknown")
        assertions = data.get("assertions", [])
        
        # Check what's already present
        has_yaml_field = any(a.get("check") == "yaml_field_equals" for a in assertions)
        has_file_exists = any(a.get("check") == "file_exists" for a in assertions)
        has_file_min_bytes = any(a.get("check") == "file_min_bytes" for a in assertions)
        has_file_contains = any(a.get("check") == "file_contains" for a in assertions)
        
        # Get workflow pattern
        pattern = WORKFLOW_PATTERNS.get(name, WORKFLOW_PATTERNS["default"])
        if name in WORKFLOW_PATTERNS:
            pattern = WORKFLOW_PATTERNS[name]
        else:
            pattern = WORKFLOW_PATTERNS["default"].copy()
            pattern["output_paths"] = [p.replace("{name}", name) for p in pattern["output_paths"]]
        
        missing_checks = []
        additions = []
        
        # Add file_exists if missing
        if not has_file_exists:
            for output_path in pattern["output_paths"]:
                additions.append({
                    "id": f"{name[:8]}-001-exists",
                    "check": "file_exists",
                    "path": output_path,
                    "description": f"{name} output file was written"
                })
        
        # Add file_min_bytes if missing
        if not has_file_min_bytes:
            for output_path in pattern["output_paths"]:
                additions.append({
                    "id": f"{name[:8]}-002-substantive",
                    "check": "file_min_bytes",
                    "path": output_path,
                    "min_bytes": pattern["min_bytes"],
                    "description": f"{name} output is substantive (>{pattern['min_bytes']} bytes)"
                })
        
        # Add file_contains if missing
        if not has_file_contains:
            for i, content_pattern in enumerate(pattern["content_patterns"]):
                for output_path in pattern["output_paths"]:
                    additions.append({
                        "id": f"{name[:8]}-00{i+3}-content",
                        "check": "file_contains",
                        "path": output_path,
                        "pattern": content_pattern,
                        "description": f"{name} output contains expected content"
                    })
        
        return {
            "file": assertion_file.name,
            "name": name,
            "current_checks": len(assertions),
            "has_yaml_field": has_yaml_field,
            "has_file_exists": has_file_exists,
            "has_file_min_bytes": has_file_min_bytes,
            "has_file_contains": has_file_contains,
            "additions": additions
        }
        
    except Exception as e:
        print(f"Error analyzing {assertion_file.name}: {e}")
        return None

def enrich_assertion_file(assertion_file: Path, additions: list):
    """Add missing checks to an assertion file."""
    try:
        with open(assertion_file, "r") as f:
            data = json.load(f)
        
        assertions = data.get("assertions", [])
        
        # Add new assertions
        assertions.extend(additions)
        
        # Update the file
        data["assertions"] = assertions
        
        with open(assertion_file, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"  ✓ Enriched {assertion_file.name} with {len(additions)} checks")
        
    except Exception as e:
        print(f"  ✗ Failed to enrich {assertion_file.name}: {e}")

def main():
    """Analyze and enrich all assertion files."""
    import sys
    
    dry_run = "--dry-run" in sys.argv
    
    print("Analyzing assertion files...\n")
    
    analysis_results = []
    
    for assertion_file in ASSERTIONS_DIR.glob("*.json"):
        if assertion_file.name in ["template.json", "README.md"]:
            continue
            
        result = analyze_assertion_file(assertion_file)
        if result:
            analysis_results.append(result)
    
    # Summary
    print(f"\nAnalyzed {len(analysis_results)} assertion files")
    print(f"Missing file_exists: {sum(1 for r in analysis_results if not r['has_file_exists'])}")
    print(f"Missing file_min_bytes: {sum(1 for r in analysis_results if not r['has_file_min_bytes'])}")
    print(f"Missing file_contains: {sum(1 for r in analysis_results if not r['has_file_contains'])}")
    
    # Show sample additions for files with changes
    print("\n" + "="*60)
    total_additions = sum(len(r['additions']) for r in analysis_results)
    print(f"Total additions to apply: {total_additions}")
    print("="*60)
    
    # Show first few files that would be changed
    files_with_changes = [r for r in analysis_results if r['additions']]
    if files_with_changes:
        print("\nSample changes (first 5 files):")
        for result in files_with_changes[:5]:
            print(f"\n{result['file']}:")
            for addition in result['additions'][:3]:
                print(f"  + {addition['check']}: {addition['path']}")
    
    if dry_run:
        print("\nDry run mode - no changes applied. Run without --dry-run to apply.")
    else:
        # Apply changes
        print("\nApplying enrichments...")
        for result in analysis_results:
            if result['additions']:
                enrich_assertion_file(ASSERTIONS_DIR / result['file'], result['additions'])
        print("\nDone!")

if __name__ == "__main__":
    main()
