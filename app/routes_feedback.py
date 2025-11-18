from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .database import get_db
from .models import Feedback, Product, User
from .schemas import FeedbackJoined, RawFeedbackOut

from pathlib import Path
import csv


router = APIRouter(prefix="/feedback", tags=["Feedback"])

# Lokasi file CSV mentah
# Struktur project kita: sentiment-system/app/..., data di sentiment-system/data/7282_1.csv
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "7282_1.csv"


# =====================================================
# 1. FEEDBACK (DATA DARI DATABASE)
#    - sudah diproses
#    - punya product_name, username, sentiment_label, text_length
# =====================================================
@router.get("/", response_model=List[FeedbackJoined])
def list_feedback(
    db: Session = Depends(get_db),
    product_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    rating_min: Optional[int] = Query(None, ge=0, le=5),
    rating_max: Optional[int] = Query(None, ge=0, le=5),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    # Query join 3 tabel: feedback + products + users
    q = (
        db.query(
            Feedback.id,
            Feedback.product_id,
            Product.name.label("product_name"),
            Feedback.user_id,
            User.username,
            Feedback.rating,
            Feedback.title,
            Feedback.text,
            Feedback.review_date,
            Feedback.sentiment_label,
            Feedback.text_length,
            Feedback.created_at,
        )
        .join(Product, Feedback.product_id == Product.id)
        .join(User, Feedback.user_id == User.id, isouter=True)
    )

    filters = []
    if product_id is not None:
        filters.append(Feedback.product_id == product_id)
    if user_id is not None:
        filters.append(Feedback.user_id == user_id)
    if rating_min is not None:
        filters.append(Feedback.rating >= rating_min)
    if rating_max is not None:
        filters.append(Feedback.rating <= rating_max)

    if filters:
        q = q.filter(and_(*filters))

    q = q.order_by(Feedback.id).offset(offset).limit(limit)

    rows = q.all()
    # mapping manual ke dict agar sesuai schema FeedbackJoined
    return [
        {
            "id": r.id,
            "product_id": r.product_id,
            "product_name": r.product_name,
            "user_id": r.user_id,
            "username": r.username,
            "rating": r.rating,
            "title": r.title,
            "text": r.text,
            "review_date": r.review_date,
            "sentiment_label": r.sentiment_label,
            "text_length": r.text_length,
            "created_at": r.created_at,
        }
        for r in rows
    ]


# =====================================================
# 2. FEEDBACK RAW (DATA MENTAH DARI CSV KAGGLE)
#    - tidak lewat database
#    - tidak ada sentiment_label, product_id, user_id
#    - field mengikuti kolom di file 7282_1.csv
# =====================================================
@router.get("/raw", response_model=List[RawFeedbackOut])
def list_feedback_raw(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    if not CSV_PATH.exists():
        raise HTTPException(
            status_code=500,
            detail=f"CSV tidak ditemukan di: {CSV_PATH}",
        )

    results: List[dict] = []

    try:
        # Baca file CSV dengan DictReader
        with CSV_PATH.open(mode="r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for idx, row in enumerate(reader):
                # skip sampai offset
                if idx < offset:
                    continue
                # stop kalau sudah cukup limit
                if len(results) >= limit:
                    break

                rec = {
                    "address": row.get("address"),
                    "categories": row.get("categories"),
                    "city": row.get("city"),
                    "country": row.get("country"),
                    "latitude": row.get("latitude"),
                    "longitude": row.get("longitude"),
                    "name": row.get("name"),
                    "postalCode": row.get("postalCode"),
                    "province": row.get("province"),

                    "reviews_date": row.get("reviews.date"),
                    "reviews_dateAdded": row.get("reviews.dateAdded"),
                    "reviews_doRecommend": row.get("reviews.doRecommend"),
                    "reviews_id": row.get("reviews.id"),
                    "reviews_rating": row.get("reviews.rating"),
                    "reviews_text": row.get("reviews.text"),
                    "reviews_title": row.get("reviews.title"),
                    "reviews_userCity": row.get("reviews.userCity"),
                    "reviews_username": row.get("reviews.username"),
                    "reviews_userProvince": row.get("reviews.userProvince"),
                }
                results.append(rec)

    except Exception as e:
        # kalau ada error baca csv, lempar ke client
        raise HTTPException(
            status_code=500,
            detail=f"Error membaca CSV: {e}",
        )

    return results
