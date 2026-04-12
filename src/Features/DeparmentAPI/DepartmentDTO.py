from typing import Optional
from pydantic import BaseModel, Field

class DepartmentBaseDTO(BaseModel):
    name: Optional[str] = Field(default=None, example="Kỹ thuật", description="Tên phòng ban")

class DepartmentCreateDTO(DepartmentBaseDTO):
    pass

class DepartmentUpdateDTO(BaseModel):
    name: Optional[str] = Field(default=None, example="Kỹ thuật", description="Tên phòng ban")

class DepartmentSearchRequest(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Page size")
    q: Optional[str] = Field(None, description="Search query")