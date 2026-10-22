// Lists the patient's upcoming appointments and pays a copay on a stored card.
//
// A payment is submitted with POST appointments/<id>/pay. The charge itself runs after the
// request returns, and its result is pushed to this page over a WebSocket, matched to the
// pending payment by idempotency key.

const PLUGIN_NAME = "appointment_copay_collection";
const RESULT_TIMEOUT_MS = 20000;

const STATUS_LABELS = {
  paid: "Copay paid",
  not_billable: "No payment needed for this visit",
  no_claim: "Payment isn't available for this visit yet",
  no_amount: "No copay on file for this visit",
};

let cards = [];
let pending = null;
// Charge results by idempotency key. A result can arrive before the pay request returns the
// key, so it is kept here until the pending payment can claim it.
const results = new Map();

const money = (value) => `$${Number(value).toFixed(2)}`;

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function showBanner(kind, message) {
  const banner = document.getElementById("banner");
  banner.className = kind;
  banner.textContent = message;
  banner.hidden = false;
}

function formatWhen(isoDate) {
  return new Date(isoDate).toLocaleString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function cardLabel(card) {
  const expiry = `${String(card.expiration_month).padStart(2, "0")}/${card.expiration_year}`;
  return `${card.brand} ending ${card.last_four} (exp. ${expiry})`;
}

function renderPayment(appointment) {
  const payment = element("div", "payment");
  payment.appendChild(element("span", "amount", money(appointment.amount)));

  if (cards.length === 0) {
    payment.appendChild(element("span", "muted", "Add a card to your account to pay online."));
    return payment;
  }

  const select = element("select");
  select.setAttribute("aria-label", "Card");
  for (const card of cards) {
    const option = element("option", undefined, cardLabel(card));
    option.value = card.id;
    select.appendChild(option);
  }

  const button = element("button", "pay", `Pay ${money(appointment.amount)}`);
  button.disabled = pending !== null;
  button.onclick = () => pay(appointment, select.value);

  payment.appendChild(select);
  payment.appendChild(button);
  return payment;
}

function renderAppointment(appointment) {
  const card = element("section", "appointment");
  card.appendChild(element("h2", undefined, formatWhen(appointment.start_time)));

  const details = [appointment.visit_type, appointment.provider, appointment.location]
    .filter(Boolean)
    .join(" · ");
  card.appendChild(element("div", "details", details));

  if (appointment.status === "due") {
    card.appendChild(renderPayment(appointment));
  } else {
    const className = appointment.status === "paid" ? "pill paid" : "pill";
    card.appendChild(element("span", className, STATUS_LABELS[appointment.status]));
  }
  return card;
}

async function load() {
  const response = await fetch("appointments");
  const data = await response.json();
  cards = data.cards;

  const container = document.getElementById("appointments");
  container.replaceChildren();
  if (data.appointments.length === 0) {
    container.appendChild(element("p", "muted", "You have no upcoming appointments."));
    return;
  }
  for (const appointment of data.appointments) {
    container.appendChild(renderAppointment(appointment));
  }
}

function finishPayment(kind, message) {
  if (pending) clearTimeout(pending.timer);
  pending = null;
  showBanner(kind, message);
  load();
}

async function pay(appointment, paymentCardId) {
  pending = { key: null, timer: null };
  document.querySelectorAll("button.pay").forEach((button) => (button.disabled = true));
  showBanner("", "Processing your payment…");

  try {
    const response = await fetch(`appointments/${appointment.id}/pay`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payment_card_id: paymentCardId }),
    });
    const data = await response.json();
    if (!response.ok) {
      finishPayment("error", data.error || "The payment couldn't be submitted.");
      return;
    }
    pending.key = data.idempotency_key;
    if (results.has(pending.key)) {
      showResult(results.get(pending.key));
      return;
    }
    // The charge result normally arrives over the WebSocket. If it doesn't, reload so the
    // appointment shows its current status.
    pending.timer = setTimeout(
      () => finishPayment("", "Your payment is still processing. Check back shortly."),
      RESULT_TIMEOUT_MS,
    );
  } catch (error) {
    finishPayment("error", "The payment couldn't be submitted.");
  }
}

function handleChargeResponse(message) {
  results.set(message.idempotency_key, message);
  if (pending && message.idempotency_key === pending.key) showResult(message);
}

function showResult(message) {
  if (message.success) {
    finishPayment("ok", `Payment of ${money(message.amount)} received. Thank you.`);
  } else {
    finishPayment("error", "Your card was not charged. Try another card or contact the office.");
  }
}

function connect() {
  const channel = document.body.dataset.channel;
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const socket = new WebSocket(
    `${protocol}//${window.location.host}/plugin-io/ws/${PLUGIN_NAME}/${channel}/`,
  );
  socket.onmessage = (event) => {
    let message = JSON.parse(event.data);
    // The broadcast arrives wrapped in an envelope whose `message` holds the payload.
    while (message && message.event_type === undefined && message.message !== undefined) {
      message = message.message;
    }
    if (message && message.event_type === "charge_response") handleChargeResponse(message);
  };
  socket.onclose = () => setTimeout(connect, 3000);
}

load();
connect();
