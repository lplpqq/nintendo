from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, List

from .order import Order


@dataclass
class Totals:
    digital: int
    physical: int

    @property
    def total_number(self):
        return self.digital + self.physical


@dataclass
class OrderHistory:
    totals: Totals
    orders: List[Order]


@dataclass
class Customer:
    email: Optional[str]
    order_history: OrderHistory


@dataclass
class Tokens:
    access_token: Optional[str]
    token_type: str = None
    code: str = None
    id_token: str = None
    customer_token: Optional[str] = None

    @property
    def authorization_token(self):
        return f'{self.token_type} {self.id_token}'


@dataclass
class Data:
    tokens: Tokens = None
    customer: Customer = None


@dataclass
class Response:
    data: Data
