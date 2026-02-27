from typing import Literal, Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from src.controllers.auths import AuthController
from src.presentations.depends import get_auth_controller

router = APIRouter(prefix="/auth", tags=["Auth"])


class DevLoginRequest(BaseModel):
    email: str


class DevLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int
    email: str


@router.get("/google")
async def auth_google(
        request: Request,
        platform: Literal["web", "mobile"] = Query(default="web"),
        redirect_uri: Optional[str] = Query(None)
):
    settings = request.app.state.settings
    request.session["oauth_platform"] = platform
    request.session["redirect_uri"] = redirect_uri

    redirect_uri = f"{settings.BACKEND_URL}/api/v1/auth/google/callback"
    print("redirect_uri:", redirect_uri)

    return await request.app.state.oauth.google.authorize_redirect(
        request,
        redirect_uri=redirect_uri,
    )


@router.get("/google/callback")
async def auth_google_callback(
        request: Request,
        controller: AuthController = Depends(get_auth_controller),
):
    result = await controller.google_callback(request)
    settings = request.app.state.settings
    platform = request.session.pop("oauth_platform", "web")
    redirect_uri = request.session.pop("redirect_uri")
    print(redirect_uri)
    if platform == "mobile":
        params = urlencode({
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "user_id": result["user"]["id"],
            "email": result["user"]["email"],
        })
        return RedirectResponse(url=f"{redirect_uri}?{params}")

    redirect = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard", status_code=302)

    redirect.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=60 * 15,
    )
    redirect.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=60 * 60 * 24 * 30,
    )

    return redirect


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Logged out"}


@router.post("/dev-login", response_model=DevLoginResponse)
async def dev_login(
        request: Request,
        body: DevLoginRequest,
        controller: AuthController = Depends(get_auth_controller),
):
    """
    DEV ONLY: Login without OAuth for local development.
    Only works when DEBUG=True.
    """
    settings = request.app.state.settings

    # Security check - only allow in DEBUG mode
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")

    return await controller.dev_login(body.email, settings)
