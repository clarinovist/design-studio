import os
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.auth import router as auth_router
from app.api.designs import router as designs_router
from app.api.templates import router as templates_router
from app.api.projects import router as projects_router
from app.api.users import router as users_router
from app.api.history import router as history_router
from app.api.brand_kits import router as brand_kits_router
from app.api.ai_tools import router as ai_tools_router

# Initialize Sentry if DSN is provided
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.2")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
    )

# Get API version from VERSION file
try:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "../VERSION"), "r") as f:
        API_VERSION = f.read().strip()
except Exception:
    API_VERSION = "1.0.0"


tags_metadata = [
    {
        "name": "Authentication",
        "description": "Operations to authenticate and manage user access tokens.",
    },
    {
        "name": "Users",
        "description": "User profile, credits, and account management.",
    },
    {
        "name": "Brand Kits",
        "description": "Manage brand identity elements (colors, typography, logos).",
    },
    {
        "name": "Projects",
        "description": "Canvas projects and layouts management.",
    },
    {
        "name": "Designs",
        "description": "AI-powered image and design generation endpoints.",
    },
    {
        "name": "AI Tools",
        "description": "AI assistance for writing copy, generating titles, and magic text features.",
    },
    {
        "name": "History",
        "description": "Past generated designs and activity history.",
    },
    {
        "name": "Templates",
        "description": "Pre-made templates to start designs from.",
    },
]

app = FastAPI(
    title="Smart Design Studio API",
    description="""
    Comprehensive API for Smart Design Studio.

    This backend provides powerful tools to manage user accounts, brand identities (Brand Kits),
    AI-assisted design generation, copywriting, and canvas project state management.

    ### Authentication
    The API uses JWT-based authentication compatible with NextAuth. Use `Authorization: Bearer <token>` in requests.
    """,
    version=API_VERSION,
    contact={
        "name": "Smart Design Studio Support",
        "email": "support@smartdesignstudio.test",
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for Next.js frontend
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Ensure no wildcard in allow_origins when allow_credentials=True
if "*" in CORS_ORIGINS:
    allow_origins = ["*"]
    allow_credentials = False
else:
    allow_origins = CORS_ORIGINS
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(designs_router, prefix="/api/designs", tags=["Designs"])
app.include_router(templates_router, prefix="/api/templates", tags=["Templates"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(history_router, prefix="/api/history", tags=["History"])
app.include_router(brand_kits_router, prefix="/api/brand-kits", tags=["Brand Kits"])
app.include_router(ai_tools_router, prefix="/api/tools", tags=["AI Tools"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# Always mount static files for local dev uploads (fallback when S3 fails)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
os.makedirs(os.path.join(static_dir, "uploads"), exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")
