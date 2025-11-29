# main.py
from dotenv import load_dotenv
load_dotenv()

from invoice_generator import generate_invoice_pdf
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import FileResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import models, schemas, crud, auth
from database import get_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

app = FastAPI(title="Made-to-Order Rubber Spares")

# Scheduler for background tasks
scheduler = AsyncIOScheduler()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] if you want to restrict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- JWT settings ---
SECRET_KEY = os.getenv("SECRET_KEY", "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6A7B8C9D0E1F2")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# --- Utility functions ---
def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def admin_required(user: models.User = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user

# ------------------------------
# --- User registration -------
# ------------------------------
@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user.name, user.email, user.phone, user.password)

# ------------------------------
# --- Login (token) ------------
# ------------------------------
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

# ------------------------------
# --- Customer order ----------
# ------------------------------
@app.post("/orders")
def place_order(order: schemas.OrderCreate, current_user: models.User = Depends(get_current_user), db = Depends(get_db)):
    return crud.create_order(db, current_user.id, order.product, order.quantity)

# ------------------------------
# --- Get all orders (Admin) ---
# ------------------------------
@app.get("/orders", response_model=list[schemas.OrderOut])
def list_orders(db = Depends(get_db), user: models.User = Depends(admin_required)):
    orders = crud.get_orders(db)
    # Add user_name and user_phone to each order
    for order in orders:
        order.user_name = order.user.name if order.user else ""
        order.user_phone = str(order.user.phone) if order.user and order.user.phone else ""
    return orders

# ------------------------------
# --- Get orders for a user ----
# ------------------------------
@app.get("/orders/{user_id}", response_model=list[schemas.OrderOut])
def customer_orders(user_id: str, current_user: models.User = Depends(get_current_user), db = Depends(get_db)):
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_orders_by_user(db, user_id)

# ------------------------------
# --- Update order status (Admin)
# ------------------------------
@app.put("/orders/{order_id}/status")
def update_status(order_id: str, status_update: dict, db = Depends(get_db), user: models.User = Depends(admin_required)):
    status = status_update.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
    order = crud.update_order_status(db, order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ------------------------------
# --- Update expected delivery date (Admin)
# ------------------------------
@app.put("/orders/{order_id}/expected-delivery")
def update_expected_delivery(order_id: str, date_update: dict, db = Depends(get_db), user: models.User = Depends(admin_required)):
    expected_date = date_update.get("expected_delivery_date")
    if not expected_date:
        raise HTTPException(status_code=400, detail="Expected delivery date is required")
    order = crud.update_expected_delivery_date(db, order_id, expected_date)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# ------------------------------
# --- Delete order (Admin)
# ------------------------------
@app.delete("/orders/{order_id}")
def delete_order(order_id: str, db = Depends(get_db), user: models.User = Depends(admin_required)):
    success = crud.delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

# ------------------------------
# --- Create admin user (Admin only)
# ------------------------------
@app.post("/create_admin", response_model=schemas.UserOut)
def create_admin(user: schemas.UserCreate, db = Depends(get_db), current_user: models.User = Depends(admin_required)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_admin_user(db, user.name, user.email, user.password)

# ------------------------------
# --- Check for delays (Admin) ---
# ------------------------------
@app.post("/orders/check-delays")
def check_delays(db = Depends(get_db), user: models.User = Depends(admin_required)):
    crud.check_and_notify_delays(db)
    return {"message": "Delay check completed"}

# ------------------------------
# --- Raw Materials Management ---
# ------------------------------
@app.post("/raw-materials", response_model=schemas.RawMaterialOut)
def create_raw_material(raw_material: schemas.RawMaterialCreate, db = Depends(get_db), user: models.User = Depends(admin_required)):
    return crud.create_raw_material(
        db=db,
        order_id=raw_material.order_id,
        batch_no=raw_material.batch_no,
        recipe_no=raw_material.recipe_no,
        raw_material_quantity=raw_material.raw_material_quantity,
        rubber_type=raw_material.rubber_type
    )

@app.get("/raw-materials", response_model=list[schemas.RawMaterialOut])
def get_raw_materials(db = Depends(get_db), user: models.User = Depends(admin_required)):
    return crud.get_raw_materials(db)

@app.put("/raw-materials/{material_id}/consume")
def consume_raw_material(material_id: str, db = Depends(get_db), user: models.User = Depends(admin_required)):
    material = crud.update_raw_material_consumption(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Raw material not found")
    return {"message": "Raw material marked as consumed"}

@app.post("/raw-materials/check-natural-alerts")
def check_natural_alerts(db = Depends(get_db), user: models.User = Depends(admin_required)):
    crud.check_natural_rubber_alerts(db)
    return {"message": "Natural rubber alerts checked"}

# ------------------------------
# --- Invoice Management ---
# ------------------------------
@app.get("/invoices", response_model=list[schemas.InvoiceOut])
def get_invoices(db = Depends(get_db), user: models.User = Depends(admin_required)):
    return crud.get_invoices(db)

@app.get("/invoices/{invoice_id}/pdf")
def get_invoice_pdf(invoice_id: str, db = Depends(get_db), user: models.User = Depends(admin_required)):
    invoice = crud.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Generate PDF
    try:
        pdf_path = generate_invoice_pdf(invoice)
        return FileResponse(pdf_path, media_type='application/pdf', filename=f"invoice_{invoice.invoice_number}.pdf")
    except ImportError:
        # Fallback: Return invoice data as JSON if PDF generation fails
        return {"invoice": invoice, "message": "PDF generation requires reportlab. Install with: pip install reportlab"}

@app.put("/invoices/{invoice_id}/status")
def update_invoice_status(invoice_id: str, status_update: dict, db = Depends(get_db), user: models.User = Depends(admin_required)):
    status = status_update.get("status")
    if not status:
        raise HTTPException(status_code=400, detail="Status is required")
    invoice = crud.update_invoice_status(db, invoice_id, status)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.post("/invoices/gst", response_model=schemas.InvoiceOut)
def create_gst_invoice(invoice_data: schemas.InvoiceCreate, db = Depends(get_db), user: models.User = Depends(admin_required)):
    if not invoice_data.line_items:
        raise HTTPException(status_code=400, detail="At least one line item is required")
    
    line_items = [item.dict() for item in invoice_data.line_items]
    invoice = crud.create_invoice_with_line_items(
        db=db,
        customer_name=invoice_data.customer_name,
        customer_email=invoice_data.customer_email,
        line_items=line_items,
        customer_gstin=invoice_data.customer_gstin,
        customer_address=invoice_data.customer_address,
        delivery_note_no=invoice_data.delivery_note_no,
        buyer_order_no=invoice_data.buyer_order_no,
        dispatch_through=invoice_data.dispatch_through,
        dispatch_doc_no=invoice_data.dispatch_doc_no,
        discount_percent=invoice_data.discount_percent,
        notes=invoice_data.notes,
        order_id=invoice_data.order_id
    )
    return invoice

@app.get("/invoices/{invoice_id}", response_model=schemas.InvoiceOut)
def get_invoice_details(invoice_id: str, db = Depends(get_db), user: models.User = Depends(admin_required)):
    invoice = crud.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice

@app.get("/invoices-list", response_model=list[schemas.InvoiceOut])
def get_all_invoices(db = Depends(get_db), user: models.User = Depends(admin_required)):
    return crud.get_invoices_with_line_items(db)

@app.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: str, db = Depends(get_db), user: models.User = Depends(admin_required)):
    success = crud.delete_invoice(db, invoice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted successfully"}

@app.delete("/raw-materials/{material_id}")
def delete_raw_material(material_id: str, db = Depends(get_db), user: models.User = Depends(admin_required)):
    success = crud.delete_raw_material(db, material_id)
    if not success:
        raise HTTPException(status_code=404, detail="Raw material not found")
    return {"message": "Raw material deleted successfully"}

# ------------------------------
# --- Validate token endpoint ---
# ------------------------------
@app.get("/validate_token")
def validate_token(current_user: models.User = Depends(get_current_user)):
    return {"valid": True, "user": {"id": current_user.id, "email": current_user.email, "role": current_user.role}}

# Start scheduler on app startup
@app.on_event("startup")
async def startup_event():
    db = get_db()
    scheduler.add_job(crud.check_and_notify_delays, CronTrigger(hour=0), args=[db])  # Daily at midnight
    scheduler.add_job(crud.check_natural_rubber_alerts, CronTrigger(hour=6), args=[db])  # Daily at 6 AM
    scheduler.start()

    # Create default admin user if it doesn't exist
    try:
        admin_email = "ddrporders@gmail.com"
        existing_admin = crud.get_user_by_email(db, admin_email)
        if not existing_admin:
            # Create admin user with default password
            admin_user = crud.create_admin_user(db, "Admin", admin_email, "admin123")
            print(f"Created default admin user: {admin_email}")
        else:
            print(f"Admin user already exists: {admin_email}")
    except Exception as e:
        print(f"Error creating admin user: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
