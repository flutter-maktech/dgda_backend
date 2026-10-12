import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    print("API Documentation available at: http://localhost:8000/docs")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=1,
    )
