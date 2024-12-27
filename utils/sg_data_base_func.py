import sqlite3

# global connection
conn = None


def get_connection():
    global conn
    if conn is None:
        conn = sqlite3.connect("mingyuan_products.db")
    return conn

def create_database():
    # Connect to a single SQLite database
    conn = get_connection()
    cursor = conn.cursor()

    # Create Products table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY,
            sample_name TEXT NOT NULL,
            model_number TEXT NOT NULL,
            composition TEXT,
            weight TEXT,
            width TEXT,
            finished_price REAL,
            fabric_price REAL,
            remarks TEXT
        );
    """
    )

    # Save (commit) the changes
    conn.commit()

def add_product(id, sample_name, model_number, composition, weight, width, finished_price, fabric_price, remarks):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
        INSERT INTO Products (id, sample_name, model_number, composition, weight, width, finished_price, fabric_price, remarks)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
            (id, sample_name, model_number, composition, weight, width, finished_price, fabric_price, remarks),
        )

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database Error: {e}")

def close_connection():
    global conn
    if conn:
        conn.close()
        conn = None

def preview_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")

    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

# Initialize and load database
def initialize_database():
    global conn

    # Initialize the database tables
    create_database()

    initial_products = [
        (1, '小春日和-186A', '186A素色布', '100%polyester', '1350g', '定高280', 53.8, 39.8, '18个素色布'),
        (2, '小春日和-186A', '色织提花布', '100%polyester', '1350g', '定高280', None, 59.8, '4个色织提花布'),
        (3, '小春日和-186A', '亮片立边纱', '100%polyester', '1350g', '定宽130', None, 56.0, '只能做韩褶'),
        (4, '金枝玉叶-KK', 'KK素色布', '100%polyester', '1350g', '定高280', 53.8, 39.8, '24个素色布'),
        (5, '金枝玉叶-KK', 'F数码印花布', '100%polyester', '1350g', '定高280', None, 69.8, None),
        # 继续插入其他产品数据
    ]

    for product in initial_products:
        add_product(*product)

def get_fabric_price_by_model(model_number):
    conn = get_connection()  # 获取数据库连接
    cursor = conn.cursor()

    try:
        # 查询面料价
        cursor.execute(
            """
            SELECT fabric_price FROM Products
            WHERE model_number = ?;
            """, 
            (model_number,)
        )
        result = cursor.fetchone()
        
        if result:
            print(f"Fabric price for model '{model_number}': {result[0]}")
            return result[0]  # 返回查询结果
        else:
            print(f"No product found with model number '{model_number}'.")
            return None  # 如果没有找到对应产品，返回 None
    
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    
    finally:
        close_connection()  # 查询完成后关闭连接
