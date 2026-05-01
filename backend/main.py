"""
EduPilot AI -- FastAPI Application Entry Point.
Adaptive Study Planner & Academic Performance Predictor.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db, async_session
from api.students import router as students_router
from api.predictions import router as predictions_router
from api.study_plans import router as plans_router
from api.progress import router as progress_router
from api.analytics import router as analytics_router
from api.auth import router as auth_router
from services.seed_service import seed_demo_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed demo data on startup."""
    await init_db()
    # Seed demo data on first run
    async with async_session() as db:
        try:
            seeded = await seed_demo_data(db)
            if seeded:
                print("[OK] Demo data seeded successfully")
        except Exception as e:
            print(f"[WARN] Seed skipped: {e}")
    print("[OK] EduPilot AI -- Server ready!")
    yield


app = FastAPI(
    title="EduPilot AI",
    description="Adaptive Study Planner & Academic Performance Predictor",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(auth_router)
app.include_router(students_router)
app.include_router(predictions_router)
app.include_router(plans_router)
app.include_router(progress_router)
app.include_router(analytics_router)

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
    if os.path.exists(os.path.join(FRONTEND_DIR, "assets")):
        app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")


@app.get("/")
async def serve_root():
    """Serve login page as entry point."""
    login_path = os.path.join(FRONTEND_DIR, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/dashboard")
async def serve_dashboard():
    """Serve the main dashboard."""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "EduPilot AI", "version": "2.0.0"}
