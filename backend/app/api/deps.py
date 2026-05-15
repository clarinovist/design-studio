from app.core.config import settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import ROLE_ADMIN, User

security = HTTPBearer(auto_error=False)


def _is_development_environment() -> bool:
    return (settings.ENVIRONMENT or "").strip().lower() in {"development", "dev", "local"}


def _allow_dev_email_bypass(request: Request) -> bool:
    if not settings.ALLOW_DEV_AUTH_BYPASS:
        return False
    if not _is_development_environment():
        return False
    return not request.url.path.startswith("/api/internal/")


def _parse_operator_admin_emails() -> set[str]:
    raw = settings.OPERATOR_ADMIN_EMAILS or ""
    return {email.strip().lower() for email in raw.split(",") if email.strip()}


def is_admin_user(user: User) -> bool:
    if (user.role or "").strip().lower() == ROLE_ADMIN:
        return True
    return (user.email or "").strip().lower() in _parse_operator_admin_emails()


async def get_optional_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    dev_email = request.headers.get("X-User-Email") if _allow_dev_email_bypass(request) else None

    email: str | None = None
    name: str | None = None

    if not credentials:
        if dev_email:
            email = dev_email
            name = "Dev User"
        else:
            return None
    else:
        try:
            token = credentials.credentials
            payload = verify_token(token)
            email = payload.get("email")
            name = payload.get("name")
            if not email:
                return None
        except Exception:
            return None

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        from app.core.credit_costs import DEFAULT_CREDITS

        user = User(
            email=email,
            name=name or "Unknown User",
            provider="google",
            credits_remaining=DEFAULT_CREDITS,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await get_optional_current_user(request=request, credentials=credentials, db=db)
    if not user:
        raise UnauthorizedError(
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not is_admin_user(current_user):
        raise ForbiddenError(detail="Admin access required")
    return current_user
