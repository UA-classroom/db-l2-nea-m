import os
import db as db

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from schemas import (
    RegisterUser, RegisterStaff, RegisterBooking, RegisterReview, RegisterService, RegisterPayment, UpdatePayment, UserFavoriteInput, LoginUser
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
app.mount("/img", StaticFiles(directory="img"), name="images")
app.mount("/backend_js", StaticFiles(directory="backend_js"), name="backend")

@app.get("/")
def serve_index():
    return FileResponse(os.path.join("frontend", "index.html"))

@app.get("/login")
def serve_index():
    return FileResponse(os.path.join("frontend", "login.html"))

@app.get("/mina_sidor")
def serve_index():
    return FileResponse(os.path.join("frontend", "mina_sidor.html"))

@app.get("/business")
def serve_index():
    return FileResponse(os.path.join("frontend", "business.html"))

@app.get("/services")
def serve_index():
    return FileResponse(os.path.join("frontend", "services.html"))


@app.get("/users/{user_id}")
def get_user(user_id: int):
    try:
        return db.get_user(user_id)
    
    except ValueError:
        raise HTTPException(status_code=404, detail="User not registered.")


@app.get("/businesses/{business_id}")
def get_business(business_id: int):
    try:
        return db.get_business(business_id)
    
    except ValueError:
        raise HTTPException(status_code=404, detail="Business not registered.")

@app.get("/businesses")
def get_all_businesses():
    try:
        return db.get_all_businesses()
    
    except ValueError:
        raise HTTPException(status_code=404, detail="Business not registered.")

@app.get("/reviews/staff/{staff_id}")
def get_reviews_by_staff(staff_id: int):
    try:
        return db.get_reviews_by_staff(staff_id)
    
    except ValueError:
        raise HTTPException(status_code=404, detail="No reviews found for staff member")
    
@app.post("/reviews")
def register_review(review_input: RegisterReview):
    try:
        return db.register_review(review_input)
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/users")
def register_user(user_input: RegisterUser):
    try:
        return db.register_user(user_input)
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/staff")
def register_staff(staff_input: RegisterStaff):
    try:
        return db.register_staff(staff_input)
    
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/register_booking")
def register_booking(booking_input: RegisterBooking):
    try:
        return db.register_booking(booking_input)

    except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/add_services")
def register_service(service_input: RegisterService):
    try:
        return db.register_service(service_input)

    except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/payments")
def register_payment(payment_input: RegisterPayment):
    try:
        return db.register_payment(payment_input)

    except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")

@app.patch("/payments/{payment_id}")
def update_payment(payment_update: UpdatePayment):
    try:
        return db.update_payment(payment_update)

    except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/favorites")
def add_favorite(favorite_input: UserFavoriteInput):
    try:
        return db.add_favorite(favorite_input)

    except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/favorites")
def get_user_favorites(request: Request):
    user_id = request.cookies.get("user_id")
    return db.get_user_favorites(user_id)

@app.delete("/favorites")
def remove_favorite(favorite_input: UserFavoriteInput):
    try:
        return db.remove_favorite(favorite_input)

    except ValueError as ve:
            raise HTTPException(status_code=404, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int):
    try:
        return db.delete_booking(booking_id)

    except ValueError as ve:
            raise HTTPException(status_code=404, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/login")
def login(email_input: LoginUser):
    try:
        user = db.login(email_input.email)
    
    except ValueError as ve:
            raise HTTPException(status_code=401, detail=str(ve))
    except RuntimeError:
            raise HTTPException(status_code=500, detail="Internal server error")

    response = JSONResponse({"message": "Inloggad"})
    response.set_cookie(
        key="user_id",
        value=str(user["user_id"]),
        path="/",          
        httponly=False,   
        samesite="lax"
    )

    return response

@app.get("/list_bookings")
def get_my_bookings(request: Request):

    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    try:
         return db.get_my_bookings(int(user_id))
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Internal server error")