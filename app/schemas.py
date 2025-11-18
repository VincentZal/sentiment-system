from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class ConfigORM(BaseModel):
    class Config:
        orm_mode = True


# =========================
# PRODUCT
# =========================
class ProductOut(ConfigORM):
    id: int
    name: Optional[str]
    categories: Optional[str]
    address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    country: Optional[str]
    postalCode: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]


# =========================
# USER
# =========================
class UserOut(ConfigORM):
    id: int
    username: Optional[str]
    user_city: Optional[str]
    user_province: Optional[str]
    created_at: datetime


# =========================
# FEEDBACK (DARI DATABASE)
# =========================
class FeedbackOut(ConfigORM):
    id: int
    product_id: int
    user_id: Optional[int]
    rating: Optional[int]
    title: Optional[str]
    text: Optional[str]
    review_date: Optional[datetime]
    sentiment_label: Optional[str]
    text_length: int
    created_at: datetime


# Expanded feedback dengan JOIN product & user
class FeedbackJoined(ConfigORM):
    id: int
    product_id: int
    product_name: Optional[str]
    user_id: Optional[int]
    username: Optional[str]
    rating: Optional[int]
    title: Optional[str]
    text: Optional[str]
    review_date: Optional[datetime]
    sentiment_label: Optional[str]
    text_length: int
    created_at: datetime


# =========================
# SENTIMENT OVERVIEW
# =========================
class SentimentOverview(ConfigORM):
    positive: int
    neutral: int
    negative: int
    total: int


# =========================
# SENTIMEN PER PRODUK
# =========================
class ProductSentiment(ConfigORM):
    product_id: int
    product_name: Optional[str]
    city: Optional[str]
    country: Optional[str]
    reviews_count: int
    positive: int
    neutral: int
    negative: int
    positive_pct: float
    avg_rating: Optional[float]


# =========================
# TREND SENTIMEN (TIME SERIES)
# =========================
class TrendPoint(ConfigORM):
    period: str          # contoh: "2016-05"
    positive: int
    neutral: int
    negative: int
    total: int


class TrendSeries(ConfigORM):
    series: List[TrendPoint]


# =========================
# RAW FEEDBACK (LANGSUNG DARI CSV)
# - tidak pakai database
# - tidak ada sentiment_label, product_id, user_id
# - semua field string agar parsing simpel
# =========================
class RawFeedbackOut(BaseModel):
    address: Optional[str]
    categories: Optional[str]
    city: Optional[str]
    country: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    name: Optional[str]
    postalCode: Optional[str]
    province: Optional[str]

    reviews_date: Optional[str]
    reviews_dateAdded: Optional[str]
    reviews_doRecommend: Optional[str]
    reviews_id: Optional[str]
    reviews_rating: Optional[str]
    reviews_text: Optional[str]
    reviews_title: Optional[str]
    reviews_userCity: Optional[str]
    reviews_username: Optional[str]
    reviews_userProvince: Optional[str]
