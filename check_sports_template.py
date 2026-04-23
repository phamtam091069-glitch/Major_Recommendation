#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from utils.constants import MAJOR_DISPLAY, MAJOR_PERSONALITY_REQUIREMENTS, SUGGESTION_VI

print("=" * 80)
print("CHECKING SPORTS MAJOR TEMPLATES")
print("=" * 80)

# Find all sports-related majors
sports_majors = [k for k in MAJOR_DISPLAY.keys() if 'the' in k.lower()]

print("\nSports majors found in MAJOR_DISPLAY:")
for major in sports_majors:
    print(f"  - {major}: {MAJOR_DISPLAY[major]}")

print("\n" + "=" * 80)
print("CHECKING MISSING TEMPLATES FOR EACH SPORTS MAJOR:")
print("=" * 80)

missing_personality = []
missing_suggestion = []

for major in sports_majors:
    has_personality = major in MAJOR_PERSONALITY_REQUIREMENTS
    has_suggestion = major in SUGGESTION_VI
    
    print(f"\n{major}:")
    print(f"  - In MAJOR_PERSONALITY_REQUIREMENTS: {has_personality}")
    print(f"  - In SUGGESTION_VI: {has_suggestion}")
    
    if not has_personality:
        missing_personality.append(major)
    if not has_suggestion:
        missing_suggestion.append(major)

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"\nMissing MAJOR_PERSONALITY_REQUIREMENTS: {missing_personality}")
print(f"Missing SUGGESTION_VI: {missing_suggestion}")

if missing_personality or missing_suggestion:
    print("\n⚠️  TEMPLATES MISSING - NEED TO BE ADDED")
else:
    print("\n✓ All templates are complete")
