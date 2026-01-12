from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import Response

from src.controllers.auths import AuthController

router = APIRouter(prefix="/auth", tags=["Users"])


@router.get("/google")
async def auth_google(request: Request):
    return await request.state.oauth.google.authorize_redirect(
        request,
        redirect_uri=f"{request.state.settings.BACKEND_URL}/auth/google/callback"
    )


@router.get("/google/callback")
async def auth_google_callback(
        redirect_uri: str,
        request: Request,
        response: Response,
        controller: AuthController
):
    return await controller.google_callback(redirect_uri, request, response)
