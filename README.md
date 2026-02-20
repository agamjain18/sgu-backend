# SGU Backend

This is a FastAPI-based backend connected to a SQLite database using SQLAlchemy.

## Setup

1.  **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the application**:
    ```bash
    uvicorn main:app --reload
    ```

The API will be available at `http://127.0.0.1:8000`.
You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Project Structure

- `main.py`: The FastAPI application and CRUD endpoints.
- `models.py`: SQLAlchemy database models.
- `schemas.py`: Pydantic schemas for data validation.
- `database.py`: Database connection and session management.
- `requirements.txt`: Python dependencies.
- `sql_app.db`: SQLite database file (created automatically on first run).
