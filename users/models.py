from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
#
# from sqlalchemy import create_engine
# from sqlalchemy.orm import declarative_base
# from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, func
# from sqlalchemy.orm import sessionmaker
# import logging
#
# logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
#
# url = "postgresql://user:password@localhost:5432/test"
# engine = create_engine(url)  # подключение к бд
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# session = SessionLocal()
# Base = declarative_base()  # базовый класс для SQLAlchemy-моделей
#
#
# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String(50), unique=True, nullable=False)
#     email = Column(String(100), unique=True, nullable=False)
#     password_hash = Column(String, nullable=False)
#     first_name = Column(String(50))
#     last_name = Column(String(50))
#     birth_date = Column(Date)
#     phone_number = Column(String(20))
#     created_at = Column(TIMESTAMP, server_default=func.now())
#     updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
#
#
# Base.metadata.create_all(bind=engine)
#
# session.commit()
