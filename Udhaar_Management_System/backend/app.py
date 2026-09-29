import sqlite3
import os
from datetime import datetime, date
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
import io
import csv

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "udhaar.db")

app = FastAPI(title="Udhaar Management System API - Nav Durga Super Market")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        admin_id TEXT PRIMARY KEY,
        admin_name TEXT NOT NULL,
        role TEXT DEFAULT 'Admin',
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

    try:
        cursor.execute("ALTER TABLE admins ADD COLUMN role TEXT DEFAULT 'Admin';")
    except Exception:
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        phone_number TEXT UNIQUE NOT NULL,
        alternate_number TEXT,
        email TEXT,
        address TEXT,
        created_date TEXT NOT NULL,
        updated_date TEXT NOT NULL,
        time TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credit_transactions (
        transaction_id TEXT PRIMARY KEY,
        customer_id TEXT NOT NULL,
        transaction_date TEXT NOT NULL,
        due_date TEXT NOT NULL,
        total_amount REAL NOT NULL,
        payment_status TEXT NOT NULL,
        note TEXT,
        created_date TEXT NOT NULL,
        updated_date TEXT NOT NULL,
        time TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credit_items (
        item_id TEXT PRIMARY KEY,
        transaction_id TEXT NOT NULL,
        item_name TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit_price REAL NOT NULL,
        subtotal REAL NOT NULL,
        credited_at TEXT NOT NULL,
        FOREIGN KEY (transaction_id) REFERENCES credit_transactions(transaction_id) ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        transaction_id TEXT NOT NULL,
        customer_id TEXT NOT NULL,
        payment_amount REAL NOT NULL,
        payment_date TEXT NOT NULL,
        payment_method TEXT NOT NULL,
        reference_id TEXT,
        FOREIGN KEY (transaction_id) REFERENCES credit_transactions(transaction_id) ON DELETE CASCADE,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
    );
    """)

    conn.commit()
    conn.close()

@app.on_event("startup")
def on_startup():
    init_db()

# Pydantic Schemas
class AdminRegisterRequest(BaseModel):
    admin_name: str
    role: Optional[str] = "Admin"
    username: str
    password: str
    confirm_password: str

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class CustomerCreateRequest(BaseModel):
    customer_name: str
    phone_number: str
    alternate_number: Optional[str] = ""
    email: Optional[str] = ""
    address: Optional[str] = ""
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

class CustomerUpdateRequest(BaseModel):
    customer_name: str
    phone_number: str
    alternate_number: Optional[str] = ""
    email: Optional[str] = ""
    address: Optional[str] = ""
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

class TransactionCreateRequest(BaseModel):
    customer_id: str
    transaction_date: str
    due_date: str
    total_amount: float
    note: Optional[str] = ""
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

class TransactionUpdateRequest(BaseModel):
    customer_id: str
    transaction_date: str
    due_date: str
    total_amount: float
    note: Optional[str] = ""
    created_date: Optional[str] = None
    updated_date: Optional[str] = None

class CreditItemCreateRequest(BaseModel):
    transaction_id: str
    item_name: str
    quantity: float
    unit_price: float

class CreditItemUpdateRequest(BaseModel):
    transaction_id: str
    item_name: str
    quantity: float
    unit_price: float

class PaymentCreateRequest(BaseModel):
    transaction_id: str
    customer_id: Optional[str] = ""
    payment_amount: float
    payment_date: str
    payment_method: str
    reference_id: Optional[str] = ""

class PaymentUpdateRequest(BaseModel):
    payment_amount: float
    payment_date: str
    payment_method: str
    reference_id: Optional[str] = ""

# Helpers for Auto IDs
def get_next_id(prefix: str, table_name: str, id_column: str) -> str:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {id_column} FROM {table_name} ORDER BY {id_column} DESC")
    rows = cursor.fetchall()
    conn.close()
    
    max_num = 0
    for r in rows:
        val = r[0]
        if val and val.startswith(prefix):
            try:
                num = int(val[len(prefix):])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"{prefix}{max_num + 1:03d}"

def compute_transaction_status(total_amount: float, total_paid: float, due_date_str: str) -> str:
    if total_paid >= total_amount:
        return "Paid"
    try:
        due_d = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except Exception:
        due_d = date.today()
    if date.today() > due_d:
        return "Overdue"
    return "Pending"

# AUTH ENDPOINTS
@app.post("/api/auth/register")
def register_admin(req: AdminRegisterRequest):
    if not req.admin_name.strip() or not req.username.strip() or not req.password:
        raise HTTPException(status_code=400, detail="All fields are required")
    if req.password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id FROM admins WHERE username = ?", (req.username.strip(),))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    admin_id = get_next_id("ADM", "admins", "admin_id")
    role_val = req.role.strip() if req.role and req.role.strip() else "Admin"
    cursor.execute(
        "INSERT INTO admins (admin_id, admin_name, role, username, password) VALUES (?, ?, ?, ?, ?)",
        (admin_id, req.admin_name.strip(), role_val, req.username.strip(), req.password)
    )
    conn.commit()
    conn.close()
    return {"message": "Admin registered successfully", "admin_id": admin_id}

@app.post("/api/auth/login")
def login_admin(req: AdminLoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, admin_name, username FROM admins WHERE username = ? AND password = ?", (req.username.strip(), req.password))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"message": "Login successful", "admin": dict(row)}

# CUSTOMERS ENDPOINTS
@app.get("/api/customers/next-id")
def get_customer_next_id():
    return {"next_id": get_next_id("CUST", "customers", "customer_id")}

@app.get("/api/customers")
def get_customers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers ORDER BY customer_id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    # Calculate performance for view
    result = []
    for c in rows:
        perf = calculate_customer_perf(c["customer_id"])
        c["performance_status"] = perf["status"]
        c["performance_percentage"] = perf["percentage"]
        result.append(c)
    return result

@app.post("/api/customers")
def create_customer(req: CustomerCreateRequest):
    if not req.customer_name.strip():
        raise HTTPException(status_code=400, detail="Customer name is required")
    phone = req.phone_number.strip()
    if not phone:
        raise HTTPException(status_code=400, detail="Mobile number is required")
    if len(phone) != 10 or not phone.isdigit():
        raise HTTPException(status_code=400, detail="Mobile number must contain exactly 10 digits")
    if req.alternate_number and req.alternate_number.strip():
        alt_phone = req.alternate_number.strip()
        if len(alt_phone) != 10 or not alt_phone.isdigit():
            raise HTTPException(status_code=400, detail="Alternate number must contain exactly 10 digits")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers WHERE phone_number = ?", (phone,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Mobile number must be unique")

    now = datetime.now()
    cust_id = get_next_id("CUST", "customers", "customer_id")
    created_date = req.created_date if req.created_date else now.strftime("%Y-%m-%d")
    updated_date = req.updated_date if req.updated_date else created_date
    time_str = now.strftime("%H:%M:%S")

    cursor.execute("""
    INSERT INTO customers (customer_id, customer_name, phone_number, alternate_number, email, address, created_date, updated_date, time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (cust_id, req.customer_name.strip(), phone, req.alternate_number.strip() if req.alternate_number else "", req.email.strip() if req.email else "", req.address.strip() if req.address else "", created_date, updated_date, time_str))
    conn.commit()
    conn.close()
    return {"message": "Customer created successfully", "customer_id": cust_id}

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Customer not found")
    return dict(row)

@app.put("/api/customers/{customer_id}")
def update_customer(customer_id: str, req: CustomerUpdateRequest):
    if not req.customer_name.strip():
        raise HTTPException(status_code=400, detail="Customer name is required")
    phone = req.phone_number.strip()
    if not phone:
        raise HTTPException(status_code=400, detail="Mobile number is required")
    if len(phone) != 10 or not phone.isdigit():
        raise HTTPException(status_code=400, detail="Mobile number must contain exactly 10 digits")
    if req.alternate_number and req.alternate_number.strip():
        alt_phone = req.alternate_number.strip()
        if len(alt_phone) != 10 or not alt_phone.isdigit():
            raise HTTPException(status_code=400, detail="Alternate number must contain exactly 10 digits")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers WHERE phone_number = ? AND customer_id != ?", (phone, customer_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Mobile number must be unique")

    now = datetime.now()
    updated_date = req.updated_date if req.updated_date else now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    cursor.execute("""
    UPDATE customers 
    SET customer_name = ?, phone_number = ?, alternate_number = ?, email = ?, address = ?, updated_date = ?, time = ?
    WHERE customer_id = ?
    """, (req.customer_name.strip(), phone, req.alternate_number.strip() if req.alternate_number else "", req.email.strip() if req.email else "", req.address.strip() if req.address else "", updated_date, time_str, customer_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Customer not found")
    conn.commit()
    conn.close()
    return {"message": "Customer updated successfully"}

@app.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM credit_transactions WHERE customer_id = ?", (customer_id,))
    cnt = cursor.fetchone()[0]
    if cnt > 0:
        conn.close()
        raise HTTPException(status_code=400, detail="Cannot delete customer because related transactions exist")
    cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()
    return {"message": "Customer deleted successfully"}

def calculate_customer_perf(customer_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_id, total_amount, due_date FROM credit_transactions WHERE customer_id = ?", (customer_id,))
    txns = cursor.fetchall()

    total_transactions = len(txns)
    total_credit = sum(t["total_amount"] for t in txns)
    
    cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE customer_id = ?", (customer_id,))
    sum_paid_row = cursor.fetchone()[0]
    total_paid = sum_paid_row if sum_paid_row is not None else 0.0

    pending_amount = max(0.0, total_credit - total_paid)
    
    # Overdue count
    overdue_count = 0
    today = date.today()
    for t in txns:
        t_id = t["transaction_id"]
        cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (t_id,))
        t_paid = cursor.fetchone()[0] or 0.0
        if t_paid < t["total_amount"]:
            try:
                d_date = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                if today > d_date:
                    overdue_count += 1
            except Exception:
                pass
    conn.close()

    if total_credit > 0:
        pct = round((total_paid / total_credit) * 100, 1)
    else:
        pct = 100.0 if total_transactions == 0 else 0.0

    if total_transactions == 0:
        status_str = "Good"
    elif overdue_count > 0:
        status_str = "Poor" if overdue_count > 1 else "Average"
    elif pending_amount > 0:
        status_str = "Average"
    elif pct >= 100:
        status_str = "Excellent"
    else:
        status_str = "Good"

    return {
        "total_transactions": total_transactions,
        "total_credit": total_credit,
        "total_paid": total_paid,
        "pending_amount": pending_amount,
        "overdue_count": overdue_count,
        "percentage": min(100.0, pct),
        "status": status_str
    }

@app.get("/api/customers/{customer_id}/summary")
def get_customer_summary(customer_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    cust = cursor.fetchone()
    if not cust:
        conn.close()
        raise HTTPException(status_code=404, detail="Customer not found")
    
    cursor.execute("SELECT * FROM credit_transactions WHERE customer_id = ? ORDER BY transaction_date DESC", (customer_id,))
    txns = [dict(t) for t in cursor.fetchall()]

    # Credited items for all transactions of customer
    txn_ids = [t["transaction_id"] for t in txns]
    items = []
    if txn_ids:
        placeholders = ",".join(["?"] * len(txn_ids))
        cursor.execute(f"SELECT * FROM credit_items WHERE transaction_id IN ({placeholders}) ORDER BY item_id ASC", txn_ids)
        items = [dict(i) for i in cursor.fetchall()]

    cursor.execute("SELECT * FROM payments WHERE customer_id = ? ORDER BY payment_date DESC", (customer_id,))
    payments = [dict(p) for p in cursor.fetchall()]
    conn.close()

    perf = calculate_customer_perf(customer_id)
    return {
        "customer": dict(cust),
        "transactions": txns,
        "items": items,
        "payments": payments,
        "performance": perf
    }

# TRANSACTIONS ENDPOINTS
@app.get("/api/transactions/next-id")
def get_transaction_next_id():
    return {"next_id": get_next_id("TXN", "credit_transactions", "transaction_id")}

@app.get("/api/transactions")
def get_transactions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.*, c.customer_name 
    FROM credit_transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    ORDER BY t.transaction_id DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]

    # compute real status
    for r in rows:
        cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (r["transaction_id"],))
        paid = cursor.fetchone()[0] or 0.0
        r["total_paid"] = paid
        r["pending_amount"] = max(0.0, r["total_amount"] - paid)
        r["payment_status"] = compute_transaction_status(r["total_amount"], paid, r["due_date"])
    conn.close()
    return rows

@app.post("/api/transactions")
def create_transaction(req: TransactionCreateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers WHERE customer_id = ?", (req.customer_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Customer not found")

    txn_id = get_next_id("TXN", "credit_transactions", "transaction_id")
    now = datetime.now()
    created_date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    status_str = compute_transaction_status(req.total_amount, 0.0, req.due_date)

    cursor.execute("""
    INSERT INTO credit_transactions (transaction_id, customer_id, transaction_date, due_date, total_amount, payment_status, note, created_date, updated_date, time)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (txn_id, req.customer_id, req.transaction_date, req.due_date, req.total_amount, status_str, req.note.strip() if req.note else "", created_date, created_date, time_str))
    conn.commit()
    conn.close()
    return {"message": "Transaction created successfully", "transaction_id": txn_id}

@app.get("/api/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.*, c.customer_name 
    FROM credit_transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    WHERE t.transaction_id = ?
    """, (transaction_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    data = dict(row)
    cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (transaction_id,))
    paid = cursor.fetchone()[0] or 0.0
    data["total_paid"] = paid
    data["pending_amount"] = max(0.0, data["total_amount"] - paid)
    data["payment_status"] = compute_transaction_status(data["total_amount"], paid, data["due_date"])
    conn.close()
    return data

@app.put("/api/transactions/{transaction_id}")
def update_transaction(transaction_id: str, req: TransactionUpdateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers WHERE customer_id = ?", (req.customer_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Customer not found")

    cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (transaction_id,))
    paid = cursor.fetchone()[0] or 0.0
    status_str = compute_transaction_status(req.total_amount, paid, req.due_date)

    now = datetime.now()
    updated_date = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    cursor.execute("""
    UPDATE credit_transactions
    SET customer_id = ?, transaction_date = ?, due_date = ?, total_amount = ?, payment_status = ?, note = ?, updated_date = ?, time = ?
    WHERE transaction_id = ?
    """, (req.customer_id, req.transaction_date, req.due_date, req.total_amount, status_str, req.note.strip() if req.note else "", updated_date, time_str, transaction_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    conn.commit()
    conn.close()
    return {"message": "Transaction updated successfully"}

@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credit_transactions WHERE transaction_id = ?", (transaction_id,))
    conn.commit()
    conn.close()
    return {"message": "Transaction deleted successfully"}

@app.get("/api/transactions/{transaction_id}/summary")
def get_transaction_summary(transaction_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT t.*, c.customer_name 
    FROM credit_transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    WHERE t.transaction_id = ?
    """, (transaction_id,))
    t_row = cursor.fetchone()
    if not t_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Transaction not found")
    txn = dict(t_row)

    cursor.execute("SELECT * FROM credit_items WHERE transaction_id = ?", (transaction_id,))
    items = [dict(i) for i in cursor.fetchall()]

    cursor.execute("SELECT * FROM payments WHERE transaction_id = ? ORDER BY payment_date DESC", (transaction_id,))
    payments = [dict(p) for p in cursor.fetchall()]
    conn.close()

    total_paid = sum(p["payment_amount"] for p in payments)
    pending = max(0.0, txn["total_amount"] - total_paid)
    status_str = compute_transaction_status(txn["total_amount"], total_paid, txn["due_date"])

    txn["total_paid"] = total_paid
    txn["pending_amount"] = pending
    txn["payment_status"] = status_str

    return {
        "transaction": txn,
        "items": items,
        "payments": payments
    }

# CREDIT ITEMS ENDPOINTS
@app.get("/api/items/next-id")
def get_item_next_id():
    return {"next_id": get_next_id("ITEM", "credit_items", "item_id")}

@app.get("/api/items")
def get_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM credit_items ORDER BY item_id ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/items")
def create_credit_item(req: CreditItemCreateRequest):
    if not req.item_name.strip():
        raise HTTPException(status_code=400, detail="Item name is required")
    if req.quantity <= 0 or req.unit_price < 0:
        raise HTTPException(status_code=400, detail="Invalid quantity or unit price")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_id FROM credit_transactions WHERE transaction_id = ?", (req.transaction_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Transaction not found")

    item_id = get_next_id("ITEM", "credit_items", "item_id")
    subtotal = round(req.quantity * req.unit_price, 2)
    credited_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO credit_items (item_id, transaction_id, item_name, quantity, unit_price, subtotal, credited_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (item_id, req.transaction_id, req.item_name.strip(), req.quantity, req.unit_price, subtotal, credited_at))
    conn.commit()
    conn.close()
    return {"message": "Credit item created successfully", "item_id": item_id}

@app.get("/api/items/{item_id}")
def get_item(item_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM credit_items WHERE item_id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Item not found")
    return dict(row)

@app.put("/api/items/{item_id}")
def update_item(item_id: str, req: CreditItemUpdateRequest):
    if not req.item_name.strip() or req.quantity <= 0 or req.unit_price < 0:
        raise HTTPException(status_code=400, detail="Invalid item details")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_id FROM credit_transactions WHERE transaction_id = ?", (req.transaction_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Transaction not found")

    subtotal = round(req.quantity * req.unit_price, 2)
    cursor.execute("""
    UPDATE credit_items
    SET transaction_id = ?, item_name = ?, quantity = ?, unit_price = ?, subtotal = ?
    WHERE item_id = ?
    """, (req.transaction_id, req.item_name.strip(), req.quantity, req.unit_price, subtotal, item_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    conn.commit()
    conn.close()
    return {"message": "Credit item updated successfully"}

@app.delete("/api/items/{item_id}")
def delete_item(item_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM credit_items WHERE item_id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item deleted successfully"}

# PAYMENTS ENDPOINTS
@app.get("/api/payments/next-id")
def get_payment_next_id():
    return {"next_id": get_next_id("PAY", "payments", "payment_id")}

@app.get("/api/payments")
def get_payments():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p.*, c.customer_name 
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
    ORDER BY p.payment_id DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/payments")
def create_payment(req: PaymentCreateRequest):
    if req.payment_amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, total_amount, due_date FROM credit_transactions WHERE transaction_id = ?", (req.transaction_id,))
    txn = cursor.fetchone()
    if not txn:
        conn.close()
        raise HTTPException(status_code=400, detail="Transaction not found")

    cust_id = txn["customer_id"]
    pay_id = get_next_id("PAY", "payments", "payment_id")

    cursor.execute("""
    INSERT INTO payments (payment_id, transaction_id, customer_id, payment_amount, payment_date, payment_method, reference_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (pay_id, req.transaction_id, cust_id, req.payment_amount, req.payment_date, req.payment_method.strip(), req.reference_id.strip() if req.reference_id else ""))
    
    # Recalculate transaction status
    cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (req.transaction_id,))
    total_paid = cursor.fetchone()[0] or 0.0
    new_status = compute_transaction_status(txn["total_amount"], total_paid, txn["due_date"])
    cursor.execute("UPDATE credit_transactions SET payment_status = ? WHERE transaction_id = ?", (new_status, req.transaction_id))

    conn.commit()
    conn.close()
    return {"message": "Payment created successfully", "payment_id": pay_id}

@app.get("/api/payments/{payment_id}")
def get_payment(payment_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT p.*, c.customer_name 
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
    WHERE p.payment_id = ?
    """, (payment_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Payment not found")
    return dict(row)

@app.put("/api/payments/{payment_id}")
def update_payment(payment_id: str, req: PaymentUpdateRequest):
    if req.payment_amount <= 0:
        raise HTTPException(status_code=400, detail="Payment amount must be positive")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_id FROM payments WHERE payment_id = ?", (payment_id,))
    p_row = cursor.fetchone()
    if not p_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Payment not found")

    txn_id = p_row["transaction_id"]
    cursor.execute("""
    UPDATE payments
    SET payment_amount = ?, payment_date = ?, payment_method = ?, reference_id = ?
    WHERE payment_id = ?
    """, (req.payment_amount, req.payment_date, req.payment_method.strip(), req.reference_id.strip() if req.reference_id else "", payment_id))

    # Recalculate transaction status
    cursor.execute("SELECT total_amount, due_date FROM credit_transactions WHERE transaction_id = ?", (txn_id,))
    t_row = cursor.fetchone()
    if t_row:
        cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (txn_id,))
        total_paid = cursor.fetchone()[0] or 0.0
        new_status = compute_transaction_status(t_row["total_amount"], total_paid, t_row["due_date"])
        cursor.execute("UPDATE credit_transactions SET payment_status = ? WHERE transaction_id = ?", (new_status, txn_id))

    conn.commit()
    conn.close()
    return {"message": "Payment updated successfully"}

@app.delete("/api/payments/{payment_id}")
def delete_payment(payment_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT transaction_id FROM payments WHERE payment_id = ?", (payment_id,))
    p_row = cursor.fetchone()
    if not p_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Payment not found")

    txn_id = p_row["transaction_id"]
    cursor.execute("DELETE FROM payments WHERE payment_id = ?", (payment_id,))

    # Recalculate transaction status
    cursor.execute("SELECT total_amount, due_date FROM credit_transactions WHERE transaction_id = ?", (txn_id,))
    t_row = cursor.fetchone()
    if t_row:
        cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (txn_id,))
        total_paid = cursor.fetchone()[0] or 0.0
        new_status = compute_transaction_status(t_row["total_amount"], total_paid, t_row["due_date"])
        cursor.execute("UPDATE credit_transactions SET payment_status = ? WHERE transaction_id = ?", (new_status, txn_id))

    conn.commit()
    conn.close()
    return {"message": "Payment deleted successfully"}

# OUTSTANDING BALANCE
@app.get("/api/outstanding")
def get_outstanding_balances():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_id ASC")
    customers = cursor.fetchall()
    
    result = []
    today = date.today()

    for c in customers:
        cid = c["customer_id"]
        cursor.execute("SELECT transaction_id, total_amount, due_date FROM credit_transactions WHERE customer_id = ?", (cid,))
        txns = cursor.fetchall()

        total_due = sum(t["total_amount"] for t in txns)
        cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE customer_id = ?", (cid,))
        total_paid = cursor.fetchone()[0] or 0.0

        pending_amount = max(0.0, total_due - total_paid)
        
        # nearest active due date
        latest_due = "-"
        has_overdue = False
        for t in txns:
            cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (t["transaction_id"],))
            t_paid = cursor.fetchone()[0] or 0.0
            if t_paid < t["total_amount"]:
                try:
                    d_date = datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                    if today > d_date:
                        has_overdue = True
                    latest_due = t["due_date"]
                except Exception:
                    pass

        if pending_amount <= 0:
            status_str = "Paid"
        elif has_overdue:
            status_str = "Overdue"
        else:
            status_str = "Pending"

        result.append({
            "customer_id": cid,
            "customer_name": c["customer_name"],
            "total_due": total_due,
            "total_paid": total_paid,
            "pending_amount": pending_amount,
            "due_date": latest_due,
            "status": status_str
        })
    conn.close()
    return result

# CUSTOMER PERFORMANCE
@app.get("/api/performance")
def get_customer_performance():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_id ASC")
    customers = cursor.fetchall()
    conn.close()

    result = []
    for c in customers:
        perf = calculate_customer_perf(c["customer_id"])
        result.append({
            "customer_id": c["customer_id"],
            "customer_name": c["customer_name"],
            "total_transactions": perf["total_transactions"],
            "total_credit": perf["total_credit"],
            "total_paid": perf["total_paid"],
            "pending_amount": perf["pending_amount"],
            "overdue_count": perf["overdue_count"],
            "performance_percentage": perf["percentage"],
            "performance_status": perf["status"]
        })
    return result

# DASHBOARD
@app.get("/api/dashboard")
def get_dashboard_summary():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    total_customers = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total_amount) FROM credit_transactions")
    total_credit = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT SUM(payment_amount) FROM payments")
    total_paid = cursor.fetchone()[0] or 0.0

    outstanding_balance = max(0.0, total_credit - total_paid)

    cursor.execute("""
    SELECT t.transaction_id, c.customer_name, t.total_amount, t.transaction_date, t.due_date, t.payment_status
    FROM credit_transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    ORDER BY t.transaction_id DESC LIMIT 5
    """)
    recent_transactions = [dict(r) for r in cursor.fetchall()]

    for r in recent_transactions:
        cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (r["transaction_id"],))
        p = cursor.fetchone()[0] or 0.0
        r["payment_status"] = compute_transaction_status(r["total_amount"], p, r["due_date"])

    conn.close()
    return {
        "total_customers": total_customers,
        "total_credit": total_credit,
        "total_paid": total_paid,
        "outstanding_balance": outstanding_balance,
        "recent_transactions": recent_transactions
    }

# SEARCH
@app.get("/api/search")
def search_system(q: str = Query("", min_length=1)):
    keyword = f"%{q.strip().lower()}%"
    conn = get_db()
    cursor = conn.cursor()

    # Search Customers
    cursor.execute("""
    SELECT customer_id, customer_name, phone_number, email 
    FROM customers
    WHERE LOWER(customer_id) LIKE ? OR LOWER(customer_name) LIKE ? OR phone_number LIKE ? OR LOWER(email) LIKE ?
    """, (keyword, keyword, keyword, keyword))
    customers = [dict(r) for r in cursor.fetchall()]

    # Search Transactions
    cursor.execute("""
    SELECT t.transaction_id, t.customer_id, c.customer_name, t.total_amount, t.transaction_date, t.payment_status
    FROM credit_transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    WHERE LOWER(t.transaction_id) LIKE ? OR LOWER(c.customer_name) LIKE ?
    """, (keyword, keyword))
    transactions = [dict(r) for r in cursor.fetchall()]

    # Search Items
    cursor.execute("""
    SELECT item_id, transaction_id, item_name, quantity, unit_price, subtotal
    FROM credit_items
    WHERE LOWER(item_id) LIKE ? OR LOWER(item_name) LIKE ? OR LOWER(transaction_id) LIKE ?
    """, (keyword, keyword, keyword))
    items = [dict(r) for r in cursor.fetchall()]

    # Search Payments
    cursor.execute("""
    SELECT p.payment_id, p.transaction_id, p.customer_id, c.customer_name, p.payment_amount, p.payment_date, p.payment_method
    FROM payments p
    JOIN customers c ON p.customer_id = c.customer_id
    WHERE LOWER(p.payment_id) LIKE ? OR LOWER(p.transaction_id) LIKE ? OR LOWER(c.customer_name) LIKE ?
    """, (keyword, keyword, keyword))
    payments = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "query": q,
        "customers": customers,
        "transactions": transactions,
        "items": items,
        "payments": payments
    }

# REPORTS GENERATION
@app.get("/api/reports")
def generate_report_data(
    report_type: str = Query("Customer Report"),
    customer_id: Optional[str] = None,
    transaction_id: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    report_lang: str = Query("English")
):
    conn = get_db()
    cursor = conn.cursor()

    report_payload = {
        "report_type": report_type,
        "report_lang": report_lang,
        "shop_name": "Nav Durga Super Market",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer": None,
        "transaction": None,
        "transactions": [],
        "items": [],
        "payments": [],
        "performance": None,
        "outstanding": None,
        "records": []
    }

    # Date filter query helper
    date_clause = ""
    params = []
    if from_date and to_date:
        if from_date > to_date:
            conn.close()
            raise HTTPException(status_code=400, detail="From Date cannot be after To Date")

    if report_type == "Customer Report":
        if not customer_id:
            conn.close()
            raise HTTPException(status_code=400, detail="Customer selection required for Customer Report")
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        c = cursor.fetchone()
        if not c:
            conn.close()
            raise HTTPException(status_code=404, detail="Customer not found")
        report_payload["customer"] = dict(c)

        sql = "SELECT * FROM credit_transactions WHERE customer_id = ?"
        p = [customer_id]
        if from_date and to_date:
            sql += " AND transaction_date BETWEEN ? AND ?"
            p.extend([from_date, to_date])
        cursor.execute(sql + " ORDER BY transaction_date DESC", p)
        report_payload["transactions"] = [dict(t) for t in cursor.fetchall()]

        t_ids = [t["transaction_id"] for t in report_payload["transactions"]]
        if t_ids:
            cursor.execute(f"SELECT * FROM credit_items WHERE transaction_id IN ({','.join(['?']*len(t_ids))})", t_ids)
            report_payload["items"] = [dict(i) for i in cursor.fetchall()]

        p_sql = "SELECT * FROM payments WHERE customer_id = ?"
        pp = [customer_id]
        if from_date and to_date:
            p_sql += " AND payment_date BETWEEN ? AND ?"
            pp.extend([from_date, to_date])
        cursor.execute(p_sql + " ORDER BY payment_date DESC", pp)
        report_payload["payments"] = [dict(pm) for pm in cursor.fetchall()]

        report_payload["performance"] = calculate_customer_perf(customer_id)

    elif report_type == "Credit Transaction Report":
        sql = """
        SELECT t.*, c.customer_name 
        FROM credit_transactions t
        JOIN customers c ON t.customer_id = c.customer_id
        WHERE 1=1
        """
        p = []
        if transaction_id:
            sql += " AND t.transaction_id = ?"
            p.append(transaction_id)
        if customer_id:
            sql += " AND t.customer_id = ?"
            p.append(customer_id)
        if from_date and to_date:
            sql += " AND t.transaction_date BETWEEN ? AND ?"
            p.extend([from_date, to_date])
        cursor.execute(sql + " ORDER BY t.transaction_id DESC", p)
        txns = [dict(t) for t in cursor.fetchall()]
        for t in txns:
            cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE transaction_id = ?", (t["transaction_id"],))
            paid = cursor.fetchone()[0] or 0.0
            t["total_paid"] = paid
            t["pending_amount"] = max(0.0, t["total_amount"] - paid)
            t["payment_status"] = compute_transaction_status(t["total_amount"], paid, t["due_date"])
        report_payload["transactions"] = txns

    elif report_type == "Credited Items Report":
        sql = """
        SELECT i.*, c.customer_name 
        FROM credit_items i
        JOIN credit_transactions t ON i.transaction_id = t.transaction_id
        JOIN customers c ON t.customer_id = c.customer_id
        WHERE 1=1
        """
        p = []
        if transaction_id:
            sql += " AND i.transaction_id = ?"
            p.append(transaction_id)
        if customer_id:
            sql += " AND t.customer_id = ?"
            p.append(customer_id)
        if from_date and to_date:
            sql += " AND substr(i.credited_at, 1, 10) BETWEEN ? AND ?"
            p.extend([from_date, to_date])
        cursor.execute(sql + " ORDER BY i.item_id ASC", p)
        report_payload["items"] = [dict(r) for r in cursor.fetchall()]

    elif report_type == "Payment Report":
        sql = """
        SELECT p.*, c.customer_name 
        FROM payments p
        JOIN customers c ON p.customer_id = c.customer_id
        WHERE 1=1
        """
        p = []
        if customer_id:
            sql += " AND p.customer_id = ?"
            p.append(customer_id)
        if transaction_id:
            sql += " AND p.transaction_id = ?"
            p.append(transaction_id)
        if from_date and to_date:
            sql += " AND p.payment_date BETWEEN ? AND ?"
            p.extend([from_date, to_date])
        cursor.execute(sql + " ORDER BY p.payment_date DESC", p)
        report_payload["payments"] = [dict(r) for r in cursor.fetchall()]

    elif report_type == "Outstanding Balance Report":
        cursor.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_id ASC")
        custs = cursor.fetchall()
        out_list = []
        for c in custs:
            cid = c["customer_id"]
            if customer_id and cid != customer_id:
                continue
            cursor.execute("SELECT total_amount FROM credit_transactions WHERE customer_id = ?", (cid,))
            tdue = sum(r[0] for r in cursor.fetchall())
            cursor.execute("SELECT SUM(payment_amount) FROM payments WHERE customer_id = ?", (cid,))
            tpaid = cursor.fetchone()[0] or 0.0
            pending = max(0.0, tdue - tpaid)
            out_list.append({
                "customer_id": cid,
                "customer_name": c["customer_name"],
                "total_due": tdue,
                "total_paid": tpaid,
                "pending_amount": pending,
                "status": "Paid" if pending <= 0 else "Pending"
            })
        report_payload["records"] = out_list

    elif report_type == "Customer Performance Summary Report":
        cursor.execute("SELECT customer_id, customer_name FROM customers ORDER BY customer_id ASC")
        custs = cursor.fetchall()
        perf_list = []
        for c in custs:
            if customer_id and c["customer_id"] != customer_id:
                continue
            perf = calculate_customer_perf(c["customer_id"])
            perf["customer_id"] = c["customer_id"]
            perf["customer_name"] = c["customer_name"]
            perf_list.append(perf)
        report_payload["records"] = perf_list

    elif report_type == "Complete Summary Report":
        # All customers with transactions, items, payments, performance
        cursor.execute("SELECT * FROM customers ORDER BY customer_id ASC")
        custs = [dict(c) for c in cursor.fetchall()]
        complete_data = []
        for c in custs:
            cid = c["customer_id"]
            if customer_id and cid != customer_id:
                continue
            cursor.execute("SELECT * FROM credit_transactions WHERE customer_id = ?", (cid,))
            ctxns = [dict(t) for t in cursor.fetchall()]
            cursor.execute("SELECT * FROM payments WHERE customer_id = ?", (cid,))
            cpays = [dict(p) for p in cursor.fetchall()]
            perf = calculate_customer_perf(cid)
            complete_data.append({
                "customer": c,
                "transactions": ctxns,
                "payments": cpays,
                "performance": perf
            })
        report_payload["records"] = complete_data

    conn.close()
    return report_payload
