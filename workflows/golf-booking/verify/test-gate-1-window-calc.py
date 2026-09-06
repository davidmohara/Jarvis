#!/usr/bin/env python3
"""
Test Gate 1 Booking Window Pre-Check calculation.

Scenario: Workflow runs on Wednesday, September 9 at 11:00 PM CST (midnight EST Sept 10).
Target booking: September 18 at 1:00 PM.
Expected: PASS (9 days from Sept 10 is within 8-day window? NO — should FAIL)

Wait, let me recalculate:
- Runtime: Wed Sept 9, 11 PM CST = Thu Sept 10, 12 AM EST (midnight)
- "Today" at runtime (date +%Y-%m-%d in EST): 2026-09-10
- Target date: 2026-09-18
- Days from Sept 10 to Sept 18: 8 days
- Window threshold: ≤ 8 days
- Result: PASS ✓

But the test name says "pass as valid" — let me verify the math:
Sept 10 -> Sept 11 (1) -> Sept 12 (2) -> Sept 13 (3) -> Sept 14 (4) -> Sept 15 (5) -> Sept 16 (6) -> Sept 17 (7) -> Sept 18 (8)
= 8 days exactly. PASS.
"""

from datetime import datetime, timedelta
import sys
import json

def calculate_days_until_target(today_str, target_str):
    """
    Calculate days from today to target date.
    Args:
        today_str: YYYY-MM-DD format (the runtime "today")
        target_str: YYYY-MM-DD format (target booking date)
    Returns:
        Number of days (int)
    """
    today = datetime.strptime(today_str, "%Y-%m-%d").date()
    target = datetime.strptime(target_str, "%Y-%m-%d").date()
    delta = target - today
    return delta.days

def gate_1_check(today_str, target_str, target_time_str="13:00", max_days=8):
    """
    Gate 1 Booking Window Pre-Check.

    Args:
        today_str: Runtime "today" in YYYY-MM-DD (when workflow executes)
        target_str: Target booking date in YYYY-MM-DD
        target_time_str: Target time in HH:MM (informational only for Gate 1)
        max_days: Maximum days ahead (default 8)

    Returns:
        dict with status, days_out, and pass/fail
    """
    days_out = calculate_days_until_target(today_str, target_str)

    result = {
        "today": today_str,
        "target_date": target_str,
        "target_time": target_time_str,
        "days_out": days_out,
        "window_threshold": max_days,
        "status": "PASS" if days_out <= max_days else "FAIL",
        "reason": f"{days_out} days from {today_str} to {target_str}"
    }

    if days_out <= max_days:
        result["gate_1"] = "PASS"
        result["action"] = "Proceed to step-02 (login)"
    else:
        result["gate_1"] = "FAIL"
        result["action"] = "Abort. Set status: awaiting-window. Do not substitute date."

    return result

# Test case: Wed Sept 9 at 11 PM CST = Thu Sept 10 at midnight EST
# Target: Sept 18 at 1:00 PM
test_result = gate_1_check(
    today_str="2026-09-10",
    target_str="2026-09-18",
    target_time_str="13:00",
    max_days=8
)

print("=" * 70)
print("GATE 1 BOOKING WINDOW PRE-CHECK TEST")
print("=" * 70)
print()
print(f"Scenario: Workflow runs Wed Sept 9, 11:00 PM CST")
print(f"          (= Thu Sept 10, 12:00 AM EST — midnight)")
print()
print(f"Runtime 'today' (EST):     {test_result['today']}")
print(f"Target booking date:       {test_result['target_date']}")
print(f"Target time:               {test_result['target_time']}")
print()
print(f"Days until target:         {test_result['days_out']} days")
print(f"Window threshold:          ≤ {test_result['window_threshold']} days")
print()
print(f"Gate 1 Result:             {test_result['gate_1']}")
print(f"Expected:                  PASS")
print()

# Verify the test passes
if test_result['gate_1'] == "PASS":
    print("✓ TEST PASSED")
    print()
    print(f"  Booking {test_result['target_date']} at {test_result['target_time']} is valid.")
    print(f"  Window is open. Workflow will proceed to step-02 (login).")
    sys.exit(0)
else:
    print("✗ TEST FAILED")
    print()
    print(f"  Expected Gate 1: PASS")
    print(f"  Actual Gate 1:   {test_result['gate_1']}")
    print(f"  Reason: {test_result['reason']}")
    sys.exit(1)
