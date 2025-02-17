from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import time

from .adventureai import AdventureGame
from .utils import ResourceManager

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API som påbörjat nytt spel

# API som börjar gammalts spel

# API som skickar user input tillsammans med user id

# API som skapar ny användare

# API som loggar in en användare
