def get_sample_orders():
    orders = [
        {
            "source": "test",
            "external_id": "1",
            "title": "Telegram bot",
            "url": "https://example.com/orders/1",
            "description": "Need a simple Telegram bot for notifications",
            "budget": 7000,
            "tags": ["python", "telegram"],
        },
        {
            "source": "test",
            "external_id": "2",
            "title": "Fix layout",
            "url": "https://example.com/orders/2",
            "description": "Need to fix HTML and CSS layout",
            "budget": 3000,
            "tags": ["html", "css"],
        },
    ]

    return orders