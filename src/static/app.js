const scanBtn = document.getElementById("scan-btn");
const statusEl = document.getElementById("status");
const grid = document.getElementById("results-grid");

function setStatus(message, tone = "muted") {
  statusEl.textContent = message;
  statusEl.style.color = tone === "accent" ? "#8ef6ff" : "#9aa3b2";
}

function buildCard(opportunity) {
  const card = document.createElement("div");
  card.className = "card";

  const title = document.createElement("h3");
  title.textContent = opportunity.event_key;
  card.appendChild(title);

  const badgeRow = document.createElement("div");
  badgeRow.className = "badge-row";
  badgeRow.innerHTML = `
    <span class="badge">Total cost: ${opportunity.total_cost.toFixed(4)}</span>
    <span class="badge">Edge: ${opportunity.edge.toFixed(4)}</span>
  `;
  card.appendChild(badgeRow);

  const orders = document.createElement("div");
  orders.className = "orders";
  const ordersTitle = document.createElement("strong");
  ordersTitle.textContent = "Suggested bundle";
  orders.appendChild(ordersTitle);

  opportunity.orders.forEach((order) => {
    const line = document.createElement("div");
    line.innerHTML = `<span>${order.outcome}</span>Limit ${order.limit_price.toFixed(
      4
    )} · Size ${order.size.toFixed(2)}`;
    orders.appendChild(line);
  });

  card.appendChild(orders);
  return card;
}

async function runScan() {
  setStatus("Scanning markets...", "accent");
  grid.innerHTML = "";

  const params = new URLSearchParams({
    category: document.getElementById("category").value,
    min_edge: document.getElementById("min-edge").value,
    stake: document.getElementById("stake").value,
    max_markets: document.getElementById("max-markets").value,
  });

  try {
    const response = await fetch(`/api/opportunities?${params.toString()}`);
    const data = await response.json();

    if (!data.length) {
      setStatus("No opportunities found. Try lowering the edge.");
      return;
    }

    data.forEach((opp) => grid.appendChild(buildCard(opp)));
    setStatus(`Found ${data.length} opportunities.`, "accent");
  } catch (error) {
    console.error(error);
    setStatus("Scan failed. Try again.");
  }
}

scanBtn.addEventListener("click", runScan);
