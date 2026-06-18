from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel

import db
import db_sqlalchemy
from database import SessionLocal

app = FastAPI()


class OrderResponse(BaseModel):
    source: str
    external_id: str
    title: str
    url: str
    budget: str
    status: str
    reason: str
    project_type: str
    parsed_budget: int | None
    matched_keyword: str | None
    negative_keyword: str | None
    risky_keyword: str | None
    contacted: bool
    created_at: str


class OrdersListResponse(BaseModel):
    items: list[OrderResponse]
    count: int
    limit: int
    status: Literal["matched", "risky", "rejected"] | None


class StatusStat(BaseModel):
    status: str
    total: int


class RejectedReasonStat(BaseModel):
    reason: str
    total: int


class BudgetQualityStat(BaseModel):
    status: str
    total: int
    unknown_budget: int
    known_budget: int


class BudgetStat(BaseModel):
    status: str
    with_budget: int
    min_budget: int | None
    max_budget: int | None
    avg_budget: float | None


class TelegramStats(BaseModel):
    unsent_count: int


class StatsResponse(BaseModel):
    total_orders: int
    by_status: list[StatusStat]
    rejected_reasons: list[RejectedReasonStat]
    budget_quality: list[BudgetQualityStat]
    budget_stats: list[BudgetStat]
    telegram: TelegramStats


class OrderUpdateRequest(BaseModel):
    contacted: bool


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "freelance-monitor",
    }


@app.get("/orders/", response_model=OrdersListResponse)
def orders(limit: int = Query(20, ge=1, le=100),
           status: Literal["matched", "risky", "rejected"] | None = None):
    orders = db.get_all_orders(status=status, limit=limit)
    response = {
        "items": orders,
        "count": len(orders),
        "limit": limit,
        "status": status,
    }
    return response


@app.get("/orders/{source}/{external_id}", response_model=OrderResponse)
def get_order_detail(source: str, external_id: str):
    order = db.get_order_by_source_and_external_id(source, external_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/stats", response_model=StatsResponse)
def get_stats():
    total = db.get_orders_count()
    statuses = db.get_status_stats()
    rejected_reason = db.get_rejected_reason_stats()
    budget_quality = db.get_budget_quality_stats()
    budget_stats = db.get_budget_stats()
    tg_unsent = db.get_unsent_telegram_orders()

    return {
        "total_orders": total,
        "by_status": statuses,
        "rejected_reasons": rejected_reason,
        "budget_quality": budget_quality,
        "budget_stats": budget_stats,
        "telegram": {
            "unsent_count": len(tg_unsent)
        },
    }


@app.patch("/orders/{source}/{external_id}", response_model=OrderResponse)
def update_order(source: str, external_id: str, update_data: OrderUpdateRequest):
    updated = db.update_order_contacted(source, external_id, update_data.contacted)
    if not updated:
        raise HTTPException(status_code=404, detail="Failed to update order")
    order = db.get_order_by_source_and_external_id(source, external_id)
    return order


def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@app.get("/pg/orders/", response_model=OrdersListResponse)
def pg_orders(limit: int = Query(20, ge=1, le=100),
              status: Literal["matched", "risky", "rejected"] | None = None, session=Depends(get_db_session)):
    orders = db_sqlalchemy.get_all_orders_as_dicts(session, status=status, limit=limit)

    return {
        "items": orders,
        "count": len(orders),
        "limit": limit,
        "status": status,
    }

@app.get("/pg/orders/{source}/{external_id}", response_model=OrderResponse)
def pg_get_order_detail(source: str, external_id: str, session=Depends(get_db_session)):
    order = db_sqlalchemy.get_order_by_source_and_external_id_as_dict(session, source=source, external_id=external_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/pg/orders/{source}/{external_id}", response_model=OrderResponse)
def pg_update_order(source: str, external_id: str, update_data: OrderUpdateRequest, session=Depends(get_db_session)):
    updated = db_sqlalchemy.update_order_contacted_as_dict(session=session, source=source, external_id=external_id, contacted=update_data.contacted)
    if not updated:
        raise HTTPException(status_code=404, detail="Order not found")
    return updated