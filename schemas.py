from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, constr
from typing import Optional

class RegisterUser(BaseModel):
    role: int
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    gender: str = Field(..., max_length=20)
    date_of_birth: str
    email: EmailStr
    phone_number: str = Field(..., max_length=50)

class User(BaseModel):
    user_id: int
    role: int
    first_name: str
    last_name: str
    gender: str
    date_of_birth: str
    email: EmailStr
    phone_number: str
    created_at: datetime

class LoginUser(BaseModel):
    email: EmailStr

class RegisterBusiness(BaseModel):
    business_name: str = Field(..., max_length=50)
    adress: str = Field(..., max_length=50)
    phone_number: str = Field(..., max_length=50)
    description: str = Field(..., max_length=500)
    business_url_page: str = Field(..., max_length=100)

class Business(BaseModel):
    business_id: int
    business_name: str
    adress: str
    phone_number: str
    description: str
    business_url_page: str
    created_at: datetime

class RegisterStaff(BaseModel):
    business_id: int
    first_name: str = Field(..., max_length=20)
    last_name: str = Field(..., max_length=20)
    description_of_role: str = Field(..., max_length=500)

class Staff(BaseModel):
    staff_id: int
    business_id: int
    first_name: str
    last_name: str
    description_of_role: str
    created_at: datetime

class RegisterBooking(BaseModel):
    user_id: int
    staff_id: int
    service_id: int
    start_time: datetime

class Booking(BaseModel):
    booking_id: int
    user_id: int
    staff_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    is_active: bool

class RegisterReview(BaseModel):
    user_id: int
    staff_id: int
    title: str = Field(..., max_length=50)
    comment: str = Field(..., max_length=500)
    rating: int

class Review(BaseModel):
    review_id: int
    user_id: int
    staff_id: int
    title: str
    comment: str
    rating: int
    created_at: datetime

class RegisterService(BaseModel):
    business_id: int
    category_id: int
    service_name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    price: int
    duration_minutes: int

class Service(BaseModel):
    service_id: int
    business_id: int
    category_id: int
    service_name: str
    description: str
    price: int
    duration_minutes: int
    created_at: datetime

class RegisterPayment(BaseModel):
    payment_method_id: int
    user_id: int
    booking_id: int
    status_id: int
    price: float
    currency: str = Field(..., max_length=3)

class Payment(BaseModel):
    payment_id: int
    payment_method_id: int
    user_id: int
    booking_id: int
    status_id: int
    price: float
    currency: str
    created_at: datetime

class UpdatePayment(BaseModel):
    payment_id: int
    status_id: int

class UserFavoriteInput(BaseModel):
    user_id: int
    business_id: int

class UserFavorite(BaseModel):
    favorite_id: int
    user_id: int
    business_id: int

class ReviewCreate(BaseModel):
    user_id: int
    staff_id: int
    title: str = Field(..., max_length=50)
    comment: str = Field(..., max_length=500)
    rating: int