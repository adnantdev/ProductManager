# database.py - Fixed Complete Version
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import uuid
import os

class Database:
    def __init__(self, db_path="products.db"):
        self.db_path = db_path
        self.init_database()
        self.migrate_database()
    
    def init_database(self):
        """Initialize database with all tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    supplier_id INTEGER,
                    min_quantity INTEGER DEFAULT 5,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    barcode TEXT UNIQUE,
                    weight REAL,
                    dimensions TEXT,
                    notes TEXT,
                    image_path TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Suppliers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Categories table - Fixed with proper columns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    color TEXT,
                    icon TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            
            # Inventory transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    previous_quantity INTEGER,
                    new_quantity INTEGER,
                    reference TEXT,
                    notes TEXT,
                    created_by TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Barcode scan history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS barcode_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode TEXT NOT NULL,
                    product_id TEXT,
                    scan_time TEXT NOT NULL,
                    ip_address TEXT,
                    device_info TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            """)
            
            # Insert default categories if not exists
            default_categories = [
                ('Electronics', 'Electronic devices and accessories', '#4CAF50'),
                ('Clothing', 'Apparel and fashion items', '#2196F3'),
                ('Food', 'Food and beverages', '#FF9800'),
                ('Books', 'Books and publications', '#9C27B0'),
                ('Furniture', 'Furniture and home decor', '#795548'),
                ('Other', 'Other items', '#607D8B')
            ]
            
            now = datetime.now().isoformat()
            for name, desc, color in default_categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO categories (name, description, color, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, desc, color, now, now))
            
            conn.commit()
    
    def migrate_database(self):
        """Migrate database to add new columns if needed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check and add missing columns to products
            cursor.execute("PRAGMA table_info(products)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'supplier_id' not in columns:
                cursor.execute("ALTER TABLE products ADD COLUMN supplier_id INTEGER")
            
            if 'is_active' not in columns:
                cursor.execute("ALTER TABLE products ADD COLUMN is_active INTEGER DEFAULT 1")
            
            if 'image_path' not in columns:
                cursor.execute("ALTER TABLE products ADD COLUMN image_path TEXT")
            
            # Check suppliers table
            cursor.execute("PRAGMA table_info(suppliers)")
            supplier_columns = [column[1] for column in cursor.fetchall()]
            
            if 'is_active' not in supplier_columns:
                cursor.execute("ALTER TABLE suppliers ADD COLUMN is_active INTEGER DEFAULT 1")
            
            # Check categories table
            cursor.execute("PRAGMA table_info(categories)")
            category_columns = [column[1] for column in cursor.fetchall()]
            
            if 'updated_at' not in category_columns:
                try:
                    cursor.execute("ALTER TABLE categories ADD COLUMN updated_at TEXT")
                    # Update existing records with current time
                    now = datetime.now().isoformat()
                    cursor.execute("UPDATE categories SET updated_at = ? WHERE updated_at IS NULL", (now,))
                except:
                    pass
            
            if 'is_active' not in category_columns:
                try:
                    cursor.execute("ALTER TABLE categories ADD COLUMN is_active INTEGER DEFAULT 1")
                except:
                    pass
            
            if 'icon' not in category_columns:
                try:
                    cursor.execute("ALTER TABLE categories ADD COLUMN icon TEXT")
                except:
                    pass
            
            conn.commit()
    
    # ============ Product CRUD ============
    
    def add_product(self, data: Dict) -> str:
        """Add a new product"""
        product_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if barcode exists
            if data.get('barcode'):
                cursor.execute("SELECT id FROM products WHERE barcode = ? AND is_active = 1", (data['barcode'],))
                if cursor.fetchone():
                    raise ValueError(f"Barcode {data['barcode']} already exists!")
            
            # Handle supplier_id
            supplier_id = data.get('supplier_id')
            if supplier_id and isinstance(supplier_id, str):
                try:
                    supplier_id = int(supplier_id)
                except:
                    supplier_id = None
            
            cursor.execute("""
                INSERT INTO products (
                    id, name, description, price, quantity, category, 
                    status, supplier_id, min_quantity, created_at, updated_at,
                    barcode, weight, dimensions, notes, image_path, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                data.get('name'),
                data.get('description', ''),
                data.get('price', 0.0),
                data.get('quantity', 0),
                data.get('category', 'Other'),
                data.get('status', 'Active' if data.get('quantity', 0) > 0 else 'Out of Stock'),
                supplier_id,
                data.get('min_quantity', 5),
                now,
                now,
                data.get('barcode', ''),
                data.get('weight', 0.0),
                data.get('dimensions', ''),
                data.get('notes', ''),
                data.get('image_path', ''),
                1
            ))
            
            # Log initial inventory
            if data.get('quantity', 0) > 0:
                cursor.execute("""
                    INSERT INTO inventory_transactions (
                        product_id, type, quantity, previous_quantity, 
                        new_quantity, reference, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id, 'INITIAL', data['quantity'], 0, 
                    data['quantity'], 'Initial Stock', 'Initial inventory setup', now
                ))
            
            conn.commit()
            return product_id
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get a product by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, s.name as supplier_name, s.contact_person, s.phone as supplier_phone,
                       s.email as supplier_email
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.id = ? AND p.is_active = 1
            """, (product_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict]:
        """Get a product by barcode"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, s.name as supplier_name, s.contact_person, s.phone as supplier_phone
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.barcode = ? AND p.is_active = 1
            """, (barcode,))
            row = cursor.fetchone()
            
            # Log the scan
            if row:
                cursor.execute("""
                    INSERT INTO barcode_scans (barcode, product_id, scan_time)
                    VALUES (?, ?, ?)
                """, (barcode, row['id'], datetime.now().isoformat()))
                conn.commit()
            
            return dict(row) if row else None
    
    def get_all_products(self, category: str = None, search: str = None, 
                        supplier_id: int = None, status: str = None,
                        include_inactive: bool = False) -> List[Dict]:
        """Get all products with optional filters"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT p.*, s.name as supplier_name, s.contact_person
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE 1=1
            """
            params = []
            
            if not include_inactive:
                query += " AND p.is_active = 1"
            
            if category:
                query += " AND p.category = ?"
                params.append(category)
            
            if supplier_id:
                query += " AND p.supplier_id = ?"
                params.append(supplier_id)
            
            if status:
                query += " AND p.status = ?"
                params.append(status)
            
            if search:
                query += """ AND (p.name LIKE ? OR p.description LIKE ? 
                           OR p.barcode LIKE ? OR s.name LIKE ? OR p.id LIKE ?)"""
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term, search_term, search_term])
            
            query += " ORDER BY p.name"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_product(self, product_id: str, data: Dict) -> bool:
        """Update a product"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current data
            cursor.execute("SELECT quantity, barcode FROM products WHERE id = ?", (product_id,))
            current = cursor.fetchone()
            if not current:
                return False
            
            old_quantity = current[0]
            old_barcode = current[1]
            new_quantity = data.get('quantity', old_quantity)
            
            # Check barcode uniqueness
            if data.get('barcode') and data['barcode'] != old_barcode:
                cursor.execute("SELECT id FROM products WHERE barcode = ? AND id != ? AND is_active = 1", 
                             (data['barcode'], product_id))
                if cursor.fetchone():
                    raise ValueError(f"Barcode {data['barcode']} already exists!")
            
            # Build update query
            updates = []
            params = []
            
            for field in ['name', 'description', 'price', 'quantity', 'category', 
                         'supplier_id', 'min_quantity', 'barcode', 'weight', 
                         'dimensions', 'notes', 'image_path']:
                if field in data:
                    updates.append(f"{field} = ?")
                    params.append(data[field])
            
            # Auto-update status based on quantity
            if 'quantity' in data:
                new_status = 'Active' if data['quantity'] > 0 else 'Out of Stock'
                updates.append("status = ?")
                params.append(new_status)
            
            if updates:
                params.append(datetime.now().isoformat())
                params.append(product_id)
                
                query = f"UPDATE products SET {', '.join(updates)}, updated_at = ? WHERE id = ? AND is_active = 1"
                cursor.execute(query, params)
                
                # Log quantity change
                if old_quantity != new_quantity:
                    cursor.execute("""
                        INSERT INTO inventory_transactions (
                            product_id, type, quantity, previous_quantity, 
                            new_quantity, notes, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        product_id,
                        'UPDATE',
                        abs(new_quantity - old_quantity),
                        old_quantity,
                        new_quantity,
                        f"Updated from {old_quantity} to {new_quantity}",
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                return True
        
        return False
    
    def toggle_product_active(self, product_id: str, active: bool) -> bool:
        """Toggle product active status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE products 
                SET is_active = ?, updated_at = ? 
                WHERE id = ?
            """, (1 if active else 0, datetime.now().isoformat(), product_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_product(self, product_id: str, permanent: bool = False) -> bool:
        """Delete or soft-delete a product"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if permanent:
                # Also delete the image file if exists
                cursor.execute("SELECT image_path FROM products WHERE id = ?", (product_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    try:
                        os.remove(result[0])
                    except:
                        pass
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            else:
                cursor.execute("""
                    UPDATE products SET is_active = 0, updated_at = ? 
                    WHERE id = ?
                """, (datetime.now().isoformat(), product_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # ============ Inventory Operations ============
    
    def add_stock(self, product_id: str, quantity: int, reference: str = "", 
                  notes: str = "", created_by: str = "") -> bool:
        """Add stock to a product (receive shipment)"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive!")
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT quantity FROM products WHERE id = ? AND is_active = 1", (product_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            old_quantity = result[0]
            new_quantity = old_quantity + quantity
            
            cursor.execute("""
                UPDATE products 
                SET quantity = ?, updated_at = ?, status = ? 
                WHERE id = ?
            """, (
                new_quantity, 
                datetime.now().isoformat(),
                'Active' if new_quantity > 0 else 'Out of Stock',
                product_id
            ))
            
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    product_id, type, quantity, previous_quantity, 
                    new_quantity, reference, notes, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id, 'RECEIVE', quantity, old_quantity, 
                new_quantity, reference, notes, created_by, datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
    
    def remove_stock(self, product_id: str, quantity: int, reference: str = "", 
                     notes: str = "", created_by: str = "") -> bool:
        """Remove stock from a product (sale/adjustment)"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive!")
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT quantity FROM products WHERE id = ? AND is_active = 1", (product_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            old_quantity = result[0]
            if old_quantity < quantity:
                raise ValueError(f"Insufficient stock! Available: {old_quantity}, Requested: {quantity}")
            
            new_quantity = old_quantity - quantity
            
            cursor.execute("""
                UPDATE products 
                SET quantity = ?, updated_at = ?, status = ? 
                WHERE id = ?
            """, (
                new_quantity, 
                datetime.now().isoformat(),
                'Active' if new_quantity > 0 else 'Out of Stock',
                product_id
            ))
            
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    product_id, type, quantity, previous_quantity, 
                    new_quantity, reference, notes, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id, 'REMOVE', quantity, old_quantity, 
                new_quantity, reference, notes, created_by, datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
    
    def adjust_stock(self, product_id: str, quantity: int, reason: str = "",
                     notes: str = "", created_by: str = "") -> bool:
        """Adjust stock to a specific quantity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT quantity FROM products WHERE id = ? AND is_active = 1", (product_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            old_quantity = result[0]
            new_quantity = quantity
            
            if new_quantity < 0:
                raise ValueError("Quantity cannot be negative!")
            
            cursor.execute("""
                UPDATE products 
                SET quantity = ?, updated_at = ?, status = ? 
                WHERE id = ?
            """, (
                new_quantity, 
                datetime.now().isoformat(),
                'Active' if new_quantity > 0 else 'Out of Stock',
                product_id
            ))
            
            diff = new_quantity - old_quantity
            trans_type = 'ADJUST_IN' if diff > 0 else 'ADJUST_OUT'
            
            cursor.execute("""
                INSERT INTO inventory_transactions (
                    product_id, type, quantity, previous_quantity, 
                    new_quantity, reference, notes, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id, trans_type, abs(diff), old_quantity, 
                new_quantity, reason, notes, created_by, datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
    
    def get_inventory_transactions(self, product_id: str = None, 
                                   limit: int = 100) -> List[Dict]:
        """Get inventory transaction history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT t.*, p.name as product_name, p.barcode
                FROM inventory_transactions t
                JOIN products p ON t.product_id = p.id
            """
            params = []
            
            if product_id:
                query += " WHERE t.product_id = ?"
                params.append(product_id)
            
            query += " ORDER BY t.created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    # ============ Supplier Management ============
    
    def add_supplier(self, data: Dict) -> int:
        """Add a new supplier"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if supplier exists
            if data.get('name'):
                cursor.execute("SELECT id FROM suppliers WHERE name = ? AND is_active = 1", (data['name'],))
                if cursor.fetchone():
                    raise ValueError(f"Supplier '{data['name']}' already exists!")
            
            cursor.execute("""
                INSERT INTO suppliers (
                    name, contact_person, email, phone, address, notes, 
                    created_at, updated_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('name'),
                data.get('contact_person', ''),
                data.get('email', ''),
                data.get('phone', ''),
                data.get('address', ''),
                data.get('notes', ''),
                now,
                now,
                1
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_supplier(self, supplier_id: int) -> Optional[Dict]:
        """Get a supplier by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, COUNT(p.id) as product_count
                FROM suppliers s
                LEFT JOIN products p ON s.id = p.supplier_id AND p.is_active = 1
                WHERE s.id = ? AND s.is_active = 1
                GROUP BY s.id
            """, (supplier_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_suppliers(self, search: str = None) -> List[Dict]:
        """Get all suppliers"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = """
                SELECT s.*, COUNT(p.id) as product_count
                FROM suppliers s
                LEFT JOIN products p ON s.id = p.supplier_id AND p.is_active = 1
                WHERE s.is_active = 1
            """
            params = []
            
            if search:
                query += """ AND (s.name LIKE ? OR s.contact_person LIKE ? 
                           OR s.email LIKE ? OR s.phone LIKE ?)"""
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term, search_term])
            
            query += " GROUP BY s.id ORDER BY s.name"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_supplier(self, supplier_id: int, data: Dict) -> bool:
        """Update a supplier"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if name conflicts
            if data.get('name'):
                cursor.execute("SELECT id FROM suppliers WHERE name = ? AND id != ? AND is_active = 1", 
                             (data['name'], supplier_id))
                if cursor.fetchone():
                    raise ValueError(f"Supplier '{data['name']}' already exists!")
            
            updates = []
            params = []
            
            for field in ['name', 'contact_person', 'email', 'phone', 'address', 'notes']:
                if field in data:
                    updates.append(f"{field} = ?")
                    params.append(data[field])
            
            if updates:
                params.append(datetime.now().isoformat())
                params.append(supplier_id)
                
                query = f"UPDATE suppliers SET {', '.join(updates)}, updated_at = ? WHERE id = ? AND is_active = 1"
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        
        return False
    
    def delete_supplier(self, supplier_id: int, permanent: bool = False) -> bool:
        """Delete or soft-delete a supplier"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if supplier has products
            cursor.execute("SELECT COUNT(*) FROM products WHERE supplier_id = ? AND is_active = 1", (supplier_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                raise ValueError(f"Cannot delete supplier with {count} associated products! Please reassign or delete the products first.")
            
            if permanent:
                cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,))
            else:
                cursor.execute("""
                    UPDATE suppliers SET is_active = 0, updated_at = ? 
                    WHERE id = ?
                """, (datetime.now().isoformat(), supplier_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    # ============ Category Management ============
    
    def add_category(self, name: str, description: str = "", color: str = "#4CAF50") -> int:
        """Add a new category"""
        now = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if category exists
            cursor.execute("SELECT id FROM categories WHERE name = ? AND is_active = 1", (name,))
            if cursor.fetchone():
                raise ValueError(f"Category '{name}' already exists!")
            
            cursor.execute("""
                INSERT INTO categories (name, description, color, created_at, updated_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, description, color, now, now, 1))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.*, COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.name = p.category AND p.is_active = 1
                WHERE c.is_active = 1
                GROUP BY c.id
                ORDER BY c.name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_category(self, category_id: int, data: Dict) -> bool:
        """Update a category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            for field in ['name', 'description', 'color', 'icon']:
                if field in data:
                    updates.append(f"{field} = ?")
                    params.append(data[field])
            
            if updates:
                params.append(datetime.now().isoformat())
                params.append(category_id)
                
                query = f"UPDATE categories SET {', '.join(updates)}, updated_at = ? WHERE id = ? AND is_active = 1"
                cursor.execute(query, params)
                conn.commit()
                return cursor.rowcount > 0
        
        return False
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category (soft delete)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if category has products
            cursor.execute("""
                SELECT COUNT(*) FROM products 
                WHERE category = (SELECT name FROM categories WHERE id = ?) 
                AND is_active = 1
            """, (category_id,))
            count = cursor.fetchone()[0]
            if count > 0:
                raise ValueError(f"Cannot delete category with {count} associated products!")
            
            cursor.execute("""
                UPDATE categories SET is_active = 0, updated_at = ? 
                WHERE id = ?
            """, (datetime.now().isoformat(), category_id))
            conn.commit()
            return cursor.rowcount > 0
    
    # ============ Dashboard Statistics ============
    
    def get_statistics(self) -> Dict:
        """Get comprehensive statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total products and value
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(price * quantity) as total_value,
                    AVG(price) as avg_price,
                    SUM(quantity) as total_quantity
                FROM products 
                WHERE is_active = 1
            """)
            stats = cursor.fetchone()
            
            # Low stock count
            cursor.execute("""
                SELECT COUNT(*) FROM products 
                WHERE is_active = 1 AND quantity <= min_quantity AND quantity > 0
            """)
            low_stock = cursor.fetchone()[0]
            
            # Out of stock
            cursor.execute("""
                SELECT COUNT(*) FROM products 
                WHERE is_active = 1 AND quantity = 0
            """)
            out_of_stock = cursor.fetchone()[0]
            
            # Active vs inactive
            cursor.execute("""
                SELECT COUNT(*) FROM products WHERE is_active = 1
            """)
            active = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM products WHERE is_active = 0
            """)
            inactive = cursor.fetchone()[0]
            
            # Total suppliers
            cursor.execute("""
                SELECT COUNT(*) FROM suppliers WHERE is_active = 1
            """)
            total_suppliers = cursor.fetchone()[0]
            
            # Recent transactions count (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) FROM inventory_transactions 
                WHERE created_at >= ?
            """, (week_ago,))
            recent_transactions = cursor.fetchone()[0]
            
            # Category breakdown
            cursor.execute("""
                SELECT category, COUNT(*) as count, SUM(quantity) as total_qty,
                       SUM(price * quantity) as total_value
                FROM products 
                WHERE is_active = 1
                GROUP BY category
            """)
            category_stats = [{'category': row[0], 'count': row[1], 'total_quantity': row[2], 'total_value': row[3]} 
                            for row in cursor.fetchall()]
            
            return {
                'total_products': stats[0] or 0,
                'total_value': stats[1] or 0.0,
                'avg_price': stats[2] or 0.0,
                'total_quantity': stats[3] or 0,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock,
                'active_products': active,
                'inactive_products': inactive,
                'total_suppliers': total_suppliers,
                'recent_transactions': recent_transactions,
                'category_stats': category_stats
            }
    
    def get_low_stock_products(self) -> List[Dict]:
        """Get products with quantity below minimum"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, s.name as supplier_name, s.contact_person, s.phone as supplier_phone
                FROM products p
                LEFT JOIN suppliers s ON p.supplier_id = s.id
                WHERE p.is_active = 1 AND p.quantity <= p.min_quantity AND p.quantity > 0
                ORDER BY p.quantity
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_category_counts(self) -> Dict[str, int]:
        """Get count of products per category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM products 
                WHERE is_active = 1 
                GROUP BY category
            """)
            return {row[0]: row[1] for row in cursor.fetchall()}
    
    def get_transactions(self, product_id: str = None, limit: int = 100) -> List[Dict]:
        """Get transaction history (legacy support)"""
        return self.get_inventory_transactions(product_id, limit)
    
    def get_suppliers(self) -> List[str]:
        """Get supplier names (legacy support)"""
        suppliers = self.get_all_suppliers()
        return [s['name'] for s in suppliers]
    
    def get_categories(self) -> List[Dict]:
        """Get all categories (legacy support)"""
        return self.get_all_categories()
    
    def get_supplier_id_by_name(self, name: str) -> Optional[int]:
        """Get supplier ID by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM suppliers WHERE name = ? AND is_active = 1", (name,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_barcode_scan_history(self, limit: int = 50) -> List[Dict]:
        """Get barcode scan history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bs.*, p.name as product_name
                FROM barcode_scans bs
                LEFT JOIN products p ON bs.product_id = p.id
                ORDER BY bs.scan_time DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]