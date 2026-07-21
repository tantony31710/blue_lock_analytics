import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

# Setup root path for imports
ROOT_WORKSPACE = os.path.abspath(os.path.dirname(__file__))
if ROOT_WORKSPACE not in sys.path:
    sys.path.insert(0, ROOT_WORKSPACE)

# Import the FastAPI app from the telemetry_gateway module
sys.path.insert(0, os.path.join(ROOT_WORKSPACE, ".."))
from telemetry_gateway.API import app

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wrap the FastAPI app with Mangum for Vercel serverless functions
handler = Mangum(app)
