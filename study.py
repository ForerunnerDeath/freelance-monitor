class SimpleOrder:
    def __init__(self, source, external_id, title, budget):
        self.source = source
        self.external_id = external_id
        self.title = title
        self.budget = budget
        self.contacted = False

    def __str__(self):
        return self.short_info()

    def has_budget(self):
        if self.budget is None or self.budget == "":
            return False
        else:
            return True
    
    @property
    def is_budget_known(self):
        if self.budget is None or self.budget == "":
            return False
        else:
            return True

    def short_info(self):
        if self.has_budget():
            return f"{self.source} #{self.external_id}: {self.title}, бюджет: {self.budget}"
        else:
            return f"{self.source} #{self.external_id}: {self.title}, бюджет не указан"

    def mark_contacted(self):
        self.contacted = True

    def set_contacted(self, contacted):
        self.contacted = contacted

    def __repr__(self):
        return f"SimpleOrder(source={self.source!r}, external_id={self.external_id!r}, title={self.title!r}, budget={self.budget!r})"

    def __eq__(self, other):
        if not isinstance(other, SimpleOrder):
            return False
        return self.source == other.source and self.external_id == other.external_id


order1 = SimpleOrder("fl_ru", "1", "Парсер", "15000")
order2 = SimpleOrder("fl_ru", "1", "Другое название", "20000")
order3 = SimpleOrder("profi_ru", "1", "Парсер", "15000")
order4 = SimpleOrder("fl_ru", "2", "Парсер", "15000")

print(order1 == order2)  # True
print(order1 == order3)  # False
print(order1 == order4)  # False
print(order1 == "test")  # False