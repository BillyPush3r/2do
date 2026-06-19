from db.engine import create_db_and_tables
from cli import startup


if __name__ == '__main__':
    create_db_and_tables()
    startup()
