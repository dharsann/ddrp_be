from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    password: str

class UserOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    role: str
    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    product: str
    quantity: int

class OrderOut(BaseModel):
    id: str
    product: str
    quantity: int
    status: str
    order_date: datetime
    expected_delivery_date: Optional[datetime] = None
    user_name: str = ""
    user_phone: str = ""
    class Config:
        orm_mode = True

class RawMaterialCreate(BaseModel):
    order_id: str
    batch_no: str
    recipe_no: str
    raw_material_quantity: float
    rubber_type: str

class RawMaterialOut(BaseModel):
    id: str
    order_id: str
    batch_no: str
    recipe_no: str
    raw_material_quantity: float
    rubber_type: str
    arrival_date: datetime
    consumption_date: Optional[datetime] = None
    consumption_deadline: Optional[datetime] = None
    class Config:
        orm_mode = True
        from_attributes = True

class InvoiceLineItemCreate(BaseModel):
    hsn_code: str
    description: str
    quantity: int
    rate: float
    cgst_percent: float = 0.0
    sgst_percent: float = 0.0
    igst_percent: float = 0.0

class InvoiceLineItemOut(BaseModel):
    id: str
    invoice_id: str
    hsn_code: str
    description: str
    quantity: int
    rate: float
    amount: float
    cgst_percent: float
    sgst_percent: float
    igst_percent: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    total_with_tax: float
    class Config:
        orm_mode = True
        from_attributes = True

class InvoiceCreate(BaseModel):
    order_id: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_gstin: Optional[str] = None
    customer_address: Optional[str] = None
    delivery_note_no: Optional[str] = None
    buyer_order_no: Optional[str] = None
    dispatch_through: Optional[str] = None
    dispatch_doc_no: Optional[str] = None
    line_items: list[InvoiceLineItemCreate]
    discount_percent: float = 0.0
    notes: Optional[str] = None

class InvoiceOut(BaseModel):
    id: str
    order_id: Optional[str] = None
    invoice_number: str
    customer_name: str
    customer_email: str
    customer_gstin: Optional[str] = None
    customer_address: Optional[str] = None
    delivery_note_no: Optional[str] = None
    buyer_order_no: Optional[str] = None
    dispatch_through: Optional[str] = None
    dispatch_doc_no: Optional[str] = None
    line_items: list[InvoiceLineItemOut] = []
    subtotal: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    total_tax: float
    discount_amount: float
    final_amount: float
    status: str
    issue_date: datetime
    due_date: datetime
    notes: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True
