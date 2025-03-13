import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.api.v1.endpoints.game:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
