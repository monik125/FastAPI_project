from fastapi import FastAPI, HTTPException
from datetime import datetime as dt
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Enum, TIMESTAMP, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

DB_URL = "mysql+pymysql://root:Test@123@localhost/product_db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Or restrict to specific methods like "POST"
    allow_headers=["*"],  # Or restrict to specific headers
)


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(Enum("finished", "semi-finished", "raw"), nullable=False)
    description = Column(String(250))
    product_image = Column(Text)
    sku = Column(String(100), unique=True, nullable=False)
    unit_of_measure = Column(Enum("mtr", "mm", "ltr", "ml", "cm", "mg", "gm", "unit", "pack"), nullable=False)
    lead_time = Column(Integer, nullable=False)
    created_date = Column(TIMESTAMP, default=dt.utcnow, nullable=False)
    updated_date = Column(TIMESTAMP, default=dt.utcnow, onupdate=dt.utcnow, nullable=False)

Base.metadata.create_all(bind=engine)

class ProductBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: str = Field(..., pattern="^(finished|semi-finished|raw)$")
    description: Optional[str] = Field(None, max_length=250)
    product_image: Optional[str] = None
    sku: str = Field(..., max_length=100)
    unit_of_measure: str = Field(..., pattern="^(mtr|mm|ltr|ml|cm|mg|gm|unit|pack)$")
    lead_time: int = Field(..., ge=0, le=999)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int
    created_date: dt
    updated_date: dt

# @app.get('/')
# def root():
#     return{"hello": "world"}

@app.get("/product/list", response_model=List[ProductResponse])
def list_products(page: int = 1):
    db = SessionLocal()
    try:
        offset = (page - 1) * 10
        products = db.query(Product).offset(offset).limit(10).all()
        return products
    finally:
        db.close()

@app.get("/product/{pid}/info", response_model=ProductResponse)
def get_product_info(pid: int):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.product_id == pid).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    finally:
        db.close()

@app.post("/product/add", response_model=ProductResponse)
def add_product(product: ProductCreate):
    db = SessionLocal()
    try:
        db_product = Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    finally:
        db.close()

@app.put("/product/{pid}/update", response_model=ProductResponse)
def update_product(pid: int, product: ProductUpdate):
    db = SessionLocal()
    try:
        db_product = db.query(Product).filter(Product.product_id == pid).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_product, key, value)

        db.commit()
        db.refresh(db_product)
        return db_product
    finally:
        db.close()