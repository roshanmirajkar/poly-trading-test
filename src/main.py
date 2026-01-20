import argparse
import logging
from typing import List

from arbitrage_bot import BotConfig, SportsArbitrageBot
from polymarket_client import PolymarketClient


def format_opportunity(opportunity, stake: float) -> str:
    lines: List[str] = [
        f"Event: {opportunity.event_key}",
        f"Total cost: {opportunity.total_cost:.4f}",
        f"Edge: {1.0 - opportunity.total_cost:.4f}",
        "Orders:",
    ]
    for order in opportunity.orders:
        lines.append(
            f"  - Outcome: {order['outcome']} | Limit: {order['limit_price']:.4f} | Size: {order['size']:.2f}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Polymarket sports arbitrage bot")
    parser.add_argument("--category", default="sports", help="Market category to filter")
    parser.add_argument("--min-edge", type=float, default=0.01, help="Minimum arbitrage edge")
    parser.add_argument("--stake", type=float, default=100.0, help="Stake per arbitrage bundle")
    parser.add_argument("--max-markets", type=int, default=500, help="Maximum markets to scan")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logs")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    config = BotConfig(category=args.category, min_edge=args.min_edge, max_markets=args.max_markets)
    bot = SportsArbitrageBot(PolymarketClient(), config)
    markets = bot.fetch_sports_markets()
    opportunities = bot.find_arbitrage(markets)

    if not opportunities:
        logging.info("No arbitrage opportunities found.")
        return

    for opportunity in opportunities:
        opportunity.orders = bot.build_orders(opportunity, stake=args.stake)
        print(format_opportunity(opportunity, stake=args.stake))
        print("-" * 40)


if __name__ == "__main__":
    main()
