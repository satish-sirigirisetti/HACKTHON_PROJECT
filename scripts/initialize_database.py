"""Create all configured CareerAI database tables."""

from backend.database.database import initialize_database


if __name__ == "__main__":
    initialize_database()
    print("CareerAI database initialized.")