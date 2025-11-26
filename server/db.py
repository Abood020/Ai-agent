from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def find_books_db(db: Session, q: str, by: str = "title"):
    column = "author" if by == "author" else "title"
    sql = text(f"SELECT isbn, title, author, price, stock FROM books WHERE {column} LIKE :q")
    return db.execute(sql, {"q": f"%{q}%"}).mappings().all()


def create_order_db(db: Session, customer_id: int, items: list[dict]):
    """
    items: [{'isbn': '9780132350884', 'qty': 3}, ...]
    """
    customer = db.execute(
        text("SELECT id FROM customers WHERE id = :cid"),
        {"cid": customer_id}
    ).mappings().first()
    if not customer:
        raise ValueError(f"Customer {customer_id} not found")

    for item in items:
        isbn = item["isbn"]
        qty = int(item["qty"])
        book = db.execute(
            text("SELECT isbn, stock FROM books WHERE isbn = :isbn"),
            {"isbn": isbn}
        ).mappings().first()
        if not book:
            raise ValueError(f"Book {isbn} not found")
        if book["stock"] < qty:
            raise ValueError(f"Not enough stock for {isbn}, have {book['stock']}, need {qty}")

    try:
        res = db.execute(
            text("INSERT INTO orders (customer_id, status) VALUES (:cid, :status)"),
            {"cid": customer_id, "status": "completed"}
        )
        order_id = res.lastrowid

        for item in items:
            isbn = item["isbn"]
            qty = int(item["qty"])

            book = db.execute(
                text("SELECT price, stock FROM books WHERE isbn = :isbn"),
                {"isbn": isbn}
            ).mappings().first()

            db.execute(
                text("""
                    INSERT INTO order_items (order_id, isbn, qty, price_at_order)
                    VALUES (:oid, :isbn, :qty, :price)
                """),
                {"oid": order_id, "isbn": isbn, "qty": qty, "price": book["price"]}
            )

            db.execute(
                text("UPDATE books SET stock = stock - :qty WHERE isbn = :isbn"),
                {"qty": qty, "isbn": isbn}
            )

        db.commit()
        return order_id

    except Exception:
        db.rollback()
        raise
def restock_book_db(db: Session, isbn: str, qty: int):
    book = db.execute(
        text("SELECT isbn, stock FROM books WHERE isbn = :isbn"),
        {"isbn": isbn}
    ).mappings().first()
    if not book:
        raise ValueError(f"Book {isbn} not found")

    new_stock = book["stock"] + qty
    db.execute(
        text("UPDATE books SET stock = stock + :qty WHERE isbn = :isbn"),
        {"qty": qty, "isbn": isbn}
    )
    db.commit()
    return new_stock


def update_price_db(db: Session, isbn: str, price: float):
    book = db.execute(
        text("SELECT isbn FROM books WHERE isbn = :isbn"),
        {"isbn": isbn}
    ).mappings().first()
    if not book:
        raise ValueError(f"Book {isbn} not found")

    db.execute(
        text("UPDATE books SET price = :price WHERE isbn = :isbn"),
        {"price": price, "isbn": isbn}
    )
    db.commit()
    return price


def order_status_db(db: Session, order_id: int):
    order = db.execute(
        text("""
            SELECT o.id, o.customer_id, o.status, o.created_at,
                   c.name AS customer_name, c.email AS customer_email
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            WHERE o.id = :oid
        """),
        {"oid": order_id}
    ).mappings().first()

    if not order:
        raise ValueError(f"Order {order_id} not found")

    items = db.execute(
        text("""
            SELECT oi.isbn, b.title, oi.qty, oi.price_at_order
            FROM order_items oi
            JOIN books b ON oi.isbn = b.isbn
            WHERE oi.order_id = :oid
        """),
        {"oid": order_id}
    ).mappings().all()

    return {
        "order": dict(order),
        "items": [dict(i) for i in items],
    }


def inventory_summary_db(db: Session, threshold: int = 5):
    rows = db.execute(
        text("""
            SELECT isbn, title, author, price, stock
            FROM books
            WHERE stock <= :th
            ORDER BY stock ASC
        """),
        {"th": threshold}
    ).mappings().all()

    return [dict(r) for r in rows]
