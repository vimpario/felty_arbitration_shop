from pydantic import BaseModel, Field

class ProductIDModel(BaseModel):
    id: int

class ProductModel(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: int = Field(..., gt=0)
    category_id: int = Field(..., gt=0)
    file_id: str | None = None
    hidden_content: str= Field(...,min_length=1)
    is_buyed: bool = Field(default=False)  
    #NOW IT SAVE PRODUCT WITH FILE