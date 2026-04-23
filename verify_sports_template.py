#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verify that Sports major templates have been added successfully."""

from utils.constants import MAJOR_DISPLAY, MAJOR_PERSONALITY_REQUIREMENTS, SUGGESTION_VI

print("=" * 80)
print("VERIFYING SPORTS MAJOR TEMPLATES")
print("=" * 80)

sports_majors = [
    "Su pham Giao duc the chat",
    "Quan ly the thao"
]

print("\n✓ CHECKING MAJOR_DISPLAY:")
for major in sports_majors:
    if major in MAJOR_DISPLAY:
        print(f"  ✓ {major}: {MAJOR_DISPLAY[major]}")
    else:
        print(f"  ✗ {major}: MISSING!")

print("\n✓ CHECKING MAJOR_PERSONALITY_REQUIREMENTS:")
for major in sports_majors:
    if major in MAJOR_PERSONALITY_REQUIREMENTS:
        req = MAJOR_PERSONALITY_REQUIREMENTS[major]
        print(f"  ✓ {major}:")
        print(f"      Leadership: {req['leadership']}, Extroverted: {req['extroverted']}")
        print(f"      Responsibility: {req['responsibility']}, Communication: {req['communication']}")
    else:
        print(f"  ✗ {major}: MISSING!")

print("\n✓ CHECKING SUGGESTION_VI:")
for major in sports_majors:
    if major in SUGGESTION_VI:
        print(f"  ✓ {major}:")
        print(f"      {SUGGESTION_VI[major]}")
    else:
        print(f"  ✗ {major}: MISSING!")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

# Check for completeness
all_templates_present = all(
    major in MAJOR_DISPLAY and
    major in MAJOR_PERSONALITY_REQUIREMENTS and
    major in SUGGESTION_VI
    for major in sports_majors
)

if all_templates_present:
    print("\n✓ SUCCESS: All Sports major templates have been added!")
else:
    print("\n✗ FAILURE: Some templates are still missing!")
