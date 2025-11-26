from typing import List
from langchain.tools import tool

from db import (
    SessionLocal,
    find_books_db,
    create_order_db,
    restock_book_db,
    update_price_db,
    order_status_db,
    inventory_summary_db,
)


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@tool("find_books")
def find_books_tool(q: str, by: str = "title") -> list:
    """
    Search for books in the library.
    q: search text.
    by: 'title' or 'author'.
    Returns a list of matching books with isbn, title, author, price, stock.
    """
    db = SessionLocal()
    try:
        by_clean = "author" if by == "author" else "title"
        rows = find_books_db(db, q=q, by=by_clean)
        return [dict(r) for r in rows]
    finally:
        db.close()


@tool("create_order")
def create_order_tool(customer_id: int, items: List[dict]) -> dict:
    """
    Create a new order for a customer and reduce stock.
    customer_id: integer id of the customer.
    items: list of objects like {"isbn": "9780132350884", "qty": 3}.
    Returns the new order_id.
    """
    db = SessionLocal()
    try:
        order_id = create_order_db(db, customer_id=customer_id, items=items)
        return {"order_id": order_id}
    finally:
        db.close()


@tool("restock_book")
def restock_book_tool(isbn: str, qty: int) -> dict:
    """
    Restock a book by increasing its stock quantity.
    isbn: book isbn.
    qty: how many units to add.
    Returns the new stock.
    """
    db = SessionLocal()
    try:
        new_stock = restock_book_db(db, isbn=isbn, qty=qty)
        return {"isbn": isbn, "new_stock": new_stock}
    finally:
        db.close()


@tool("update_price")
def update_price_tool(isbn: str, price: float) -> dict:
    """
    Update the price of a book.
    isbn: book isbn.
    price: new price as float.
    """
    db = SessionLocal()
    try:
        new_price = update_price_db(db, isbn=isbn, price=price)
        return {"isbn": isbn, "new_price": new_price}
    finally:
        db.close()


@tool("order_status")
def order_status_tool(order_id: int) -> dict:
    """
    Get full status of an order, including customer info and items.
    order_id: id of the order.
    """
    db = SessionLocal()
    try:
        status = order_status_db(db, order_id=order_id)
        return status
    finally:
        db.close()


@tool("inventory_summary")
def inventory_summary_tool(threshold: int = 5) -> dict:
    """
    Get books whose stock is less than or equal to threshold.
    threshold: integer (default 5).
    """
    db = SessionLocal()
    try:
        rows = inventory_summary_db(db, threshold=threshold)
        return {"threshold": threshold, "low_stock": rows}
    finally:
        db.close()


TOOLS = [
    find_books_tool,
    create_order_tool,
    restock_book_tool,
    update_price_tool,
    order_status_tool,
    inventory_summary_tool,
]
