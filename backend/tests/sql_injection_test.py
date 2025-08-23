# tests/sql_injection_test.py
import httpx
import asyncio
from urllib.parse import quote

async def test_sql_injection():
    base_url = "http://localhost:8042"
    
    test_cases = [
        # Basic SQL injection tests
        {
            "url": f"{base_url}/api/v1/auth/login",
            "method": "POST",
            "data": {"username": "admin' OR '1'='1", "password": "test"},
            "description": "Basic SQL injection in login"
        },
        {
            "url": f"{base_url}/api/v1/auth/login",
            "method": "POST", 
            "data": {"username": "admin'--", "password": "test"},
            "description": "SQL comment injection"
        },
        # Time-based blind SQL injection
        {
            "url": f"{base_url}/api/v1/auth/login",
            "method": "POST",
            "data": {"username": "admin' AND (SELECT pg_sleep(5))--", "password": "test"},
            "description": "Time-based blind SQLi"
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for i, test in enumerate(test_cases, 1):
            try:
                print(f"\n🔍 Test {i}: {test['description']}")
                print(f"Payload: {test['data']}")
                
                start_time = asyncio.get_event_loop().time()
                
                if test["method"] == "POST":
                    response = await client.post(test["url"], data=test["data"])
                else:
                    response = await client.get(test["url"], params=test["data"])
                
                response_time = asyncio.get_event_loop().time() - start_time
                
                print(f"Status: {response.status_code}")
                print(f"Response time: {response_time:.2f}s")
                print(f"Response: {response.text[:100]}...")
                
                # Analysis
                if response.status_code == 200 and "token" in response.text:
                    print("❌ ВОЗМОЖНА УЯЗВИМОСТЬ: Успешный login с инъекцией!")
                elif response_time > 4.5:
                    print("⏰ ВОЗМОЖНА УЯЗВИМОСТЬ: Time-based blind SQLi detected!")
                else:
                    print("✅ Защита работает: инъекция отклонена")
                    
            except Exception as e:
                print(f"🚫 Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting SQL Injection Tests...")
    asyncio.run(test_sql_injection())