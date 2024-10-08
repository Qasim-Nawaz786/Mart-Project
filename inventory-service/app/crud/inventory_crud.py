from app.models.inventory_model import InventoryItem
from sqlmodel import Session, select
from fastapi import HTTPException

def add_new_inventory(inventory_data:InventoryItem, session: Session):
    print("adding new inventory")
    session.add(inventory_data)
    session.commit()
    session.refresh(inventory_data)
    return inventory_data


def get_all_inventory_items(session: Session):
    all_inventory_items = session.exec(select(InventoryItem)).all()
    return all_inventory_items

def get_inventory_by_id(inventory_id: int, session: Session):
    inventory = session.exec(select(InventoryItem).where(InventoryItem.id == inventory_id)).one_or_none()
    if inventory is None:
        raise HTTPException(status_code=404, detail="inventory not found")
    return inventory



def delete_inventory_item_by_id(inventory_item_id: int, session: Session):
    # Step 1: Get the Inventory Item by ID
    inventory_item = session.exec(select(InventoryItem).where(InventoryItem.id == inventory_item_id)).one_or_none()
    if inventory_item is None:
        raise HTTPException(status_code=404, detail="Inventory Item not found")
    # Step 2: Delete the Inventory Item
    session.delete(inventory_item)
    session.commit()
    return {"message": "Inventory Item Deleted Successfully"}


def validate_product_id(Product_id: int, session: Session)->InventoryItem | None:
    product = session.exec(select(InventoryItem).where(InventoryItem.product_id == Product_id)).one_or_none()
    return product

# def update_inventory_by_id(inventory_id: int, to_update_inventory_data: inventoryUpdate, session: Session):
#     update_data = session.exec(select(inventory).where(inventory.id == inventory_id)).one_or_none()
#     if update_data is None:
#         raise HTTPException(status_code=404, message="inventory not found")
#     hero_date = to_update_inventory_data.model_dump(exclude_unset=True)
#     update_data.sqlmodel_update(hero_date)
#     session.add(update_data)
#     session.commit()    
#     # session.refresh(update_data)
#     return update_data


