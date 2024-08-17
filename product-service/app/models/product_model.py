from sqlmodel import SQLModel, Field, Relationship

class Product(SQLModel, table= True):
    id: int | None = Field(default=None, primary_key=True)
    name: str 
    description: str
    price: float
    expirey:str | None = None
    brand: str | None = None
    weignt:float | None = None
    category: str 
    sku: str | None = None
    # rating:list["ProductRating"] = Relationship(backpopulates= "product")



# class ProductRating(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     product_id: int = Field(foreign_key="product.id")
#     rating: int
#     review: str | None = None
#     product = Relationship(back_populates="rating")
    
    # user_id: int # One to Manu Relationship
    

class ProductUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    expiry: str | None = None      ### None means If you want to update only one value, there will be only one, the rest will not be required 
    brand: str | None = None
    weight: float | None = None
    category: str | None = None
    sku: str | None = None