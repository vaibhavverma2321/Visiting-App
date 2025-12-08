from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)

    cards = relationship("VisitingCard", back_populates="owner", cascade="all, delete")


class VisitingCard(Base):
    __tablename__ = "visiting_cards"

    id = Column(Integer, primary_key=True, index=True)

    person_name = Column(String, nullable=False)
    designation = Column(String, nullable=True)
    company_name = Column(String, nullable=False)

    email = Column(String, nullable=True)
    address = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="cards")
    phone_numbers = relationship("PhoneNumber", back_populates="card", cascade="all, delete")

class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False)

    card_id = Column(Integer, ForeignKey("visiting_cards.id"))
    card = relationship("VisitingCard", back_populates="phone_numbers")