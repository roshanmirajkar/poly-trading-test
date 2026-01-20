import dataclasses
import logging
from typing import Any, Dict, List, Optional

import requests


@dataclasses.dataclass
class Market:
    id: str
    question: str
    category: Optional[str]
    event_id: Optional[str]
    event_slug: Optional[str]
    outcomes: List[str]
    outcome_prices: List[float]


class PolymarketClient:
    def __init__(self, base_url: str = "https://gamma-api.polymarket.com") -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        logging.debug("Requesting %s with params=%s", url, params)
        response = self.session.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def list_markets(
        self,
        limit: int = 200,
        offset: int = 0,
        category: Optional[str] = None,
        active: bool = True,
        closed: bool = False,
    ) -> List[Market]:
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "active": str(active).lower(),
            "closed": str(closed).lower(),
        }
        if category:
            params["category"] = category

        data = self._get("/markets", params=params)
        markets: List[Market] = []
        for entry in data:
            outcomes = entry.get("outcomes") or []
            outcome_prices = entry.get("outcomePrices") or []
            markets.append(
                Market(
                    id=str(entry.get("id")),
                    question=entry.get("question") or "",
                    category=entry.get("category"),
                    event_id=entry.get("event_id") or entry.get("eventId"),
                    event_slug=entry.get("event_slug") or entry.get("eventSlug"),
                    outcomes=list(outcomes),
                    outcome_prices=[float(price) for price in outcome_prices],
                )
            )
        return markets
