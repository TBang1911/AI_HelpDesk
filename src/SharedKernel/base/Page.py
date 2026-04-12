import math
from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

class Page(BaseModel, Generic[T]):
    content: List[T]
    page_number: int
    page_size: int
    total_elements: int

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return math.ceil(self.total_elements / self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page_number < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page_number > 1

    class Config:
        from_attributes = True