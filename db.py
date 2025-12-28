import psycopg2
from psycopg2.extras import RealDictCursor
from db_setup import get_connection
from schemas import (
    RegisterUser, RegisterBusiness, RegisterStaff, RegisterBooking, RegisterReview, RegisterService, RegisterPayment, ReviewCreate, UpdatePayment, UserFavoriteInput, LoginUser
)


def get_user(user_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
            user = cursor.fetchone()

        if not user:
            raise ValueError(f"User with ID {user_id} not found")          
    return user

def get_business(business_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    businesses.*,
                    business_images.image_url
                FROM businesses
                JOIN business_images
                    ON businesses.business_id = business_images.business_id
                WHERE businesses.business_id = %s;
                """,
                (business_id,)
            )
            business = cursor.fetchone()

            if not business:
                raise ValueError(f"Business with ID {business_id} not found")
            
            cursor.execute(
                """
                SELECT
                    staff.staff_id,
                    staff.first_name,
                    staff.last_name,
                    staff_availability.available_from
                FROM staff
                LEFT JOIN staff_availability
                    ON staff.staff_id = staff_availability.staff_id
                WHERE staff.business_id = %s
                ORDER BY staff.staff_id, staff_availability.available_from;
                """,
                (business_id,)
            )
            staff_rows = cursor.fetchall()

            staff_dict = {}
            for row in staff_rows:
                staff_id = row["staff_id"]

                staff_dict[staff_id] = {
                    "staff_id": staff_id,
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "availability": []
                }

                if row["available_from"]:
                    staff_dict[staff_id]["availability"].append({"available_from": row["available_from"]})

            staff = list(staff_dict.values())

            cursor.execute(
                """
                SELECT *
                FROM services
                WHERE business_id = %s
                ORDER BY service_name;
                """,
                (business_id,)
            )
            services = cursor.fetchall()

    return {
        "business": business,
        "staff": staff,
        "services": services
    }

def get_all_businesses():
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    businesses.*,
                    business_images.image_url
                FROM businesses
                LEFT JOIN business_images
                    ON businesses.business_id = business_images.business_id
                """
            )
            business = cursor.fetchall()

            if not business:
                raise ValueError
    return business

def get_reviews_by_staff(staff_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    reviews.review_id,
                    reviews.staff_id,
                    staff.last_name AS staff_last_name,
                    reviews.user_id,
                    users.last_name AS user_last_name,
                    reviews.title,
                    reviews.comment,
                    reviews.rating,
                    reviews.created_at
                FROM reviews
                JOIN users ON reviews.user_id = users.user_id
                JOIN staff ON reviews.staff_id = staff.staff_id
                WHERE reviews.staff_id = %s
                ORDER BY reviews.created_at DESC;
                """,
                (staff_id,)
            )
            reviews = cursor.fetchall()

            if not reviews:
                raise ValueError(f"No reviews found for staff member ID: {staff_id}.")
    return reviews

def register_review(review_input: RegisterReview):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO reviews (
                        user_id,
                        staff_id,
                        title,
                        comment,
                        rating
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING review_id, created_at;
                    """,
                    (
                        review_input.user_id,
                        review_input.staff_id,
                        review_input.title,
                        review_input.comment,
                        review_input.rating,
                    ),
                )

                posted_review = cursor.fetchone()

            except psycopg2.errors.NotNullViolation:
                raise ValueError(f"Missing required field")
            except psycopg2.errors.ForeignKeyViolation:
                raise ValueError(f"Invalid reference (fk)")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")
            
    return posted_review

def register_user(user_input: RegisterUser):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                        INSERT INTO users (role, first_name, last_name, gender, date_of_birth, email, phone_number)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING user_id;
                    """,
                    (user_input.role, 
                     user_input.first_name, 
                     user_input.last_name, 
                     user_input.gender, 
                     user_input.date_of_birth, 
                     user_input.email, 
                     user_input.phone_number))
                
                registering_user = cursor.fetchone()

            except psycopg2.errors.UniqueViolation:
                raise ValueError(f"Duplicate or constraint violation")
            except psycopg2.errors.NotNullViolation:
                raise ValueError(f"Missing required field")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")
            
    return registering_user

def register_staff(staff_input: RegisterStaff):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO staff (
                        business_id,
                        first_name,
                        last_name,
                        description_of_role
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING staff_id, created_at;
                    """,
                    (
                        staff_input.business_id,
                        staff_input.first_name,
                        staff_input.last_name,
                        staff_input.description_of_role,
                    ),
                )

                registering_staff = cursor.fetchone()

            except psycopg2.errors.NotNullViolation:
                raise ValueError(f"Missing required field")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")

    return registering_staff

def register_booking(booking_input: RegisterBooking):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO bookings (
                        user_id,
                        staff_id,
                        service_id,
                        start_time
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING booking_id;
                    """,
                    (
                        booking_input.user_id,
                        booking_input.staff_id,
                        booking_input.service_id,
                        booking_input.start_time
                    ),
                )

                new_booking = cursor.fetchone()

            except psycopg2.errors.NotNullViolation:
                raise ValueError(f"Missing required field")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")

    return new_booking

def register_service(service_input: RegisterService):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO services (
                        business_id,
                        category_id,
                        service_name,
                        description,
                        price,
                        duration_minutes
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING service_id, created_at;
                    """,
                    (
                        service_input.business_id,
                        service_input.category_id,
                        service_input.service_name,
                        service_input.description,
                        service_input.price,
                        service_input.duration_minutes,
                    ),
                )

                new_service = cursor.fetchone()

            except psycopg2.errors.NotNullViolation:
                raise ValueError(f"Missing required field")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")

    return new_service

def register_payment(payment_input: RegisterPayment):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO payments (
                        payment_method_id,
                        user_id,
                        booking_id,
                        status_id,
                        price,
                        currency
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING payment_id, created_at;
                    """,
                    (
                        payment_input.payment_method_id,
                        payment_input.user_id,
                        payment_input.booking_id,
                        payment_input.status_id,
                        payment_input.price,
                        payment_input.currency.upper(),
                    ),
                )

                new_payment = cursor.fetchone()

            except psycopg2.errors.NotNullViolation:
                raise ValueError(f"Missing required field")
            except psycopg2.errors.ForeignKeyViolation:
                raise ValueError(f"Invalid reference (fk)")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")
            
    return new_payment

def update_payment(payment_update: UpdatePayment):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    UPDATE payments
                    SET status_id = %s, created_at = CURRENT_TIMESTAMP
                    WHERE payment_id = %s
                    RETURNING payment_id, user_id, booking_id, payment_method_id, status_id, price, currency, created_at;
                    """,
                    (payment_update.status_id, payment_update.payment_id)
                )

                updated = cursor.fetchone()

            except psycopg2.errors.ForeignKeyViolation:
                raise ValueError(f"Invalid reference (fk)")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")
    return updated

def add_favorite(favorite_input: UserFavoriteInput):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            try:
                cursor.execute(
                    """
                    INSERT INTO user_favorites (user_id, business_id)
                    VALUES (%s, %s)
                    RETURNING favorite_id;
                    """,
                    (favorite_input.user_id, favorite_input.business_id)
                )
                new_fav = cursor.fetchone()

            except psycopg2.errors.UniqueViolation:
                raise ValueError(f"Duplicate or constraint violation")
            except psycopg2.errors.NotNullViolation:
                raise ValueError(f"Missing required field")
            except psycopg2.Error:
                raise RuntimeError(f"Database error")
    return new_fav

def get_user_favorites(user_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT user_favorites.business_id, businesses.business_name
                FROM user_favorites
                JOIN businesses ON user_favorites.business_id = businesses.business_id
                WHERE user_favorites.user_id = %s
                """,
                (user_id,)
            )
            favorites = cursor.fetchall()

    return favorites

def remove_favorite(favorite_input: UserFavoriteInput):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                DELETE FROM user_favorites
                WHERE user_id = %s AND business_id = %s
                RETURNING favorite_id;
                """,
                (favorite_input.user_id, favorite_input.business_id)
            )
            deleted = cursor.fetchone()

            if not deleted:
                raise ValueError(f"Favorite not found or already removed")

    return deleted

def delete_booking(booking_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:

            cursor.execute(
                """
                DELETE FROM payments
                WHERE booking_id = %s;
                """,
                (booking_id,)
            )

            cursor.execute(
                """
                DELETE FROM bookings
                WHERE booking_id = %s
                RETURNING booking_id;
                """,
                (booking_id,)
            )
            deleted_booking = cursor.fetchone()

            if not deleted_booking:
                raise ValueError(f"Booking with booking ID: {booking_id} not found")

    return {"Deleted booking with ID": deleted_booking["booking_id"]}

def login(email: str):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s;",
                (email,)
            )
            user = cursor.fetchone()

        if not user:
            raise ValueError(f"No user found with email: {email}")
    return user

def get_my_bookings(user_id: int):
    con = get_connection()
    with con:
        with con.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(
                """
                SELECT
                    bookings.booking_id,
                    bookings.start_time,
                    bookings.end_time,
                    staff.first_name,
                    staff.last_name,
                    services.service_name,
                    businesses.business_name
                FROM bookings
                JOIN staff ON bookings.staff_id = staff.staff_id
                JOIN services ON bookings.service_id = services.service_id
                JOIN businesses ON staff.business_id = businesses.business_id
                WHERE bookings.user_id = %s
                ORDER BY bookings.start_time;
                """,
                (user_id,)
            )

            bookings = cursor.fetchall()

    return bookings