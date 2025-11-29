from datetime import datetime
from database import get_db

# Firebase collections
USERS_COLLECTION = "users"
ORDERS_COLLECTION = "orders"
RAW_MATERIALS_COLLECTION = "raw_materials"
INVOICES_COLLECTION = "invoices"
INVOICE_LINE_ITEMS_COLLECTION = "invoice_line_items"

class User:
    def __init__(self, id=None, name=None, email=None, phone=None, password_hash=None, role="customer"):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.role = role

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "password_hash": self.password_hash,
            "role": self.role
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            password_hash=data.get("password_hash"),
            role=data.get("role", "customer")
        )

class Order:
    def __init__(self, id=None, user_id=None, product=None, quantity=None, status="Pending",
                 order_date=None, expected_delivery_date=None, user=None):
        self.id = id
        self.user_id = user_id
        self.product = product
        self.quantity = quantity
        self.status = status
        self.order_date = order_date or datetime.utcnow()
        self.expected_delivery_date = expected_delivery_date
        self.user = user

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product": self.product,
            "quantity": self.quantity,
            "status": self.status,
            "order_date": self.order_date,
            "expected_delivery_date": self.expected_delivery_date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            product=data.get("product"),
            quantity=data.get("quantity"),
            status=data.get("status", "Pending"),
            order_date=data.get("order_date"),
            expected_delivery_date=data.get("expected_delivery_date")
        )

class RawMaterial:
    def __init__(self, id=None, order_id=None, batch_no=None, recipe_no=None,
                 raw_material_quantity=None, rubber_type="Natural", arrival_date=None,
                 consumption_date=None, consumption_deadline=None):
        self.id = id
        self.order_id = order_id
        self.batch_no = batch_no
        self.recipe_no = recipe_no
        self.raw_material_quantity = raw_material_quantity
        self.rubber_type = rubber_type
        self.arrival_date = arrival_date or datetime.utcnow()
        self.consumption_date = consumption_date
        self.consumption_deadline = consumption_deadline

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "batch_no": self.batch_no,
            "recipe_no": self.recipe_no,
            "raw_material_quantity": self.raw_material_quantity,
            "rubber_type": self.rubber_type,
            "arrival_date": self.arrival_date,
            "consumption_date": self.consumption_date,
            "consumption_deadline": self.consumption_deadline
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id"),
            batch_no=data.get("batch_no"),
            recipe_no=data.get("recipe_no"),
            raw_material_quantity=data.get("raw_material_quantity"),
            rubber_type=data.get("rubber_type", "Natural"),
            arrival_date=data.get("arrival_date"),
            consumption_date=data.get("consumption_date"),
            consumption_deadline=data.get("consumption_deadline")
        )

class Invoice:
    def __init__(self, id=None, order_id=None, invoice_number=None, customer_name=None,
                 customer_email=None, customer_gstin=None, customer_address=None,
                 delivery_note_no=None, buyer_order_no=None, dispatch_through=None,
                 dispatch_doc_no=None, subtotal=0.0, total_cgst=0.0, total_sgst=0.0,
                 total_igst=0.0, total_tax=0.0, discount_amount=0.0, final_amount=None,
                 status="Pending", issue_date=None, due_date=None, notes=None):
        self.id = id
        self.order_id = order_id
        self.invoice_number = invoice_number
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.customer_gstin = customer_gstin
        self.customer_address = customer_address
        self.delivery_note_no = delivery_note_no
        self.buyer_order_no = buyer_order_no
        self.dispatch_through = dispatch_through
        self.dispatch_doc_no = dispatch_doc_no
        self.subtotal = subtotal
        self.total_cgst = total_cgst
        self.total_sgst = total_sgst
        self.total_igst = total_igst
        self.total_tax = total_tax
        self.discount_amount = discount_amount
        self.final_amount = final_amount
        self.status = status
        self.issue_date = issue_date or datetime.utcnow()
        self.due_date = due_date
        self.notes = notes
        self.line_items = []

    def to_dict(self):
        return {
            "id": self.id,
            "order_id": self.order_id,
            "invoice_number": self.invoice_number,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "customer_gstin": self.customer_gstin,
            "customer_address": self.customer_address,
            "delivery_note_no": self.delivery_note_no,
            "buyer_order_no": self.buyer_order_no,
            "dispatch_through": self.dispatch_through,
            "dispatch_doc_no": self.dispatch_doc_no,
            "subtotal": self.subtotal,
            "total_cgst": self.total_cgst,
            "total_sgst": self.total_sgst,
            "total_igst": self.total_igst,
            "total_tax": self.total_tax,
            "discount_amount": self.discount_amount,
            "final_amount": self.final_amount,
            "status": self.status,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            order_id=data.get("order_id"),
            invoice_number=data.get("invoice_number"),
            customer_name=data.get("customer_name"),
            customer_email=data.get("customer_email"),
            customer_gstin=data.get("customer_gstin"),
            customer_address=data.get("customer_address"),
            delivery_note_no=data.get("delivery_note_no"),
            buyer_order_no=data.get("buyer_order_no"),
            dispatch_through=data.get("dispatch_through"),
            dispatch_doc_no=data.get("dispatch_doc_no"),
            subtotal=data.get("subtotal", 0.0),
            total_cgst=data.get("total_cgst", 0.0),
            total_sgst=data.get("total_sgst", 0.0),
            total_igst=data.get("total_igst", 0.0),
            total_tax=data.get("total_tax", 0.0),
            discount_amount=data.get("discount_amount", 0.0),
            final_amount=data.get("final_amount"),
            status=data.get("status", "Pending"),
            issue_date=data.get("issue_date"),
            due_date=data.get("due_date"),
            notes=data.get("notes")
        )

class InvoiceLineItem:
    def __init__(self, id=None, invoice_id=None, hsn_code=None, description=None,
                 quantity=None, rate=None, amount=None, cgst_percent=0.0, sgst_percent=0.0,
                 igst_percent=0.0, cgst_amount=0.0, sgst_amount=0.0, igst_amount=0.0,
                 total_with_tax=None):
        self.id = id
        self.invoice_id = invoice_id
        self.hsn_code = hsn_code
        self.description = description
        self.quantity = quantity
        self.rate = rate
        self.amount = amount
        self.cgst_percent = cgst_percent
        self.sgst_percent = sgst_percent
        self.igst_percent = igst_percent
        self.cgst_amount = cgst_amount
        self.sgst_amount = sgst_amount
        self.igst_amount = igst_amount
        self.total_with_tax = total_with_tax

    def to_dict(self):
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "hsn_code": self.hsn_code,
            "description": self.description,
            "quantity": self.quantity,
            "rate": self.rate,
            "amount": self.amount,
            "cgst_percent": self.cgst_percent,
            "sgst_percent": self.sgst_percent,
            "igst_percent": self.igst_percent,
            "cgst_amount": self.cgst_amount,
            "sgst_amount": self.sgst_amount,
            "igst_amount": self.igst_amount,
            "total_with_tax": self.total_with_tax
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            invoice_id=data.get("invoice_id"),
            hsn_code=data.get("hsn_code"),
            description=data.get("description"),
            quantity=data.get("quantity"),
            rate=data.get("rate"),
            amount=data.get("amount"),
            cgst_percent=data.get("cgst_percent", 0.0),
            sgst_percent=data.get("sgst_percent", 0.0),
            igst_percent=data.get("igst_percent", 0.0),
            cgst_amount=data.get("cgst_amount", 0.0),
            sgst_amount=data.get("sgst_amount", 0.0),
            igst_amount=data.get("igst_amount", 0.0),
            total_with_tax=data.get("total_with_tax")
        )
