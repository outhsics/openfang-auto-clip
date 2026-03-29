#!/bin/bash
#
# OpenFang API - Quick Test Script
#
# This script tests all API endpoints
#

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "🧪 OpenFang API Test Suite"
echo "========================"
echo "API URL: $BASE_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo "📋 Test 1: Health Check"
HEALTH=$(curl -s "$BASE_URL/api/v1/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASS${NC} - API is healthy"
else
    echo -e "${RED}❌ FAIL${NC} - API health check failed"
    exit 1
fi
echo ""

# Test 2: List Jobs (should be empty initially)
echo "📋 Test 2: List Jobs"
JOBS=$(curl -s "$BASE_URL/api/v1/jobs")
echo "   Jobs: $JOBS"
echo -e "${GREEN}✅ PASS${NC} - Jobs endpoint working"
echo ""

# Test 3: Upload File (if demo transcript exists)
DEMO_TRANSCRIPT="../examples/demo/sample_level2_transcript.srt"
if [ -f "$DEMO_TRANSCRIPT" ]; then
    echo "📋 Test 3: Upload File"
    UPLOAD=$(curl -s -X POST "$BASE_URL/api/v1/upload" \
        -F "file=@$DEMO_TRANSCRIPT")

    if echo "$UPLOAD" | grep -q "file_id"; then
        FILE_ID=$(echo "$UPLOAD" | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])")
        echo -e "${GREEN}✅ PASS${NC} - File uploaded (ID: $FILE_ID)"
    else
        echo -e "${RED}❌ FAIL${NC} - Upload failed"
        echo "   Response: $UPLOAD"
    fi
    echo ""
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - Demo transcript not found at $DEMO_TRANSCRIPT"
    echo ""
fi

# Test 4: Process (with uploaded file or local path)
if [ -n "$FILE_ID" ]; then
    echo "📋 Test 4: Process with uploaded file"
    PROCESS=$(curl -s -X POST "$BASE_URL/api/v1/process" \
        -H "Content-Type: application/json" \
        -d "{\"level\": 2, \"uploaded_file_id\": \"$FILE_ID\"}")
elif [ -f "$DEMO_TRANSCRIPT" ]; then
    echo "📋 Test 4: Process with local path"
    PROCESS=$(curl -s -X POST "$BASE_URL/api/v1/process" \
        -H "Content-Type: application/json" \
        -d "{\"level\": 2, \"transcript_path\": \"$(pwd)/$DEMO_TRANSCRIPT\"}")
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - Process test (no file available)"
    PROCESS=""
fi

if [ -n "$PROCESS" ]; then
    if echo "$PROCESS" | grep -q "job_id"; then
        JOB_ID=$(echo "$PROCESS" | python3 -c "import sys, json; print(json.load(sys.stdin)['job_id'])" 2>/dev/null)
        echo -e "${GREEN}✅ PASS${NC} - Job created (ID: $JOB_ID)"

        # Test 5: Get Job Status
        echo ""
        echo "📋 Test 5: Get Job Status"
        sleep 2  # Wait a bit for job to start
        JOB_STATUS=$(curl -s "$BASE_URL/api/v1/jobs/$JOB_ID")

        if echo "$JOB_STATUS" | grep -q "status"; then
            STATUS=$(echo "$JOB_STATUS" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)
            echo -e "${GREEN}✅ PASS${NC} - Job status: $STATUS"
        else
            echo -e "${RED}❌ FAIL${NC} - Could not get job status"
        fi
    else
        echo -e "${RED}❌ FAIL${NC} - Process failed"
        echo "   Response: $PROCESS"
    fi
    echo ""
fi

echo "========================"
echo -e "${GREEN}✅ Test Suite Complete!${NC}"
echo ""
echo "📚 API Documentation: $BASE_URL/docs"
echo "🔍 ReDoc: $BASE_URL/redoc"
