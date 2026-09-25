import { Hono } from "hono";

// Страница теста берётся из репозитория и обновляется раз в 5 минут,
// поэтому правки в index.html попадают на сайт без передеплоя.
const PAGE_URL =
  "https://raw.githubusercontent.com/melnikmotion-lab/tg-bot/claude/hopeful-tesla-nt719i/psychotype-test/index.html";
const PAGE_TTL_MS = 5 * 60 * 1000;
let page = { html: "", at: 0 };

async function getPage(): Promise<string> {
  if (page.html && Date.now() - page.at < PAGE_TTL_MS) return page.html;
  try {
    const r = await fetch(PAGE_URL);
    if (!r.ok) throw new Error(`http ${r.status}`);
    page = { html: await r.text(), at: Date.now() };
  } catch (e) {
    console.error("page fetch failed", e);
    if (!page.html) throw e;
  }
  return page.html;
}

const TYPES = ["Исполнитель", "Предприниматель", "Руководитель", "Творец"];
const USERNAME_RE = /^@?([A-Za-z][A-Za-z0-9_]{3,31})$/;

function clean(v: unknown, limit: number): string {
  return String(v ?? "").trim().slice(0, limit);
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

const RATE_LIMIT = 5;
const RATE_WINDOW_MS = 10 * 60 * 1000;
const hits = new Map<string, number[]>();

function rateLimited(ip: string): boolean {
  const now = Date.now();
  const arr = (hits.get(ip) ?? []).filter((t) => now - t < RATE_WINDOW_MS);
  if (arr.length >= RATE_LIMIT) {
    hits.set(ip, arr);
    return true;
  }
  arr.push(now);
  hits.set(ip, arr);
  return false;
}

// Контакт человека: ник в Telegram и/или номер телефона (хотя бы что-то одно)
type Person = { name: string; contact: string; phone: string };

function readPerson(data: any): Person | null {
  const person = {
    name: clean(data?.name, 80),
    contact: clean(data?.contact, 80),
    phone: clean(data?.phone, 40),
  };
  const hasContact = person.contact.length >= 3 || person.phone.replace(/\D/g, "").length >= 5;
  return person.name && hasContact ? person : null;
}

function personLines(p: Person): string {
  return (
    `<b>Имя:</b> ${escapeHtml(p.name)}\n` +
    (p.contact ? `<b>Телеграм:</b> ${escapeHtml(p.contact)}\n` : "") +
    (p.phone ? `<b>Телефон:</b> ${escapeHtml(p.phone)}\n` : "")
  );
}

// Кнопка «Написать»: по нику, а если его нет — по номеру в международном формате
function writeUrl(p: Person): string | null {
  const m = USERNAME_RE.exec(p.contact);
  if (m) return `https://t.me/${m[1]}`;
  const digits = p.phone.replace(/\D/g, "");
  if (p.phone.startsWith("+") && digits.length >= 10) return `https://t.me/+${digits}`;
  return null;
}

async function sendToOwner(text: string, person: Person): Promise<boolean> {
  const payload: any = {
    chat_id: Bun.env.OWNER_CHAT_ID,
    text,
    parse_mode: "HTML",
    disable_web_page_preview: true,
  };
  const url = writeUrl(person);
  if (url) {
    payload.reply_markup = {
      inline_keyboard: [[{ text: "Написать", url }]],
    };
  }
  try {
    const r = await fetch(`https://api.telegram.org/bot${Bun.env.BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!r.ok) {
      console.error("telegram sendMessage failed", r.status, await r.text());
      return false;
    }
    return true;
  } catch (e) {
    console.error("telegram sendMessage error", e);
    return false;
  }
}

function validPair(v: unknown): number[] | null {
  const pair = Array.isArray(v) ? v.map(Number) : [];
  const ok =
    pair.length === 2 &&
    pair.every((t) => Number.isInteger(t) && t >= 0 && t < 4) &&
    pair[0] !== pair[1];
  return ok ? pair : null;
}

const app = new Hono();

app.get("/", async (c) => {
  try {
    return c.html(await getPage());
  } catch {
    return c.text("Тест временно недоступен, попробуйте через минуту", 503);
  }
});

app.post("/api/result", async (c) => {
  let data: any;
  try {
    data = await c.req.json();
  } catch {
    return c.json({ ok: false, error: "bad_request" }, 400);
  }

  if (data?.website) {
    return c.json({ ok: true });
  }

  const person = readPerson(data);
  const pair = validPair(data?.pair);
  const scores = Array.isArray(data?.scores) ? data.scores.map(Number) : [];
  const valid =
    pair !== null &&
    person !== null &&
    scores.length === 4 &&
    scores.every((v: number) => Number.isFinite(v) && v >= 0 && v <= 10);
  if (!valid) {
    return c.json({ ok: false, error: "bad_request" }, 400);
  }

  const ip = c.req.header("x-forwarded-for")?.split(",")[0]?.trim() ?? "?";
  if (rateLimited(ip)) {
    return c.json({ ok: false, error: "too_many" }, 429);
  }

  const breakdown = [0, 1, 2, 3]
    .sort((a, b) => scores[b] - scores[a])
    .map((t) => `${t + 1} · ${TYPES[t]}: ${scores[t]}`)
    .join("\n");
  const tiebreak = Number(data?.tiebreak) > 0 ? `\n\nДоп. вопросов при ничьей: ${Number(data.tiebreak)}` : "";

  const text =
    "🧪 <b>Тест на сайте пройден</b>\n\n" +
    personLines(person!) +
    "\n" +
    `<b>Результат:</b> ${TYPES[pair![0]]} + ${TYPES[pair![1]]}\n\n` +
    `<b>Баллы (из 10):</b>\n${breakdown}` +
    tiebreak;

  if (!(await sendToOwner(text, person!))) {
    return c.json({ ok: false, error: "telegram" }, 502);
  }

  return c.json({ ok: true });
});

app.post("/api/lead", async (c) => {
  let data: any;
  try {
    data = await c.req.json();
  } catch {
    return c.json({ ok: false, error: "bad_request" }, 400);
  }

  if (data?.website) {
    return c.json({ ok: true });
  }

  const person = readPerson(data);
  const pair = validPair(data?.pair);
  if (!pair || !person) {
    return c.json({ ok: false, error: "bad_request" }, 400);
  }

  const ip = c.req.header("x-forwarded-for")?.split(",")[0]?.trim() ?? "?";
  if (rateLimited(ip)) {
    return c.json({ ok: false, error: "too_many" }, 429);
  }

  const text =
    "🆕 <b>Заявка на диагностику с теста</b>\n\n" +
    personLines(person) +
    `<b>Результат теста:</b> ${TYPES[pair[0]]} + ${TYPES[pair[1]]}`;

  if (!(await sendToOwner(text, person))) {
    return c.json({ ok: false, error: "telegram" }, 502);
  }
  return c.json({ ok: true });
});

export default {
  port: Bun.env.PORT,
  fetch: app.fetch,
};
