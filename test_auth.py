import asyncio
import sys
import httpx

async def test_backend():
    print("Testing backend authentication flow...")
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(base_url=base_url) as client:
        # 1. Health check
        res = await client.get("/health")
        print(f"1. Health Check: {res.status_code} -> {res.json()}")
        assert res.status_code == 200

        # 2. Login as default seeded admin
        login_data = {
            "email": "admin@dgda.gouv.cd",
            "password": "Admin@DGDA2026!"
        }
        res = await client.post("/api/v1/auth/login", json=login_data)
        print(f"2. Admin Login: {res.status_code}")
        assert res.status_code == 200
        tokens = res.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print(f"   Logged in admin: {tokens['user']['email']}, Role: {tokens['user']['role']}")

        # 3. Access protected /me route
        headers = {"Authorization": f"Bearer {access_token}"}
        res = await client.get("/api/v1/auth/me", headers=headers)
        print(f"3. Get Current User (/me): {res.status_code} -> {res.json()['email']}")
        assert res.status_code == 200

        # 4. Register a regular user
        import random
        rand_num = random.randint(1000, 9999)
        reg_data = {
            "email": f"officer{rand_num}@dgda.cd",
            "username": f"officer_{rand_num}",
            "full_name": "Douane Officer",
            "password": "Password123!"
        }
        res = await client.post("/api/v1/auth/register", json=reg_data)
        print(f"4. Register User: {res.status_code}")
        assert res.status_code == 201
        user_tokens = res.json()
        print(f"   Registered: {user_tokens['user']['email']}")

        # 5. Refresh token test
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        print(f"5. Token Refresh: {res.status_code}")
        assert res.status_code == 200
        new_tokens = res.json()
        assert "access_token" in new_tokens
        print("   Fresh Access Token acquired successfully!")

    print("\n All Authentication tests passed flawlessly!")

if __name__ == "__main__":
    asyncio.run(test_backend())
