from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/backlog", tags=["backlog"], dependencies=[Depends(get_current_user)])


@router.get("")
def list_backlog() -> list[dict[str, str]]:
    return [{"id": "item-1", "title": "Test"}]
