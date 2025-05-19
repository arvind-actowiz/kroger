# Kroger Scraper

A Python project to scrape categories and product details from Kroger and store it in a MySQL database.

## Database Schema

### Categories Table
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    category_url VARCHAR(255) NOT NULL,
    STATUS ENUM('pending', 'done') NOT NULL DEFAULT 'pending'
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    UPC VARCHAR(64),
    URL TEXT,
    NAME VARCHAR(255),
    categories JSON,
    image TEXT,
    store_id VARCHAR(64),
    store_location VARCHAR(255),
    price VARCHAR(10),
    mrp VARCHAR(10),
    availability VARCHAR(32) DEFAULT 'in stock',
    keyword VARCHAR(255),
    size VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Setup Instructions

Clone the repository:
```
git clone https://github.com/arvind-actowiz/kroger.git
cd kroger
```

Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Create a .env file based on .env.example and configure your database connection:
```
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

Set up your MySQL database with the provided schema.
