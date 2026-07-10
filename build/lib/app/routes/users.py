from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me')
def get_me(current_user: CurrentUser = Depends(get_current_user)) -> dict:
    return {
        'id': current_user.id,
        'authenticated': True,
        'email': current_user.email,
        'name': current_user.name,
        'roles': current_user.roles,
    }
