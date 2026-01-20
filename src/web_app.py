import logging
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template, request

from arbitrage_bot import ArbOpportunity, BotConfig, SportsArbitrageBot
from polymarket_client import PolymarketClient

app = Flask(__name__)


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/api/opportunities")
def api_opportunities():
    category = request.args.get("category", "sports")
    min_edge = float(request.args.get("min_edge", "0.01"))
    max_markets = int(request.args.get("max_markets", "200"))
    stake = float(request.args.get("stake", "100"))

    config = BotConfig(category=category, min_edge=min_edge, max_markets=max_markets)
    bot = SportsArbitrageBot(PolymarketClient(), config)
    markets = bot.fetch_sports_markets()
    opportunities = bot.find_arbitrage(markets)

    payload = [serialize_opportunity(bot, opp, stake) for opp in opportunities]
    return jsonify(payload)


def serialize_opportunity(
    bot: SportsArbitrageBot, opportunity: ArbOpportunity, stake: float
) -> Dict[str, Any]:
    orders = bot.build_orders(opportunity, stake=stake)
    return {
        "event_key": opportunity.event_key,
        "total_cost": opportunity.total_cost,
        "edge": 1.0 - opportunity.total_cost,
        "best_prices": opportunity.best_prices,
        "markets": opportunity.markets,
        "orders": orders,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=8000)
