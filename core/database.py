import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Optional
import json


class DatabaseManager:
    def __init__(self, db_config: Dict):
        """
        Initialize database connection with configuration
        
        Args:
            db_config: Dictionary containing database credentials
                {
                    'host': 'localhost',
                    'database': 'your_db',
                    'user': 'your_user',
                    'password': 'your_password',
                    'port': 3306
                }
        """
        self.db_config = db_config
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Connect to database when entering context manager"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connection when exiting context manager"""
        self.close()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor(dictionary=True)
            print("Successfully connected to database")
        except Error as e:
            print(f"Database connection failed: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def execute_query(self, query: str, params: Optional[tuple] = None):
        """Execute a single SQL query"""
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor
        except Error as e:
            self.connection.rollback()
            print(f"Query failed: {e}\nQuery: {query}")
            raise
    
    
    def insert_categories(self, categories: List[Dict]):
        """
        Insert scraped categories into database
        Args:
            products: List of product dictionaries with:
                - name
                - url
        """
        try:
            insert_query = """
                INSERT INTO categories (
                    category_name, category_url
                ) VALUES (
                    %(name)s, %(url)s)
            """
            
            self.cursor.executemany(insert_query, categories)
            self.connection.commit()
            print(f"Inserted/updated {len(categories)} categories")

        except Error as e:
            self.connection.rollback()
            print(f"Category insertion failed: {e}")
            raise
    

    def get_pending_categories(self) -> List[Dict]:
        """Fetch categories that haven't been processed yet"""
        self.cursor.execute("""
            SELECT id, category_name, category_url
            FROM categories
            WHERE status IS NULL OR status != 'done'
        """)
        return self.cursor.fetchall()

    def insert_products(self, products: List[Dict]):
        """
        Insert scraped product details into the database.

        Args:
            products: List of product dictionaries with keys:
                - UPC
                - URL
                - name
                - categories (list, stored as JSON)
                - image
                - storeId
                - storeLocation
                - price
                - mrp
                - availability
                - keyword
                - size
        """
        try:
            insert_query = """
                INSERT INTO products (
                    upc, url, name, categories, image, store_id,
                    store_location, price, mrp, availability,
                    keyword, size
                ) VALUES (
                    %(UPC)s, %(URL)s, %(name)s, %(categories)s, %(image)s,
                    %(storeId)s, %(storeLocation)s, %(price)s, %(mrp)s,
                    %(availability)s, %(keyword)s, %(size)s
                )
            """

            # Convert `categories` list to JSON string before insert
            for product in products:
                product["categories"] = json.dumps(product.get("categories", []))

            self.cursor.executemany(insert_query, products)
            self.connection.commit()
            print(f"Inserted/updated {len(products)} products")

        except Error as e:
            self.connection.rollback()
            print(f"Product insertion failed: {e}")
            raise
