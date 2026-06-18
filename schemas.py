from typing import Literal

from pydantic import BaseModel


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