from app.models.product_model import Product, ProductUpdate
from sqlmodel import Session, select
from fastapi import HTTPException


def add_new_product(product_data:Product, session: Session):
    print("adding new product")
    session.add(product_data)
    session.commit()
    session.refresh(product_data)
    return product_data

def get_all_products(session: Session):
    all_products = session.exec(select(Product)).all()
    print(f"all products {all_products}")
    return all_products


def get_product_by_id(product_id: int, session: Session):
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

def delete_product_by_id(product_id:int, session: Session):
    delete_id = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    print(f"delete id {delete_id}")
    if delete_id is None:
        raise HTTPException(status_code=404, message="Product_id not found")
    session.delete(delete_id)
    session.commit()
    return {"message": "Product deleted by id: {product_id}"}

def update_product_by_id(product_id: int, to_update_product_data: ProductUpdate, session: Session):
    update_data = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    if update_data is None:
        raise HTTPException(status_code=404, message="Product not found")
    hero_date = to_update_product_data.model_dump(exclude_unset=True)
    update_data.sqlmodel_update(hero_date)
    session.add(update_data)
    session.commit()    
    # session.refresh(update_data)
    return update_data


def validate_product_id(product_id: int, session: Session)->Product | None:
    product = session.exec(select(Product).where(Product.id == product_id)).one_or_none()
    return product

