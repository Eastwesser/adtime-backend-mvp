from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.core.dependencies import admin_required, manager_required
from app.schemas.user import UserResponse

router = APIRouter(prefix="/test", tags=["Test"])
templates = Jinja2Templates(directory="templates")

@router.get("/admin-only")
async def admin_test(user: UserResponse = Depends(admin_required)):
    return {"message": "Welcome admin!", "user_role": user.role}

@router.get("/manager-only")  
async def manager_test(user: UserResponse = Depends(manager_required)):
    return {"message": "Welcome manager!", "user_role": user.role}

@router.get("/oauth", response_class=HTMLResponse)
async def test_oauth_page(request: Request):
    """Test page for OAuth2 flows"""
    return templates.TemplateResponse("test_oauth.html", {"request": request})

@router.get("/payments", response_class=HTMLResponse)  
async def test_payments_page(request: Request):
    """Test page for payment flows"""
    return templates.TemplateResponse("test_payments.html", {"request": request})