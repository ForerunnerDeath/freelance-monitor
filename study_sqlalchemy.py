from getpass import getpass

from sqlalchemy import create_engine, Boolean, Integer, String, select, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.exc import IntegrityError

password = getpass("PostgreSQL password: ")

database_url = (
    f"postgresql+psycopg://postgres:{password}"
    f"@localhost:5432/freelance_monitor"
    )

engine = create_engine(database_url, echo=True)


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_orders_source_external_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(50))
    external_id: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(500))
    contacted: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return (
            f"Order(id={self.id!r}, "
            f"source={self.source!r}, "
            f"external_id={self.external_id!r}, "
            f"title={self.title!r}, "
            f"contacted={self.contacted!r})"
        )


Base.metadata.create_all(engine)


def save_order(session, order):
    try:
        session.add(order)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def get_order(session, source, external_id):
    statement = select(Order).where(
        Order.source == source,
        Order.external_id == external_id,
    )
    result = session.execute(statement)
    order = result.scalars().first()
    return order


def update_order_contacted(session, source, external_id, contacted):
    order = get_order(session, source, external_id)

    if order is None:
        return False
    order.contacted = contacted
    session.commit()
    return True


with Session(engine) as session:
    updated = update_order_contacted(session, "fl_ru", "test-2", True)
    print("Updated to True:", updated)

with Session(engine) as session:
    updated = update_order_contacted(session, "fl_ru", "not-exists", True)
    print("Updated not exists:", updated)