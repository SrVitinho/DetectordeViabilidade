from fastapi import FastAPI
import uvicorn

from .routers import teste

app = FastAPI()

app.include_router(teste.router, prefix="/api/v1", tags=["teste"])

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)