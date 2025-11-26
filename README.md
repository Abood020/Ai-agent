# Library Desk Agent

This project implements a simple Library Desk Agent as part of a training and submission task.
The idea is to provide a virtual assistant for library staff that can:

* Answer questions about books (search by title or author)
* Create orders for specific customers
* Restock books
* Update book prices
* Retrieve the status of an existing order
* Generate reports for low-stock books

The agent does not hallucinate or assume database changes. All operations must be executed through defined tools that interact directly with the database.

---

## Project Structure

The project is organized into three main parts:

* `app/` – Streamlit frontend UI
* `server/` – FastAPI backend, agent logic, tools, and business operations
* `db/` – SQL scripts for creating and seeding the SQLite database (`schema.sql` and `seed.sql`)

Additionally, the root directory includes:

* `library.db` – SQLite database generated after running migrations/seed
* `.env.example` – Environment variable template (OpenAI key, database path, model provider, etc.)
* `.gitignore` – Excludes virtual environments, compiled files, and other unneeded artifacts

---

## Directory Layout

```bash
library-agent/
├── app/
│   └── streamlit_app.py       
│
├── db/
│   ├── schema.sql             
│   └── seed.sql                
│
├── server/
│   ├── agent.py                
│   ├── config.py               
│   ├── db.py                   
│   ├── db_messages.py          
│   ├── main.py                
│   ├── requirements.txt        
│   └── tools.py                
│
├── .env.example                
├── .gitignore                  
├── library.db                  
└── README.md

