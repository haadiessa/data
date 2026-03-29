from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# آپ کا نیون (Neon) ڈیٹا بیس کا آن لائن لنک
# ہم نے اسے براہ راست یہاں لکھ دیا ہے تاکہ ورسل اسے فورا پہچان لے
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_A4MKorq6avFZ@ep-ancient-leaf-amopq2iw-pooler.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require"

# ڈیٹا بیس انجن بنانا
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ڈیٹا بیس سیشن حاصل کرنے کا فنکشن (جو main.py میں استعمال ہوتا ہے)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()