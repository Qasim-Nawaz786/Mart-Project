from app.models.user_model import UserLogin
from sqlmodel import Session, select
from fastapi import HTTPException

def add_login_user_data(user_data:UserLogin, session: Session):
    print("adding new user")
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return user_data


# def add_item(item_data: OrderItem, session: Session):
#     print("adding new item")
#     session.add(item_data)
#     session.commit()
#     session.refresh(item_data)
#     return item_data    

def get_user(session: Session):
    get_all_user = session.exec(select(UserLogin)).all()
    print(f"all orders {get_all_user}")
    if get_all_user is None:
        raise HTTPException(status_code=404, detail="orders not found")
    return get_all_user



def delete_user_by_id(user_id:int, session: Session):
    delete_id = session.exec(select(UserLogin).where(UserLogin.User_id == user_id)).one_or_none()
    print(f"delete id {delete_id}")
    if delete_id is None:
        raise HTTPException(status_code=404, message="User_id not found")
    session.delete(delete_id)
    session.commit()
    return {"message": "User deleted by id: {delete_id}"}


# def get_item(session: Session):
#     get_all_item = session.exec(select(OrderItem)).all()
#     print(f"all orders {get_all_item}")
#     if get_all_item is None:
#         raise HTTPException(status_code=404, detail="orders not found")
#     return get_all_item

# def get_order_by_id(order_id: int, session: Session):
#     order_by_id = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
#     if order_by_id is None:
#         raise HTTPException(status_code=404, detail="order_id is not found")
#     return order_by_id  











