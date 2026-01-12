from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.app.config import Settings
from src.app.errors import TokenError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


TokenType = Literal["access", "refresh"]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _build_payload(
        *,
        subject: str,
        token_type: TokenType,
        expires_delta: timedelta,
        extra_claims: dict[str, Any] | None = None,
) -> dict[str, Any]:
    now = _utcnow()
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return payload


def create_access_token(
        *,
        subject: str,
        settings: Settings,
        extra_claims: dict[str, Any] | None = None,
        expires_minutes: int | None = None,
) -> str:
    expire = timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = _build_payload(
        subject=subject,
        token_type="access",
        expires_delta=expire,
        extra_claims=extra_claims,
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def create_refresh_token(
        *,
        subject: str,
        settings: Settings,
        extra_claims: dict[str, Any] | None = None,
        expires_days: int | None = None,
) -> str:
    expire = timedelta(days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = _build_payload(
        subject=subject,
        token_type="refresh",
        expires_delta=expire,
        extra_claims=extra_claims,
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def decode_token(
        token: str,
        *,
        settings: Settings,
        expected_type: TokenType | None = None,
) -> dict[str, Any]:
    try:
        options = {"verify_aud": bool(settings.AUDIENCE)}
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.AUDIENCE,
            issuer=settings.ISSUER,
            options=options,
        )
    except JWTError as e:
        raise TokenError("Invalid or expired token") from e

    if expected_type and payload.get("type") != expected_type:
        raise TokenError(f"Wrong token type. Expected '{expected_type}'")

    if "sub" not in payload:
        raise TokenError("Token missing 'sub'")

    return payload


@dataclass
class AccumulatedTreasure:
    current_amount: int
    time_to_full_minutes: int


def calculate_accumulated_treasure(
        current_amount: int,
        capacity: int,
        production_rate: int,  # Per hour
        last_collect_date: Optional[datetime],
) -> AccumulatedTreasure:
    if last_collect_date is None:
        return AccumulatedTreasure(
            current_amount=current_amount,
            time_to_full_minutes=int((capacity - current_amount) / production_rate * 60) if production_rate > 0 else 0
        )

    now = datetime.now(timezone.utc)
    hours_elapsed = (now - last_collect_date).total_seconds() / 3600

    generated = int(production_rate * hours_elapsed)
    new_amount = min(current_amount + generated, capacity)

    remaining_capacity = capacity - new_amount
    time_to_full = int(remaining_capacity / production_rate * 60) if production_rate > 0 else 0

    return AccumulatedTreasure(
        current_amount=new_amount,
        time_to_full_minutes=time_to_full
    )
