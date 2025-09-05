import uvicorn

if __name__ == "__main__":
    # Production-ready uvicorn configuration
    uvicorn.run(
        "app.main:app",  # Use import string format for reloading
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        workers=2,  # Adjust based on your server capacity
        log_level="debug",
        access_log=True,
        server_header=False,  
        date_header=False, 
    )