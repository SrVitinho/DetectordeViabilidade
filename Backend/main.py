from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.testing.suite.test_reflection import users
from contextlib import asynccontextmanager

import auth
from User import userController
from Viabilidade import viabilidadeController
from ML.loader import load_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(userController.router)
app.include_router(viabilidadeController.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
