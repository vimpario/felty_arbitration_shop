from pydantic import BaseModel, Field

class ProductIDModel(BaseModel):
    id: int

class ProductModel(BaseModel):
    name: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    price: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    field_id: str | None = None
    hidden_content: str= Field(...,min_length=5)