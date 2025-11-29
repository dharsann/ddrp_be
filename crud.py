from models import User, Order, RawMaterial, Invoice, InvoiceLineItem, USERS_COLLECTION, ORDERS_COLLECTION, RAW_MATERIALS_COLLECTION, INVOICES_COLLECTION, INVOICE_LINE_ITEMS_COLLECTION
from database import get_db
from auth import hash_password
from mail import send_order_status_email, send_order_confirmation_email, send_delay_notification_email, send_raw_material_arrival_email, send_natural_rubber_alert_email
from sheets import append_order_to_sheet, append_inventory_to_sheet
from datetime import datetime, timedelta
import random
import string

def create_user(db, name: str, email: str, phone: str, password: str):
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        return None

    user_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "password_hash": hash_password(password),
        "role": "customer"
    }

    doc_ref = db.collection(USERS_COLLECTION).document()
    user_data["id"] = doc_ref.id
    doc_ref.set(user_data)

    user = User.from_dict(user_data)
    return user

def get_user_by_email(db, email: str):
    users_ref = db.collection(USERS_COLLECTION)
    query = users_ref.where("email", "==", email).limit(1)
    docs = query.stream()
    for doc in docs:
        return User.from_dict(doc.to_dict())
    return None

def create_order(db, user_id: str, product: str, quantity: int):
    # Auto-calculate expected delivery date (7 days from order date)
    expected_delivery_date = datetime.utcnow() + timedelta(days=7)
    order_data = {
        "user_id": user_id,
        "product": product,
        "quantity": quantity,
        "status": "Pending",
        "order_date": datetime.utcnow(),
        "expected_delivery_date": expected_delivery_date
    }

    doc_ref = db.collection(ORDERS_COLLECTION).document()
    order_data["id"] = doc_ref.id
    doc_ref.set(order_data)

    order = Order.from_dict(order_data)

    # Send order confirmation email
    user = get_user_by_email(db, None)  # Need to get user by ID, but we have email in token
    # Actually, we need to get user by ID
    user_doc = db.collection(USERS_COLLECTION).document(str(user_id)).get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        user = User.from_dict(user_data)
        recipients = [user.email, "daeiouanantharaman@gmail.com", "ksridevi943@gmail.com", "dharsannanantharaman@gmail.com"]
        try:
            send_order_confirmation_email(recipients, order.id, product, quantity)
        except Exception as e:
            print(f"Failed to send order confirmation email for order {order.id}: {e}")
        # Append to Google Sheets
        try:
            append_order_to_sheet(order.id, user.name, user.phone, product, quantity, order.order_date)
        except Exception as e:
            print(f"Failed to append order {order.id} to Google Sheets: {e}")
    return order

def get_orders(db):
    orders = []
    docs = db.collection(ORDERS_COLLECTION).stream()
    for doc in docs:
        order_data = doc.to_dict()
        order = Order.from_dict(order_data)
        # Get user data
        user_doc = db.collection(USERS_COLLECTION).document(str(order.user_id)).get()
        if user_doc.exists:
            order.user = User.from_dict(user_doc.to_dict())
        orders.append(order)
    return orders

def get_orders_by_user(db, user_id: str):
    orders = []
    docs = db.collection(ORDERS_COLLECTION).where("user_id", "==", user_id).stream()
    for doc in docs:
        order_data = doc.to_dict()
        order = Order.from_dict(order_data)
        orders.append(order)
    return orders

def update_order_status(db, order_id: str, status: str):
    doc_ref = db.collection(ORDERS_COLLECTION).document(str(order_id))
    doc = doc_ref.get()
    if doc.exists:
        order_data = doc.to_dict()
        if order_data.get("status") != status:  # Only update and send email if status changed
            order_data["status"] = status
            doc_ref.update({"status": status})

            # Get user email
            user_doc = db.collection(USERS_COLLECTION).document(str(order_data["user_id"])).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                recipients = [user_data["email"], "daeiouanantharaman@gmail.com", "ksridevi943@gmail.com", "dharsannanantharaman@gmail.com"]
                try:
                    send_order_status_email(recipients, order_id, status)
                except Exception as e:
                    print(f"Failed to send email for order {order_id}: {e}")
                # Check for delay if status is not Delivered and expected_delivery_date is set
                expected_date = order_data.get("expected_delivery_date")
                if status != "Delivered" and expected_date:
                    # Convert expected_date to datetime if it's a string or ensure timezone compatibility
                    if isinstance(expected_date, str):
                        try:
                            expected_date = datetime.fromisoformat(expected_date.replace('Z', '+00:00'))
                        except:
                            expected_date = datetime.strptime(expected_date, '%Y-%m-%d %H:%M:%S')
                    
                    # Make datetime comparison timezone-aware or naive consistently
                    current_time = datetime.utcnow()
                    if hasattr(expected_date, 'tzinfo') and expected_date.tzinfo is not None:
                        # expected_date is timezone-aware, make current_time timezone-aware too
                        from datetime import timezone
                        current_time = current_time.replace(tzinfo=timezone.utc)
                    elif hasattr(expected_date, 'tzinfo'):
                        # expected_date is timezone-naive, keep current_time timezone-naive
                        pass
                    
                    if current_time > expected_date:
                        try:
                            send_delay_notification_email(recipients, order_id, expected_date, status)
                        except Exception as e:
                            print(f"Failed to send delay notification for order {order_id}: {e}")
        order = Order.from_dict(order_data)
        return order
    return None

def delete_order(db, order_id: str):
    doc_ref = db.collection(ORDERS_COLLECTION).document(str(order_id))
    if doc_ref.get().exists:
        doc_ref.delete()
        return True
    return False

def create_admin_user(db, name: str, email: str, password: str):
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        return None

    user_data = {
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "role": "admin"
    }

    doc_ref = db.collection(USERS_COLLECTION).document()
    user_data["id"] = doc_ref.id
    doc_ref.set(user_data)

    user = User.from_dict(user_data)
    return user

def check_and_notify_delays(db):
    docs = db.collection(ORDERS_COLLECTION).where("expected_delivery_date", "<", datetime.utcnow()).where("status", "!=", "Delivered").stream()
    for doc in docs:
        order_data = doc.to_dict()
        expected_date = order_data.get("expected_delivery_date")
        if expected_date:
            user_doc = db.collection(USERS_COLLECTION).document(str(order_data["user_id"])).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                recipients = [user_data["email"], "daeiouanantharaman@gmail.com", "ksridevi943@gmail.com", "dharsannanantharaman@gmail.com"]
                try:
                    send_delay_notification_email(recipients, order_data["id"], expected_date, order_data["status"])
                except Exception as e:
                    print(f"Failed to send delay notification for order {order_data['id']}: {e}")

def update_expected_delivery_date(db, order_id: str, expected_date: str):
    from datetime import datetime
    doc_ref = db.collection(ORDERS_COLLECTION).document(str(order_id))
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"expected_delivery_date": datetime.fromisoformat(expected_date.replace('Z', '+00:00'))})
        updated_data = doc.to_dict()
        updated_data["expected_delivery_date"] = datetime.fromisoformat(expected_date.replace('Z', '+00:00'))
        return Order.from_dict(updated_data)
    return None

def create_raw_material(db, order_id: str, batch_no: str, recipe_no: str, raw_material_quantity: float, rubber_type: str):
    # Set consumption deadline for natural rubber (4-5 days from arrival)
    consumption_deadline = None
    if rubber_type.lower() == "natural":
        consumption_deadline = datetime.utcnow() + timedelta(days=5)  # Using 5 days as requested

    raw_material_data = {
        "order_id": order_id,
        "batch_no": batch_no,
        "recipe_no": recipe_no,
        "raw_material_quantity": raw_material_quantity,
        "rubber_type": rubber_type,
        "arrival_date": datetime.utcnow(),
        "consumption_deadline": consumption_deadline
    }

    doc_ref = db.collection(RAW_MATERIALS_COLLECTION).document()
    raw_material_data["id"] = doc_ref.id
    doc_ref.set(raw_material_data)

    raw_material = RawMaterial.from_dict(raw_material_data)

    # Send arrival email only once per order
    order_doc = db.collection(ORDERS_COLLECTION).document(str(order_id)).get()
    if order_doc.exists:
        # Check if this is the first raw material for this order
        existing_materials = db.collection(RAW_MATERIALS_COLLECTION).where("order_id", "==", order_id).get()
        if len(existing_materials) == 1:  # Only send email for the first material
            user_doc = db.collection(USERS_COLLECTION).document(str(order_doc.to_dict()["user_id"])).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                recipients = [user_data["email"], "daeiouanantharaman@gmail.com", "ksridevi943@gmail.com", "dharsannanantharaman@gmail.com"]
                try:
                    send_raw_material_arrival_email(recipients, order_id, bill_no, batch_no, raw_material_quantity)
                except Exception as e:
                    print(f"Failed to send raw material arrival email for order {order_id}: {e}")

        # Append to Google Sheets
        try:
            append_inventory_to_sheet(order_id, batch_no, recipe_no, raw_material_quantity, rubber_type, raw_material.arrival_date)
        except Exception as e:
            print(f"Failed to append inventory {raw_material.id} to Google Sheets: {e}")

    return raw_material

def get_raw_materials(db):
    materials = []
    docs = db.collection(RAW_MATERIALS_COLLECTION).stream()
    for doc in docs:
        material_data = doc.to_dict()
        material = RawMaterial.from_dict(material_data)
        materials.append(material)
    return [material.to_dict() for material in materials]

def update_raw_material_consumption(db, raw_material_id: str):
    doc_ref = db.collection(RAW_MATERIALS_COLLECTION).document(str(raw_material_id))
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"consumption_date": datetime.utcnow()})
        updated_data = doc.to_dict()
        updated_data["consumption_date"] = datetime.utcnow()
        return RawMaterial.from_dict(updated_data)
    return None

def check_natural_rubber_alerts(db):
    # Get all natural rubber materials without consumption date
    docs = db.collection(RAW_MATERIALS_COLLECTION).where("rubber_type", "==", "Natural").where("consumption_date", "==", None).stream()

    current_time = datetime.utcnow()
    
    for doc in docs:
        material_data = doc.to_dict()
        consumption_deadline = material_data.get("consumption_deadline")
        if consumption_deadline:
            # Handle timezone-aware/naive datetime comparison
            if isinstance(consumption_deadline, str):
                try:
                    consumption_deadline = datetime.fromisoformat(consumption_deadline.replace('Z', '+00:00'))
                except:
                    consumption_deadline = datetime.strptime(consumption_deadline, '%Y-%m-%d %H:%M:%S')
            
            # Make datetime comparison timezone-aware or naive consistently
            comparison_time = current_time
            if hasattr(consumption_deadline, 'tzinfo') and consumption_deadline.tzinfo is not None:
                # consumption_deadline is timezone-aware, make comparison_time timezone-aware too
                from datetime import timezone
                comparison_time = current_time.replace(tzinfo=timezone.utc)
            
            # Check if deadline has passed
            if comparison_time > consumption_deadline:
                recipients = ["daeiouanantharaman@gmail.com", "ksridevi943@gmail.com", "dharsannanantharaman@gmail.com"]
                try:
                    send_natural_rubber_alert_email(recipients, material_data["order_id"], consumption_deadline)
                except Exception as e:
                    print(f"Failed to send natural rubber alert for material {material_data['id']}: {e}")

def delete_raw_material(db, material_id: str):
    doc_ref = db.collection(RAW_MATERIALS_COLLECTION).document(str(material_id))
    if doc_ref.get().exists:
        doc_ref.delete()
        return True
    return False

def delete_invoice(db, invoice_id: str):
    # First, delete all line items for this invoice
    line_items_docs = db.collection(INVOICE_LINE_ITEMS_COLLECTION).where("invoice_id", "==", invoice_id).stream()
    for doc in line_items_docs:
        doc.reference.delete()
    
    # Then delete the invoice itself
    doc_ref = db.collection(INVOICES_COLLECTION).document(str(invoice_id))
    if doc_ref.get().exists:
        doc_ref.delete()
        return True
    return False

def generate_invoice_number():
    """Generate a unique invoice number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"INV-{timestamp}-{random_suffix}"

def create_invoice(db, order_id: str, unit_price: float, tax_percentage: float = 0.0, discount_percentage: float = 0.0):
    # Get order details
    order_doc = db.collection(ORDERS_COLLECTION).document(str(order_id)).get()
    if not order_doc.exists:
        return None
    order_data = order_doc.to_dict()

    user_doc = db.collection(USERS_COLLECTION).document(str(order_data["user_id"])).get()
    if not user_doc.exists:
        return None
    user_data = user_doc.to_dict()

    # Calculate amounts
    subtotal = order_data["quantity"] * unit_price
    tax_amount = subtotal * (tax_percentage / 100)
    discount_amount = subtotal * (discount_percentage / 100)
    final_amount = subtotal + tax_amount - discount_amount

    # Due date (30 days from issue)
    due_date = datetime.utcnow() + timedelta(days=30)

    # Generate invoice number
    invoice_number = generate_invoice_number()

    invoice_data = {
        "order_id": order_id,
        "invoice_number": invoice_number,
        "customer_name": user_data["name"],
        "customer_email": user_data["email"],
        "product": order_data["product"],
        "quantity": order_data["quantity"],
        "unit_price": unit_price,
        "total_amount": subtotal,
        "tax_amount": tax_amount,
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "status": "Pending",
        "issue_date": datetime.utcnow(),
        "due_date": due_date
    }

    doc_ref = db.collection(INVOICES_COLLECTION).document()
    invoice_data["id"] = doc_ref.id
    doc_ref.set(invoice_data)

    invoice = Invoice.from_dict(invoice_data)
    return invoice

def get_invoices(db):
    invoices = []
    docs = db.collection(INVOICES_COLLECTION).stream()
    for doc in docs:
        invoice_data = doc.to_dict()
        invoice = Invoice.from_dict(invoice_data)
        invoices.append(invoice)
    return invoices

def get_invoice_by_order(db, order_id: str):
    docs = db.collection(INVOICES_COLLECTION).where("order_id", "==", order_id).limit(1).stream()
    for doc in docs:
        return Invoice.from_dict(doc.to_dict())
    return None

def update_invoice_status(db, invoice_id: str, status: str):
    doc_ref = db.collection(INVOICES_COLLECTION).document(str(invoice_id))
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update({"status": status})
        updated_data = doc.to_dict()
        updated_data["status"] = status
        return Invoice.from_dict(updated_data)
    return None

def create_invoice_with_line_items(db, customer_name: str, customer_email: str, line_items: list,
                                    customer_gstin: str = None, customer_address: str = None,
                                    delivery_note_no: str = None, buyer_order_no: str = None,
                                    dispatch_through: str = None, dispatch_doc_no: str = None,
                                    discount_percent: float = 0.0, notes: str = None, order_id: str = None):
    subtotal = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    total_igst = 0.0

    invoice_line_items_data = []

    for item in line_items:
        amount = item.get("quantity") * item.get("rate")
        cgst_amount = amount * (item.get("cgst_percent", 0.0) / 100)
        sgst_amount = amount * (item.get("sgst_percent", 0.0) / 100)
        igst_amount = amount * (item.get("igst_percent", 0.0) / 100)
        total_with_tax = amount + cgst_amount + sgst_amount + igst_amount

        subtotal += amount
        total_cgst += cgst_amount
        total_sgst += sgst_amount
        total_igst += igst_amount

        invoice_line_items_data.append({
            "hsn_code": item.get("hsn_code"),
            "description": item.get("description"),
            "quantity": item.get("quantity"),
            "rate": item.get("rate"),
            "amount": amount,
            "cgst_percent": item.get("cgst_percent", 0.0),
            "sgst_percent": item.get("sgst_percent", 0.0),
            "igst_percent": item.get("igst_percent", 0.0),
            "cgst_amount": cgst_amount,
            "sgst_amount": sgst_amount,
            "igst_amount": igst_amount,
            "total_with_tax": total_with_tax
        })

    total_tax = total_cgst + total_sgst + total_igst
    discount_amount = subtotal * (discount_percent / 100)
    final_amount = subtotal + total_tax - discount_amount

    due_date = datetime.utcnow() + timedelta(days=30)
    invoice_number = generate_invoice_number()

    invoice_data = {
        "order_id": order_id,
        "invoice_number": invoice_number,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "customer_gstin": customer_gstin,
        "customer_address": customer_address,
        "delivery_note_no": delivery_note_no,
        "buyer_order_no": buyer_order_no,
        "dispatch_through": dispatch_through,
        "dispatch_doc_no": dispatch_doc_no,
        "subtotal": subtotal,
        "total_cgst": total_cgst,
        "total_sgst": total_sgst,
        "total_igst": total_igst,
        "total_tax": total_tax,
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "status": "Pending",
        "issue_date": datetime.utcnow(),
        "due_date": due_date,
        "notes": notes
    }

    doc_ref = db.collection(INVOICES_COLLECTION).document()
    invoice_data["id"] = doc_ref.id
    doc_ref.set(invoice_data)

    invoice = Invoice.from_dict(invoice_data)

    for line_item_data in invoice_line_items_data:
        line_item_data["invoice_id"] = invoice.id
        line_item_ref = db.collection(INVOICE_LINE_ITEMS_COLLECTION).document()
        line_item_data["id"] = line_item_ref.id
        line_item_ref.set(line_item_data)
        line_item = InvoiceLineItem.from_dict(line_item_data)
        invoice.line_items.append(line_item)

    return invoice

def get_invoice_by_id(db, invoice_id: str):
    doc = db.collection(INVOICES_COLLECTION).document(str(invoice_id)).get()
    if doc.exists:
        invoice_data = doc.to_dict()
        invoice = Invoice.from_dict(invoice_data)
        
        line_items_docs = db.collection(INVOICE_LINE_ITEMS_COLLECTION).where("invoice_id", "==", invoice_id).stream()
        for line_item_doc in line_items_docs:
            line_item_data = line_item_doc.to_dict()
            line_item = InvoiceLineItem.from_dict(line_item_data)
            invoice.line_items.append(line_item)
        
        return invoice
    return None

def get_invoices_with_line_items(db):
    invoices = []
    docs = db.collection(INVOICES_COLLECTION).stream()
    for doc in docs:
        invoice_data = doc.to_dict()
        invoice = Invoice.from_dict(invoice_data)
        
        line_items_docs = db.collection(INVOICE_LINE_ITEMS_COLLECTION).where("invoice_id", "==", invoice.id).stream()
        for line_item_doc in line_items_docs:
            line_item_data = line_item_doc.to_dict()
            line_item = InvoiceLineItem.from_dict(line_item_data)
            invoice.line_items.append(line_item)
        
        invoices.append(invoice)
    return invoices
