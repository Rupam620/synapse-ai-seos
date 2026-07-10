from __future__ import annotations

from typing import List

from app.repositories.backlog_repository import BacklogItem, BacklogRepository


class BacklogService:
    def __init__(self, repository: BacklogRepository) -> None:
        self._repository = repository

    def list_items(self) -> List[BacklogItem]:
        return self._repository.list_items()

    def create_item(self, title: str) -> BacklogItem:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("title must not be empty")
        return self._repository.create_item(clean_title)
