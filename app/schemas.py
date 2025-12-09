from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class VisitingCardCreate(BaseModel):
    person_name: str
    designation: Optional[str] = None
    company_name: str

    phone_numbers: List[str]

    email: Optional[EmailStr] = None
    address: Optional[str] = None
    description: Optional[str] = None
