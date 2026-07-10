from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BacklogItem:
    id: int
    title: str
    completed: bool = False


class BacklogRepository:
    def __init__(self) -> None:
        self._items: Dict[int, BacklogItem] = {
            1: BacklogItem(id=1, title="Initial backlog item", completed=False)
        }
        self._next_id: int = 2

    def list_items(self) -> List[BacklogItem]:
        return list(self._items.values())

    def get_item(self, item_id: int) -> BacklogItem | None:
        return self._items.get(item_id)

    def create_item(self, title: str) -> BacklogItem:
        item = BacklogItem(id=self._next_id, title=title, completed=False)
        self._items[self._next_id] = item
        self._next_id += 1
        return item
