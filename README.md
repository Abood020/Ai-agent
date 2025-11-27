# Library Desk Agent

This project is a simple Library Desk Agent built using FastAPI, LangChain, and Streamlit. The agent can interact with a real SQLite database through dedicated tools that handle searching books, creating orders, updating stock, modifying prices, checking order status, and generating inventory summaries. All operations are done through actual tool calls—no hallucinated actions.

---

### Project Structure

```
library-agent/
├── app/                        # Streamlit frontend
│   └── streamlit_app.py
│
├── server/                     # Backend (API + agent + tools)
│   ├── agent.py
│   ├── main.py
│   ├── db.py
│   ├── db_messages.py
│   ├── config.py
│   ├── tools.py
│   └── requirements.txt
│
├── db/                         # Database scripts
│   ├── schema.sql              # Database schema (tables)
│   └── seed.sql                # Initial seed data
│
├── prompts/
│   └── system_prompt.txt       # Agent system prompt
│
├── .env.example                # Example environment variables
├── library.db                  # SQLite database
└── README.md
```


## Requirements

- Python 3.10+
- SQLite3
- OpenAI API key

---

## Setup Instructions

1. Create a virtual environment:

   Windows:
   python -m venv venv
   venv\Scripts\activate

   macOS / Linux:
   python3 -m venv venv
   source venv/bin/activate

2. Install backend dependencies:

   cd server
   pip install -r requirements.txt

3. Prepare the database:

   cd db
   sqlite3 ../library.db < schema.sql
   sqlite3 ../library.db < seed.sql

4. Create your environment file:

   cp .env.example .env
   Add your OPENAI_API_KEY inside the file.

5. Run the FastAPI backend:

   cd server
   uvicorn main:app --reload --host 127.0.0.1 --port 8001

   API docs:
   http://127.0.0.1:8001/docs

6. Run the Streamlit frontend:

   cd app
   streamlit run streamlit_app.py

---

## Notes

- All database writes are performed through LangChain tools.
- All tool calls and assistant messages are logged in tables `messages` and `tool_calls`.
- The project structure matches the required deliverables exactly.
- The repository includes schema + seed, prompts, frontend, backend, and environment example.