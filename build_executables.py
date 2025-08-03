#!/usr/bin/env python3
"""
Build Script for Poker Analysis Standalone Executables

This script builds both the Flask web tracker and analysis pipeline executables.
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description):
    """Run a command and print its status"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(command)}")
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} completed successfully!")
        if result.stdout.strip():
            print("Output summary:")
            # Show only last few lines to avoid spam
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:
                print(f"  {line}")
    else:
        print(f"❌ {description} failed!")
        print("Error:")
        print(result.stderr)
        return False
    
    return True

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

def check_venv():
    """Check if we're in a virtual environment with PyInstaller"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller found: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller not found!")
        print("Please install it with: pip install pyinstaller")
        return False

def main():
    print("🏗️  Building Poker Analysis Standalone Executables")
    print("=" * 60)
    
    # Check if PyInstaller is available
    if not check_venv():
        sys.exit(1)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build Flask web tracker
    print(f"\n🌐 Building Flask Web Tracker...")
    if not run_command([
        "pyinstaller", 
        "app.spec"
    ], "Building poker_web_tracker executable"):
        print("❌ Failed to build web tracker!")
        return False
    
    # Build analysis pipeline
    print(f"\n📊 Building Analysis Pipeline...")
    if not run_command([
        "pyinstaller", 
        "run_analysis.spec"
    ], "Building poker_analysis executable"):
        print("❌ Failed to build analysis pipeline!")
        return False
    
    print(f"\n🎉 Build completed successfully!")
    print(f"\n📦 Executables created in 'dist/' folder:")
    
    # List the created executables
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        for file in os.listdir(dist_dir):
            if os.path.isfile(os.path.join(dist_dir, file)):
                file_path = os.path.join(dist_dir, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"   • {file} ({file_size:.1f} MB)")
    
    print(f"\n💡 Usage:")
    print(f"   Web Tracker: ./dist/poker_web_tracker")
    print(f"   Analysis:    ./dist/poker_analysis <hand_log_file> [hero_name]")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Test the executables with your data")
    print(f"   2. Copy them to your target systems")
    print(f"   3. For the web tracker, ensure templates/, static/, and data/ folders are in the same directory")

if __name__ == "__main__":
    main()