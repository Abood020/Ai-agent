from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from db_messages import save_message, save_tool_call
from sqlalchemy.orm import Session

from db import (
    SessionLocal,          
    find_books_db,
    create_order_db,
    restock_book_db,
    update_price_db,
    order_status_db,
    inventory_summary_db,
)




@tool
def find_books(q: str, by: Literal["title", "author"] = "title") -> str:
    """Search books in the library database by title or author."""
    db = SessionLocal()
    try:
        rows = find_books_db(db, q=q, by=by)
        if not rows:
            return "No books found for this query."
        lines = []
        for r in rows:
            lines.append(
                f"- {r['title']} — {r['author']} (ISBN {r['isbn']}), "
                f"price {r['price']} $, stock {r['stock']}"
            )
        return "\n".join(lines)
    finally:
        db.close()


class OrderItemInput(BaseModel):
    isbn: str = Field(..., description="Book ISBN")
    qty: int = Field(..., gt=0, description="Quantity to order")


class CreateOrderInput(BaseModel):
    customer_id: int = Field(..., description="Customer ID")
    items: List[OrderItemInput]


@tool("create_order", args_schema=CreateOrderInput)
def create_order_tool(customer_id: int, items: List[OrderItemInput]) -> str:
    """
    Create an order for a customer and reduce stock.
    Use this when the user says they bought / sold copies of specific books.
    """
    db = SessionLocal()
    try:
        items_dicts = [{"isbn": it.isbn, "qty": it.qty} for it in items]
        order_id = create_order_db(db, customer_id=customer_id, items=items_dicts)
        return f"Order {order_id} created successfully for customer {customer_id}."
    finally:
        db.close()


class RestockInput(BaseModel):
    isbn: str
    qty: int


@tool("restock_book", args_schema=RestockInput)
def restock_book_tool(isbn: str, qty: int) -> str:
    """Increase the stock of a book by a given quantity."""
    db = SessionLocal()
    try:
        new_stock = restock_book_db(db, isbn=isbn, qty=qty)
        return f"Book {isbn} restocked by {qty}. New stock = {new_stock}."
    finally:
        db.close()


class UpdatePriceInput(BaseModel):
    isbn: str
    price: float


@tool("update_price", args_schema=UpdatePriceInput)
def update_price_tool(isbn: str, price: float) -> str:
    """Update the price of a book."""
    db = SessionLocal()
    try:
        new_price = update_price_db(db, isbn=isbn, price=price)
        return f"Price of {isbn} updated to {new_price}."
    finally:
        db.close()


class OrderStatusInput(BaseModel):
    order_id: int


@tool("order_status", args_schema=OrderStatusInput)
def order_status_tool(order_id: int) -> str:
    """Get the full details and status of an order."""
    db = SessionLocal()
    try:
        data = order_status_db(db, order_id=order_id)
        order = data["order"]
        items = data["items"]
        lines = [
            f"لThe Status of Order {order['id']}",
            f"Status: {order['status']}",
        ]
        for it in items:
            pass
        return "\n".join(lines)
    finally:
        db.close()


class InventorySummaryInput(BaseModel):
    threshold: int = 5


@tool("inventory_summary", args_schema=InventorySummaryInput)
def inventory_summary_tool(threshold: int = 5) -> str:
    """List all books with stock less than or equal to the threshold."""
    db = SessionLocal()
    try:
        rows = inventory_summary_db(db, threshold=threshold)
        if not rows:
            return f"No books with stock <= {threshold}."
        lines = [f"Books with stock <= {threshold}:"]
        for r in rows:
            lines.append(
                f"- {r['title']} (ISBN {r['isbn']}), stock {r['stock']}, price {r['price']}"
            )
        return "\n".join(lines)
    finally:
        db.close()




SYSTEM_PROMPT = """
You are a helpful Library Desk Agent for a small library.
You can read and WRITE the database using the provided tools.
ALWAYS use tools whenever the user asks about:
- listing or searching books
- creating orders / selling books
- restocking books
- updating prices
- checking order status
- inventory / low-stock

Never just imagine changes; you MUST call tools to actually update the database.
Explain briefly to the user what you are doing.
Reply in the same language as the user (Arabic or English).
"""

llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

tools = [
    find_books,
    create_order_tool,
    restock_book_tool,
    update_price_tool,
    order_status_tool,
    inventory_summary_tool,
]


from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", """
        You are a helpful library desk agent. 
        You can search books, restock, update prices, view inventory, create orders.

        CRUCIAL RULES:
        - Whenever you create an order using tools, you MUST include the order id in your final answer.
        - Write it clearly in this format: "Order ID: <number>" so the librarian can copy it.
        - Also mention briefly what you did (how many copies, which book, and the new stock).

        When tools are required, call them exactly.
        Reply in the same language as the user.
    """),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])


agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    return_intermediate_steps=True,
)


def run_agent(
    message: str,
    session_id: Optional[str] = None,
    db=None,
) -> str:
    sid = session_id or "default"

    save_message(sid, "user", message)

    result = agent_executor.invoke(
        {
            "input": message,
            "chat_history": [],   
        }
    )

    steps = result.get("intermediate_steps", [])
    for step in steps:
        try:
            action, observation = step

            name = getattr(action, "tool", getattr(action, "tool_name", "unknown_tool"))

            raw_args = getattr(action, "tool_input", {})

            if isinstance(raw_args, (dict, list, str, int, float, bool)) or raw_args is None:
                args_data = raw_args
            elif hasattr(raw_args, "dict"):
                args_data = raw_args.dict()
            else:
                args_data = str(raw_args)

            save_tool_call(
                sid,
                name,
                args_data,
                {"observation": observation},
            )
        except Exception as e:
            print("Error while saving tool_call:", e)

    output = result.get("output") or result.get("final_output") or str(result)

    save_message(sid, "assistant", output)

    return output
