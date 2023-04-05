from typing import Any, Dict, Optional, overload, Type, TypeVar

from dataclass_factory import Factory, NameStyle, Schema
from requests import RequestException, Session

from .exceptions import NintendoException
from .models import Order

TRIAL_URL = "https://try.dominodatalab.com"
PRODUCTION_URL = "https://api.dominodatalab.com"

T = TypeVar("T")


class NintendoBase:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or Session()
        self.factory = Factory(
            default_schema=Schema(name_style=NameStyle.camel_lower),
            schemas={
                Order: Schema(name_mapping={
                    "name": "contentName",
                    "price": ("total", "grandTotal")
                })
            })

    def _request(self, path: str, *, method: str, params: Optional[Dict[str, Any]] = None,
                 headers: Optional[Dict[str, Any]] = None, json=None, cookies=None):
        try:
            resp = self.session.request(
                method,
                path,
                params=params, headers=headers, json=json, cookies=cookies
            )
            resp.raise_for_status()
            return resp
        except RequestException as e:
            raise NintendoException from e

    def _get(self, path: str, *, model=None, **kwargs):
        resp = self._request(path, method="GET", **kwargs)
        if model is not None:
            return self.factory.load(
                resp.json(),
                model,
            )
        return resp

    def _post(self, path, *, model=None, **kwargs):
        resp = self._request(path, method="POST", **kwargs)
        if model is not None:
            return self.factory.load(
                resp.json(),
                model,
            )
        return resp
