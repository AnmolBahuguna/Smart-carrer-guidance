#!/usr/bin/env python
"""
Check if SmartCareer is ready for deployment
Verifies all required files and configurations
"""

import os
import sys

def print_check(item, status, message=""):
    """Print colored check result"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {item}")
    if message:
        print(f"   → {message}")

def check_file_exists(filename):
    """Check if file exists"""
    exists = os.path.exists(filename)
    if exists:
        size = os.path.getsize(filename)
        print_check(f"{filename}", True, f"{size} bytes")
    else:
        print_check(f"{filename}", False, "NOT FOUND - Create this file!")
    return exists

def check_gitignore():
    """Check if .gitignore contains .env"""
    if not os.path.exists('.gitignore'):
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
        has_env = '.env' in content
        if has_env:
            print_check(".gitignore contains .env", True, "Good! Secrets protected")
        else:
            print_check(".gitignore contains .env", False, "Add .env to .gitignore!")
        return has_env

def check_requirements():
    """Check requirements.txt has gunicorn"""
    if not os.path.exists('requirements.txt'):
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
        has_gunicorn = 'gunicorn' in content
        has_flask = 'Flask' in content
        
        if has_gunicorn and has_flask:
            print_check("requirements.txt has dependencies", True, "Flask + Gunicorn found")
        else:
            missing = []
            if not has_flask: missing.append("Flask")
            if not has_gunicorn: missing.append("gunicorn")
            print_check("requirements.txt complete", False, f"Missing: {', '.join(missing)}")
        
        return has_gunicorn and has_flask

def check_procfile():
    """Check Procfile content"""
    if not os.path.exists('Procfile'):
        return False
    
    with open('Procfile', 'r') as f:
        content = f.read()
        correct = 'gunicorn app:app' in content
        if correct:
            print_check("Procfile configured correctly", True)
        else:
            print_check("Procfile configured correctly", False, "Should contain: web: gunicorn app:app")
        return correct

def check_env_example():
    """Check .env.example doesn't have real keys"""
    if not os.path.exists('.env.example'):
        print_check(".env.example exists", False, "Not critical but recommended")
        return True
    
    with open('.env.example', 'r') as f:
        content = f.read()
        has_real_openai = content.count('sk-') > 0 and 'your-' not in content
        has_real_gemini = 'AIza' in content and 'your-' not in content
        
        if has_real_openai or has_real_gemini:
            print_check(".env.example has placeholder keys", False, 
                       "SECURITY RISK! Real keys found. Use placeholders!")
            return False
        else:
            print_check(".env.example has placeholder keys", True, "Good! No real keys exposed")
            return True

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("🔍 SMARTCAREER DEPLOYMENT READINESS CHECK")
    print("="*60 + "\n")
    
    print("📁 CHECKING REQUIRED FILES:\n")
    
    checks = []
    
    # Required files
    checks.append(check_file_exists('app.py'))
    checks.append(check_file_exists('requirements.txt'))
    checks.append(check_file_exists('Procfile'))
    checks.append(check_file_exists('runtime.txt'))
    checks.append(check_file_exists('.gitignore'))
    
    print("\n📋 CHECKING CONFIGURATIONS:\n")
    
    # Configuration checks
    checks.append(check_gitignore())
    checks.append(check_requirements())
    checks.append(check_procfile())
    checks.append(check_env_example())
    
    print("\n📦 CHECKING TEMPLATES:\n")
    
    # Template files
    templates = [
        'templates/index.html',
        'templates/quiz.html',
        'templates/chatbot.html',
        'templates/dashboard.html',
        'templates/login.html',
        'templates/register.html'
    ]
    
    for template in templates:
        checks.append(check_file_exists(template))
    
    # Summary
    print("\n" + "="*60)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("="*60)
    
    total = len(checks)
    passed = sum(checks)
    failed = total - passed
    
    print(f"\nTotal Checks: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    readiness = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📈 Readiness Score: {readiness:.1f}%")
    
    print("\n" + "="*60)
    
    if readiness == 100:
        print("🎉 READY TO DEPLOY!")
        print("\n✅ All checks passed! You can deploy now.")
        print("\nNext Steps:")
        print("1. Read DEPLOY_CHECKLIST.md")
        print("2. Push to GitHub")
        print("3. Deploy to Render/Railway/PythonAnywhere")
        print("\n🚀 Recommended: Render.com (Free & Easy)")
    elif readiness >= 80:
        print("⚠️  ALMOST READY")
        print("\n✅ Most checks passed, but fix the failures above before deploying.")
    else:
        print("❌ NOT READY YET")
        print("\n⚠️ Multiple issues found. Fix the failures above first.")
    
    print("="*60 + "\n")
    
    return readiness == 100

if __name__ == "__main__":
    ready = main()
    sys.exit(0 if ready else 1)
