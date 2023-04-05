from dataclasses import dataclass
from typing import List

from .profile import Profile
from .order import Order


@dataclass
class User:
    profile: Profile
    orders: List[Order]
