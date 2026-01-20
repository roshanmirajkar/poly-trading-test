import dataclasses
import logging
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple

from polymarket_client import Market, PolymarketClient


@dataclasses.dataclass
class ArbOpportunity:
    event_key: str
    total_cost: float
    best_prices: Dict[str, float]
    markets: Dict[str, str]
    orders: List[Dict[str, float]] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class BotConfig:
    category: str = "sports"
    max_markets: int = 500
    min_edge: float = 0.01


class SportsArbitrageBot:
    def __init__(self, client: PolymarketClient, config: Optional[BotConfig] = None) -> None:
        self.client = client
        self.config = config or BotConfig()

    def fetch_sports_markets(self) -> List[Market]:
        markets: List[Market] = []
        offset = 0
        while len(markets) < self.config.max_markets:
            batch = self.client.list_markets(
                limit=min(200, self.config.max_markets - len(markets)),
                offset=offset,
                category=self.config.category,
                active=True,
                closed=False,
            )
            if not batch:
                break
            markets.extend(batch)
            offset += len(batch)
        logging.info("Fetched %s markets", len(markets))
        return markets

    def group_by_event(self, markets: Iterable[Market]) -> Dict[str, List[Market]]:
        grouped: Dict[str, List[Market]] = defaultdict(list)
        for market in markets:
            event_key = market.event_slug or market.event_id or market.question
            grouped[event_key].append(market)
        return grouped

    def find_arbitrage(self, markets: Iterable[Market]) -> List[ArbOpportunity]:
        grouped = self.group_by_event(markets)
        opportunities: List[ArbOpportunity] = []
        for event_key, event_markets in grouped.items():
            best_prices, market_map = self._best_prices_for_event(event_markets)
            if not best_prices:
                continue
            total_cost = sum(best_prices.values())
            edge = 1.0 - total_cost
            if edge >= self.config.min_edge:
                opportunities.append(
                    ArbOpportunity(
                        event_key=event_key,
                        total_cost=total_cost,
                        best_prices=best_prices,
                        markets=market_map,
                    )
                )
        return sorted(opportunities, key=lambda opp: opp.total_cost)

    def _best_prices_for_event(self, markets: Iterable[Market]) -> Tuple[Dict[str, float], Dict[str, str]]:
        best_prices: Dict[str, float] = {}
        market_map: Dict[str, str] = {}
        for market in markets:
            for outcome, price in zip(market.outcomes, market.outcome_prices):
                if price <= 0:
                    continue
                if outcome not in best_prices or price < best_prices[outcome]:
                    best_prices[outcome] = price
                    market_map[outcome] = market.id
        return best_prices, market_map

    def build_orders(self, opportunity: ArbOpportunity, stake: float) -> List[Dict[str, float]]:
        orders = []
        for outcome, price in opportunity.best_prices.items():
            size = stake / price
            orders.append({"outcome": outcome, "limit_price": price, "size": size})
        return orders
