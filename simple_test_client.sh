#!/bin/bash
# اسکریپت ساده تست API با curl

echo "================================================================================================="
echo "🧪 تست ساده API با curl"
echo "================================================================================================="
echo ""

BASE_URL="http://localhost:7860"

echo "🔍 بررسی سرور..."
if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo "✅ سرور در حال اجرا است"
else
    echo "❌ سرور در دسترس نیست"
    exit 1
fi

echo ""
echo "================================================================================================="
echo "📋 تست Endpoints"
echo "================================================================================================="
echo ""

# تابع تست
test_endpoint() {
    local name="$1"
    local path="$2"
    local url="$BASE_URL$path"
    
    echo "🧪 تست: $name"
    echo "   URL: $url"
    
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$url" 2>&1)
    http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d':' -f2)
    body=$(echo "$response" | grep -v "HTTP_CODE")
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo "   ✅ Status: $http_code"
        echo "   Response: ${body:0:200}..."
    else
        echo "   ❌ Status: $http_code"
        if [ -n "$body" ]; then
            echo "   Error: ${body:0:150}"
        fi
    fi
    echo ""
}

# اجرای تست‌ها
test_endpoint "Root" "/"
test_endpoint "Health" "/health"
test_endpoint "API Resources Stats" "/api/resources/stats"
test_endpoint "API Resources List" "/api/resources/list"

echo "================================================================================================="
echo "✅ تست‌ها کامل شد"
echo "================================================================================================="
