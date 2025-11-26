from sqlalchemy import text
from db import SessionLocal
import json


def save_message(session_id: str, role: str, content: str) -> None:

    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO messages (session_id, role, content)
                VALUES (:sid, :role, :content)
            """),
            {
                "sid": session_id,
                "role": role,
                "content": content,
            },
        )
        db.commit()
    finally:
        db.close()


def save_tool_call(session_id: str, name: str, args: dict, result: dict) -> None:

    db = SessionLocal()
    try:
        db.execute(
            text("""
                INSERT INTO tool_calls (session_id, name, args_json, result_json)
                VALUES (:sid, :name, :args, :result)
            """),
            {
                "sid": session_id,
                "name": name,
                "args": json.dumps(args, ensure_ascii=False),
                "result": json.dumps(result, ensure_ascii=False),
            },
        )
        db.commit()
    finally:
        db.close()


