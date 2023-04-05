from dataclasses import dataclass


@dataclass
class Order:
    name: str
    order_date: str
    price: float
    currency: str
    id: str

    @property
    def url(self):
        return f'https://www.nintendo.com/orders/{self.id}/'
