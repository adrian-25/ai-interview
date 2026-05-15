"""Setup script to validate environment and dependencies."""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version is 3.11+."""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        print("   Then edit .env with your values")
        return False
    print("✅ .env file exists")
    return True


def check_env_variables():
    """Check required environment variables."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "MONGODB_URI",
        "JWT_SECRET",
        "OPENAI_API_KEY"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your-") or value.startswith("sk-your-"):
            missing.append(var)
        else:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var:
                display = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display = value[:30] + "..." if len(value) > 30 else value
            print(f"✅ {var}: {display}")
    
    if missing:
        print(f"\n❌ Missing or invalid environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    return True


def check_dependencies():
    """Check if required packages are installed."""
    try:
        import fastapi
        import motor
        import openai
        import jose
        import passlib
        print("✅ All required packages installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False


def main():
    """Run all checks."""
    print("🔍 AI Interview Coach - Backend Setup Validation\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_env_variables),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        results.append(check_func())
    
    print("\n" + "="*50)
    if all(results):
        print("✅ All checks passed! Ready to run:")
        print("   python main.py")
        print("\n   or")
        print("   uvicorn main:app --reload")
        print("\n📚 See TESTING_GUIDE.md for API testing instructions")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
