from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from agent import run_agent
from dotenv import load_dotenv
from typing import Optional  
load_dotenv()

from db import (
    get_db,
    find_books_db,
    create_order_db,
    restock_book_db,
    update_price_db,
    order_status_db,
    inventory_summary_db,
)


class OrderItem(BaseModel):
    isbn: str
    qty: int

class CreateOrderRequest(BaseModel):
    customer_id: int
    items: list[OrderItem]


class RestockRequest(BaseModel):
    isbn: str
    qty: int


class UpdatePriceRequest(BaseModel):
    isbn: str
    price: float

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None




app = FastAPI()


@app.get("/books")
def list_books(db: Session = Depends(get_db)):
    rows = db.execute(
        text("SELECT isbn, title, author, price, stock FROM books")
    ).mappings().all()
    return [dict(r) for r in rows]

@app.get("/search_books")
def search_books(
    q: str = Query(..., description="Search text"),
    by: str = Query("title", description="title or author"),
    db: Session = Depends(get_db)
):
    rows = find_books_db(db, q=q, by=by)
    return [dict(r) for r in rows]

@app.post("/create_order")
def create_order(req: CreateOrderRequest, db: Session = Depends(get_db)):
    try:
        order_id = create_order_db(
            db,
            customer_id=req.customer_id,
            items=[item.dict() for item in req.items]
        )
        return {"order_id": order_id}
    except ValueError as e:
        return {"error": str(e)}

@app.post("/restock_book")
def restock_book(req: RestockRequest, db: Session = Depends(get_db)):
    try:
        new_stock = restock_book_db(db, isbn=req.isbn, qty=req.qty)
        return {"isbn": req.isbn, "new_stock": new_stock}
    except ValueError as e:
        return {"error": str(e)}


@app.post("/update_price")
def update_price(req: UpdatePriceRequest, db: Session = Depends(get_db)):
    try:
        new_price = update_price_db(db, isbn=req.isbn, price=req.price)
        return {"isbn": req.isbn, "new_price": new_price}
    except ValueError as e:
        return {"error": str(e)}


@app.get("/order_status")
def order_status(order_id: int = Query(...), db: Session = Depends(get_db)):
    try:
        status = order_status_db(db, order_id=order_id)
        return status
    except ValueError as e:
        return {"error": str(e)}


@app.get("/inventory_summary")
def inventory_summary(threshold: int = Query(5), db: Session = Depends(get_db)):
    rows = inventory_summary_db(db, threshold=threshold)
    return {"threshold": threshold, "low_stock": rows}

@app.post("/chat")
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    """
    Free-form chat endpoint that uses the Library Agent + tools.
    """
    reply = run_agent(
        message=req.message,
        session_id=req.session_id, 
        db=db,                      
    )
    return {"reply": reply}
