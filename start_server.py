"""Simple server startup script"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Crypto API Monitor Backend")
    print("Server will be available at: http://localhost:7860")
    print("Frontend: http://localhost:7860/index.html")
    print("HF Console: http://localhost:7860/hf_console.html")
    print("API Docs: http://localhost:7860/docs")
    print("=" * 60)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=7860,
        log_level="info",
        access_log=True
    )
