from app.models.order_model import Order,UpdateOrderitem
from sqlmodel import Session, select
from fastapi import HTTPException

def add_new_order(order_data:Order, session: Session):
    print("adding new order")
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data


# def add_item(item_data: OrderItem, session: Session):
#     print("adding new item")
#     session.add(item_data)
#     session.commit()
#     session.refresh(item_data)
#     return item_data    

def get_all_orders(session: Session):
    get_all_order = session.exec(select(Order)).all()
    print(f"all orders {get_all_order}")
    if get_all_order is None:
        raise HTTPException(status_code=404, detail="orders not found")
    return get_all_order

# def get_item(session: Session):
#     get_all_item = session.exec(select(OrderItem)).all()
#     print(f"all orders {get_all_item}")
#     if get_all_item is None:
#         raise HTTPException(status_code=404, detail="orders not found")
#     return get_all_item

def get_order_by_id(order_id: int, session: Session):
    order_by_id = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order_by_id is None:
        raise HTTPException(status_code=404, detail="order_id is not found")
    return order_by_id  



def cancle_order_by_id(order_item_id: int, session: Session):
    # Step 1: Get the Inventory Item by ID
    order_item = session.exec(select(Order).where(Order.id == order_item_id)).one_or_none()
    if order_item is None:
        raise HTTPException(status_code=404, detail="Order Item not found")
    # Step 2: Delete the Inventory Item
    session.delete(order_item)
    session.commit()
    return {"message": "Order Deleted Successfully"}


# def delete_item(item_data_id: int, session = Session):
#     item_to_delete = session.exec(select(OrderItem).where(OrderItem.id == item_data_id)).one_or_none()
#     if item_to_delete is None:
#         raise HTTPException(status_code=404, detail="Item not found")
#     session.delete(item_to_delete)
#     session.commit()
#     return {"message": "Item Deleted Successfully"}


# def update_item(item_data_id: int, to_update_item_data: UpdateOrderitem, session: Session):
#     update_data = session.exec(select(OrderItem).where(OrderItem.id == item_data_id)).one_or_none()
#     if update_data is None:
#         raise HTTPException(status_code=404, message="Item not found")
#     hero_date = to_update_item_data.model_dump(exclude_unset=True)
#     update_data.sqlmodel_update(hero_date)
#     session.add(update_data)
#     session.commit()
#     return update_data






