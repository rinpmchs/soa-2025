from database import engine, Base

def init_db():
    # print(f"🔍 Connecting to database: {engine.url}")  # Debugging info
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()