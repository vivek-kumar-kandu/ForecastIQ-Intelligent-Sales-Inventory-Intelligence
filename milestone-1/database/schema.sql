-- ============================================================
-- ForecastinQ - Intelligent Sales Forecasting System
-- SQLite Schema (converted from MySQL) v1.0
-- ============================================================

PRAGMA foreign_keys = ON;

CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff' CHECK(role IN ('admin','manager','staff')),
    status VARCHAR(20) DEFAULT 'active' CHECK(status IN ('active','inactive')),
    last_login DATETIME,
    remember_token VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK(status IN ('active','inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    total_purchases DECIMAL(15,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active' CHECK(status IN ('active','inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    category_id INTEGER,
    brand VARCHAR(100),
    supplier_id INTEGER,
    cost_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    selling_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    stock_quantity INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    reorder_quantity INTEGER DEFAULT 50,
    image_path VARCHAR(255),
    description TEXT,
    status VARCHAR(20) DEFAULT 'active' CHECK(status IN ('active','inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
);

CREATE TABLE inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    movement_type VARCHAR(20) NOT NULL CHECK(movement_type IN ('in','out','adjustment')),
    quantity INTEGER NOT NULL,
    reference VARCHAR(100),
    notes TEXT,
    moved_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (moved_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_code VARCHAR(30) UNIQUE NOT NULL,
    customer_id INTEGER,
    user_id INTEGER,
    total_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    discount DECIMAL(10,2) DEFAULT 0.00,
    tax DECIMAL(10,2) DEFAULT 0.00,
    grand_total DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    payment_method VARCHAR(20) DEFAULT 'cash' CHECK(payment_method IN ('cash','card','online','upi')),
    status VARCHAR(20) DEFAULT 'completed' CHECK(status IN ('completed','pending','cancelled')),
    sale_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE sales_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    forecast_type VARCHAR(20) NOT NULL CHECK(forecast_type IN ('weekly','monthly','quarterly','yearly')),
    algorithm VARCHAR(30) NOT NULL CHECK(algorithm IN ('linear_regression','moving_average','exponential_smoothing')),
    forecast_date DATE NOT NULL,
    predicted_sales DECIMAL(15,2),
    actual_sales DECIMAL(15,2),
    confidence_score DECIMAL(5,2),
    generated_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    type VARCHAR(20) NOT NULL CHECK(type IN ('low_stock','out_of_stock','forecast','sales_target','system')),
    title VARCHAR(200) NOT NULL,
    message TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type VARCHAR(100),
    generated_by INTEGER,
    parameters TEXT,
    file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (generated_by) REFERENCES users(id) ON DELETE SET NULL
);

-- ============================================================
-- SAMPLE DATA
-- ============================================================

INSERT INTO settings (setting_key, setting_value) VALUES
('company_name', 'ForecastinQ Pvt. Ltd.'),
('company_email', 'info@forecastinq.com'),
('company_phone', '+91-9876543210'),
('company_address', '123 Business Park, Chennai, Tamil Nadu'),
('currency', 'INR'),
('currency_symbol', '₹'),
('tax_rate', '18'),
('low_stock_threshold', '10'),
('theme', 'light'),
('app_version', '1.0.0');

-- Admin/Manager/Staff users: password = Admin@123 (hashed at DB-init time in Python using werkzeug, see init_db.py)
INSERT INTO users (full_name, email, username, phone, password_hash, role) VALUES
('Admin User', 'admin@forecastinq.com', 'admin', '9876543210', '__HASH__', 'admin'),
('Rajesh Manager', 'manager@forecastinq.com', 'manager', '9876543211', '__HASH__', 'manager'),
('Priya Staff', 'staff@forecastinq.com', 'staff', '9876543212', '__HASH__', 'staff');

INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic gadgets and devices'),
('Clothing', 'Apparel and fashion items'),
('Food & Beverages', 'Grocery and food products'),
('Furniture', 'Home and office furniture'),
('Sports', 'Sports equipment and accessories'),
('Books', 'Educational and general books');

INSERT INTO suppliers (supplier_code, name, email, phone, address, city, country) VALUES
('SUP001', 'TechSource India', 'contact@techsource.in', '9811122233', '45 Industrial Area', 'Mumbai', 'India'),
('SUP002', 'FashionHub Pvt Ltd', 'orders@fashionhub.com', '9822233344', '78 Garment District', 'Surat', 'India'),
('SUP003', 'FreshMart Suppliers', 'supply@freshmart.in', '9833344455', '12 Food Park', 'Delhi', 'India'),
('SUP004', 'WoodCraft Furniture', 'info@woodcraft.com', '9844455566', '34 Timber Nagar', 'Bangalore', 'India'),
('SUP005', 'SportZone Distributors', 'dist@sportzone.in', '9855566677', '56 Sports Complex', 'Pune', 'India');

INSERT INTO customers (customer_code, name, email, phone, address, city, country) VALUES
('CUST001', 'Arjun Sharma', 'arjun.sharma@gmail.com', '9900011122', '12 MG Road', 'Chennai', 'India'),
('CUST002', 'Meena Krishnan', 'meena.k@gmail.com', '9900022233', '34 Anna Nagar', 'Chennai', 'India'),
('CUST003', 'Vikram Patel', 'vikram.p@yahoo.com', '9900033344', '56 Banjara Hills', 'Hyderabad', 'India'),
('CUST004', 'Sunita Reddy', 'sunita.r@gmail.com', '9900044455', '78 Koramangala', 'Bangalore', 'India'),
('CUST005', 'Anil Kumar', 'anil.k@gmail.com', '9900055566', '90 Sector 21', 'Noida', 'India');

INSERT INTO products (product_code, name, category_id, brand, supplier_id, cost_price, selling_price, stock_quantity, min_stock_level, reorder_quantity) VALUES
('PRD001', 'Samsung Galaxy S24', 1, 'Samsung', 1, 65000, 79999, 45, 10, 20),
('PRD002', 'Apple iPhone 15', 1, 'Apple', 1, 75000, 89999, 30, 5, 15),
('PRD003', 'HP Laptop 15s', 1, 'HP', 1, 45000, 55000, 20, 5, 10),
('PRD004', 'Men''s Formal Shirt', 2, 'Arrow', 2, 800, 1499, 120, 20, 50),
('PRD005', 'Women''s Kurti Set', 2, 'Biba', 2, 600, 1299, 85, 15, 40),
('PRD006', 'Basmati Rice 5kg', 3, 'India Gate', 3, 350, 499, 200, 50, 100),
('PRD007', 'Sunflower Oil 5L', 3, 'Fortune', 3, 600, 750, 8, 20, 50),
('PRD008', 'Office Chair Ergonomic', 4, 'Featherlite', 4, 8000, 12999, 15, 5, 10),
('PRD009', 'Cricket Bat MRF', 5, 'MRF', 5, 1200, 1999, 3, 10, 20),
('PRD010', 'NCERT Class 12 Set', 6, 'NCERT', 1, 400, 650, 60, 10, 30);

-- Sample sales dated relative to "today" are inserted separately by init_db.py
-- so the dashboard/forecast charts always show recent, meaningful data.

INSERT INTO notifications (user_id, type, title, message) VALUES
(1, 'low_stock', 'Low Stock Alert', 'Sunflower Oil 5L is running low (8 units left).'),
(1, 'low_stock', 'Low Stock Alert', 'Cricket Bat MRF has only 3 units remaining.'),
(1, 'forecast', 'Forecast Ready', 'Monthly sales forecast for January has been generated.'),
(2, 'sales_target', 'Sales Target', 'You are 85% towards your monthly sales target.'),
(1, 'system', 'System Update', 'ForecastinQ v1.0.0 is now running.');
