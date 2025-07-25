from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.routes import user, availability, calendar, agenda, team
from app.middleware import LoggingMiddleware
from starlette.middleware import Middleware
from dotenv import load_dotenv
import os
import time
from collections import defaultdict

load_dotenv()

app = FastAPI()

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Simple in-memory rate limiter (per IP)
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))
RATE_PERIOD = 1  # seconds
rate_limiters = defaultdict(list)

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    ip = request.client.host
    now = time.time()
    window = rate_limiters[ip]
    # Remove old requests
    window = [t for t in window if now - t < RATE_PERIOD]
    if len(window) >= RATE_LIMIT:
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    window.append(now)
    rate_limiters[ip] = window
    return await call_next(request)

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(availability.router, prefix="/availability", tags=["availability"])
app.include_router(calendar.router, prefix="/calendars", tags=["calendars"])
app.include_router(agenda.router, prefix="/agendas", tags=["agendas"])
app.include_router(team.router, prefix="/teams", tags=["teams"])

# FastAPI auto-generates Swagger docs at /docs and OpenAPI at /openapi.json 