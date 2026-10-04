import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv 

# Load environment variables from .env file
load_dotenv()

# 1. อ่านไฟล์ CSV ของคุณ
df = pd.read_csv("archive/watch_history.csv")

# 2. ตั้งค่า Connection String จาก YugabyteDB
DB_URL = os.getenv("DB_URL")

# 3. สร้าง Connection Engine
engine = create_engine(DB_URL)

# 4. บันทึกเข้า Database (สร้างตารางชื่อ netflix_titles ให้อัตโนมัติ)
# if_exists='replace' จะสร้างตารางใหม่ทับถ้ามีอยู่แล้ว
df.to_sql(
    name="watch_history",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
)

print(f"นำเข้าข้อมูล {len(df)} แถวสำเร็จเรียบร้อย!")
