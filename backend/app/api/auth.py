from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.schemas.error import ERROR_RESPONSES

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user with an email and password. Grants initial credits automatically upon successful registration.",
    responses={
        201: {"description": "User successfully registered"},
        400: ERROR_RESPONSES[400],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Registers a new user with email and password."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    # Create new user
    hashed_password = get_password_hash(data.password)
    user = User(
        email=data.email,
        name=data.name,
        password_hash=hashed_password,
        provider="credentials",
    )

    db.add(user)

    # Needs a flush to get the user ID
    await db.flush()

    from app.services.credit_service import log_credit_change

    await log_credit_change(db, user, 10, "Bonus pendaftaran")

    await db.commit()
    await db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
    description="Authenticates a user using their email and password. Used primarily as a fallback or for direct API access matching NextAuth mechanics.",
    responses={
        200: {"description": "User successfully authenticated"},
        401: ERROR_RESPONSES[401],
        422: ERROR_RESPONSES[422],
        500: ERROR_RESPONSES[500],
    }
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Verifies user credentials. Used by frontend NextAuth."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account uses Google Login. Please sign in with Google.",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return user
