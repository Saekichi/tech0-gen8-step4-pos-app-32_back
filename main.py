from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ここでCORSMiddlewareをインポート
import pymysql # 小文字でインポート（念のため）

app = FastAPI()

# MySQL接続設定
connection = pymysql.connect(
    host='tech0-gen-8-step4-db-2.mysql.database.azure.com',
    user='Tech0Gen8TA2',
    password='gen8-1-ta@2',
    db='class2_db',  # Azureのデータベースタブから確認
    ssl={'ca':'/Users/saekichiaki/CA/DigiCertGlobalRootCA.crt.pem'} # CA証明書のパスを指定
)

# CORSミドルウェアを追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可（実際の運用時は制限をかけることを推奨）
    allow_credentials=True,
    allow_methods=["*"],  # すべてのメソッドを許可
    allow_headers=["*"],  # すべてのヘッダーを許可
)

# ルートエンドポイントの追加
@app.get("/")
def read_root():
    return {"message": "Welcome to the POS System!"}

@app.get("/product/{product_code}")
def get_product(product_code: str):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM m_product_saekichi WHERE code=%s", (product_code,))
    product = cursor.fetchone()
    
    if product:
        return {"code": product[1], "name": product[2], "price": product[3]} 
    return {"error": "Product not found"}

# 購入処理用API
@app.post("/purchase")
def create_purchase(purchase_data: dict):
    cashier_code = purchase_data.get("cashier_code")
    store_code = purchase_data.get("store_code")
    pos_id = purchase_data.get("pos_id")
    product_list = purchase_data.get("product_list")
    
    total_amount = 0
    cursor = connection.cursor()
    
    cursor.execute("""
        INSERT INTO transactions (cashier_code, store_code, pos_id, date_time, total_amount)
        VALUES (%s, %s, %s, NOW(), %s)
    """, (cashier_code, store_code, pos_id, total_amount))
    
    for product in product_list:
        product_code = product["code"]
        product_name = product["name"]
        price = product["price"]
        
        cursor.execute("""
            INSERT INTO transaction_details (transaction_id, product_code, product_name, price)
            VALUES (LAST_INSERT_ID(), %s, %s, %s)
        """, (product_code, product_name, price))
        
        total_amount += price
    
    cursor.execute("""
        UPDATE transactions SET total_amount=%s WHERE id=LAST_INSERT_ID()
    """, (total_amount,))
    
    connection.commit()
    return {"message": "Purchase completed", "total_amount": total_amount}
