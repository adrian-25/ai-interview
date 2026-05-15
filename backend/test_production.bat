@echo off
REM Production API Testing Script (Windows)

if "%1"=="" (
    echo Error: API URL required
    echo Usage: test_production.bat https://your-api-url.com
    exit /b 1
)

set API_URL=%1
echo Testing Production API: %API_URL%
echo.

REM Test 1: Health Check
echo Test 1: Health Check
curl -s "%API_URL%/health"
echo.

REM Test 2: Create Account
echo.
echo Test 2: Create Account
curl -X POST "%API_URL%/api/auth/signup" ^
    -H "Content-Type: application/json" ^
    -d "{\"email\":\"test-%RANDOM%@example.com\",\"password\":\"Test1234\"}"
echo.

echo.
echo See test_production.sh for full automated testing
echo Or use Postman/Thunder Client for manual testing
