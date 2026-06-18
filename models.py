import datetime
from sqlalchemy import Boolean, Integer, String, UniqueConstraint, DateTime, Text, false, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_orders_source_external_id"),
    )

    def __repr__(self):
        return (
            f"Order(id={self.id!r}), source={self.source!r}, external_id={self.external_id!r}, status={self.status!r}, contacted={self.contacted!r}"
        )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    budget: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(50))
    reason: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.now, server_default=text("now()"))
    parsed_budget: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sent_to_telegram: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    contacted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    project_type: Mapped[str] = mapped_column(String)
    matched_keyword: Mapped[str | None] = mapped_column(String, nullable=True)
    negative_keyword: Mapped[str | None] = mapped_column(String, nullable=True)
    risky_keyword: Mapped[str | None] = mapped_column(String, nullable=True)
