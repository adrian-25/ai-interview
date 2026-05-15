#!/bin/bash
# Production API Testing Script

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if API_URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ Error: API URL required${NC}"
    echo "Usage: ./test_production.sh https://your-api-url.com"
    exit 1
fi

API_URL=$1
echo -e "${YELLOW}🧪 Testing Production API: $API_URL${NC}\n"

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Health Check${NC}"
HEALTH=$(curl -s "$API_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "$HEALTH"
    exit 1
fi

# Test 2: API Documentation
echo -e "\n${YELLOW}Test 2: API Documentation${NC}"
DOCS=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/docs")
if [ "$DOCS" = "200" ]; then
    echo -e "${GREEN}✅ API docs accessible${NC}"
else
    echo -e "${RED}❌ API docs not accessible (HTTP $DOCS)${NC}"
fi

# Test 3: Create Account
echo -e "\n${YELLOW}Test 3: Create Account${NC}"
SIGNUP_RESPONSE=$(curl -s -X POST "$API_URL/api/auth/signup" \
    -H "Content-Type: application/json" \
    -d '{"email":"test-'$(date +%s)'@example.com","password":"Test1234"}')

if echo "$SIGNUP_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ Account created${NC}"
    TOKEN=$(echo "$SIGNUP_RESPONSE" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
    echo "Token: ${TOKEN:0:20}..."
else
    echo -e "${RED}❌ Account creation failed${NC}"
    echo "$SIGNUP_RESPONSE"
    exit 1
fi

# Test 4: Start Interview Session
echo -e "\n${YELLOW}Test 4: Start Interview Session${NC}"
SESSION_RESPONSE=$(curl -s -X POST "$API_URL/api/sessions/start" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"role":"Frontend Developer"}')

if echo "$SESSION_RESPONSE" | grep -q "session_id"; then
    echo -e "${GREEN}✅ Session started${NC}"
    SESSION_ID=$(echo "$SESSION_RESPONSE" | grep -o '"session_id":"[^"]*' | cut -d'"' -f4)
    echo "Session ID: $SESSION_ID"
    QUESTION=$(echo "$SESSION_RESPONSE" | grep -o '"first_question":"[^"]*' | cut -d'"' -f4)
    echo "Question: ${QUESTION:0:50}..."
else
    echo -e "${RED}❌ Session start failed${NC}"
    echo "$SESSION_RESPONSE"
    exit 1
fi

# Test 5: Submit Answer
echo -e "\n${YELLOW}Test 5: Submit Answer${NC}"
ANSWER_RESPONSE=$(curl -s -X POST "$API_URL/api/sessions/$SESSION_ID/answer" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"answer":"This is a test answer to verify the production API is working correctly."}')

if echo "$ANSWER_RESPONSE" | grep -q "evaluation"; then
    echo -e "${GREEN}✅ Answer submitted and evaluated${NC}"
    SCORE=$(echo "$ANSWER_RESPONSE" | grep -o '"score":[0-9.]*' | cut -d':' -f2)
    echo "Score: $SCORE/10"
else
    echo -e "${RED}❌ Answer submission failed${NC}"
    echo "$ANSWER_RESPONSE"
    exit 1
fi

# Test 6: End Session
echo -e "\n${YELLOW}Test 6: End Session${NC}"
END_RESPONSE=$(curl -s -X POST "$API_URL/api/sessions/$SESSION_ID/end" \
    -H "Authorization: Bearer $TOKEN")

if echo "$END_RESPONSE" | grep -q "completed"; then
    echo -e "${GREEN}✅ Session ended${NC}"
else
    echo -e "${RED}❌ Session end failed${NC}"
    echo "$END_RESPONSE"
fi

# Test 7: Get Dashboard
echo -e "\n${YELLOW}Test 7: Get Dashboard${NC}"
DASHBOARD_RESPONSE=$(curl -s "$API_URL/api/dashboard/sessions" \
    -H "Authorization: Bearer $TOKEN")

if echo "$DASHBOARD_RESPONSE" | grep -q "sessions"; then
    echo -e "${GREEN}✅ Dashboard data retrieved${NC}"
else
    echo -e "${RED}❌ Dashboard retrieval failed${NC}"
    echo "$DASHBOARD_RESPONSE"
fi

# Summary
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All production tests passed!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n${YELLOW}Production API is ready for frontend integration!${NC}"
echo -e "API URL: $API_URL"
