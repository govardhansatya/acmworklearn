from sqlalchemy import Column, Integer, String, Date, Boolean, Text
from data.db import Base

class Birthday(Base):
    __tablename__ = "birthdays"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    date = Column(Date)
    contact = Column(String)

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    message = Column(String)
    trigger_time = Column(String)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    description = Column(Text)
    completed = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True)
    password = Column(String)
    token = Column(String)
