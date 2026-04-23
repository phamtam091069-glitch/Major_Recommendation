#!/usr/bin/env python3
"""
Auto-initialization script for Replit deployment.
Ensures model files exist before app starts.
"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_model_files():
    """Check if required model files exist."""
    required_files = [
        BASE_DIR / "models" / "rf_model.pkl",
        BASE_DIR / "models" / "ohe.pkl",
        BASE_DIR / "models" / "tfidf.pkl",
        BASE_DIR / "models" / "classes.pkl",
        BASE_DIR / "models" / "majors.json",
    ]
    
    missing = [f for f in required_files if not f.exists()]
    return len(missing) == 0, missing

def generate_model():
    """Generate model if missing."""
    print("⚠️  Model files not found. Generating...")
    print("📊 Step 1: Generate training data...")
    os.system("python data/generate_balanced_students.py")
    print("🤖 Step 2: Train model...")
    os.system("python train_model.py")
    print("✅ Model generation complete!")

if __name__ == "__main__":
    print("🔍 Checking model files...")
    exists, missing = check_model_files()
    
    if not exists:
        print(f"❌ Missing files: {[f.name for f in missing]}")
        generate_model()
    else:
        print("✅ All model files found!")
