from models import Order
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


def save_order(session, order_data, check_result, sent_to_telegram=False):
    orm_order = Order(
        source=order_data.get("source", ""),
        external_id=str(order_data.get("external_id", "")),
        title=order_data.get("title", "Без названия"),
        url=order_data.get("url", ""),
        description=order_data.get("description", ""),
        budget=str(order_data.get("budget") or ""),
        project_type=order_data.get("project_type", ""),

        status=check_result.get("status", ""),
        reason=check_result.get("reason"),
        parsed_budget=check_result.get("budget"),
        matched_keyword=check_result.get("matched_keyword"),
        negative_keyword=check_result.get("negative_keyword"),
        risky_keyword=check_result.get("risky_keyword"),

        sent_to_telegram=sent_to_telegram,
        contacted=False,

    )
    try:
        session.add(orm_order)
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def get_order_by_source_and_external_id(session, source, external_id):
    statement = select(Order).where(
        Order.source == source,
        Order.external_id == external_id,
    )
    result = session.execute(statement)
    order = result.scalars().first()
    return order


def update_order_contacted(session, source, external_id, contacted):
    db_order = get_order_by_source_and_external_id(session, source, external_id)
    if db_order is None:
        return False
    db_order.contacted = contacted
    session.commit()
    return True


def get_all_orders(session, status=None, limit=20):
    statement = select(Order)
    if status is not None:
        statement = statement.where(Order.status == status)
    statement = statement.order_by(Order.id.desc())
    statement = statement.limit(limit)
    result = session.execute(statement)
    orders = result.scalars().all()
    return orders


def order_to_dict(order):
    if order.created_at is None:
        created_at = ""
    else:
        created_at = order.created_at.isoformat(timespec="seconds")
    return {
        "source": order.source,
        "external_id": order.external_id,
        "title": order.title,
        "url": order.url,
        "budget": order.budget,
        "status": order.status,
        "reason": order.reason,
        "project_type": order.project_type,
        "parsed_budget": order.parsed_budget,
        "matched_keyword": order.matched_keyword,
        "negative_keyword": order.negative_keyword,
        "risky_keyword": order.risky_keyword,
        "contacted": order.contacted,
        "created_at": created_at,
        "sent_to_telegram": order.sent_to_telegram,
    }


def get_all_orders_as_dicts(session, status=None, limit=20):
    orders = get_all_orders(session, status=status, limit=limit)
    result = []
    for order in orders:
        result.append(order_to_dict(order))
    return result


def get_order_by_source_and_external_id_as_dict(session, source, external_id):
    order = get_order_by_source_and_external_id(session, source, external_id)
    if order is None:
        return None
    return order_to_dict(order)


def update_order_contacted_as_dict(session, source, external_id, contacted):
    updated = update_order_contacted(session, source, external_id, contacted)
    if not updated:
        return None
    return get_order_by_source_and_external_id_as_dict(session, source, external_id)


def mark_order_sent_to_telegram(session, source, external_id):
    db_order = get_order_by_source_and_external_id(session, source, external_id)
    if db_order is None:
        return False
    db_order.sent_to_telegram = True
    session.commit()
    return True


def get_unsent_telegram_orders(session):
    statement = select(Order).where(
        Order.status.in_(["matched", "risky"]),
        Order.sent_to_telegram.is_(False),
    )
    statement = statement.order_by(Order.id.asc())
    result = session.execute(statement)
    orders = result.scalars().all()
    return orders


def get_unsent_telegram_orders_as_dicts(session):
    orders = get_unsent_telegram_orders(session)
    result = []
    for order in orders:
        result.append(order_to_dict(order))
    return result


def is_order_seen(session, source, external_id):
    db_order = get_order_by_source_and_external_id(session, source, external_id)
    return db_order is not None
