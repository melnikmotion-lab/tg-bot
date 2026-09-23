import { Hono } from "hono";

const app = new Hono();

const HTML = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ПриродоВед: дело, ради которого ты живёшь</title>
<meta name="description" content="Найдём точное направление вашей реализации за 60 дней.">
<meta name="theme-color" content="#FDA408">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Onest:wght@400;500;600&family=Unbounded:wght@600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --orange: #FDA408;
    --yellow: #FFC90D;
    --ink: #000;
    --muted: #3d3d3d;
    --paper: #fff;
    --error: #b00020;
    --display: "Unbounded", "Arial Rounded MT Bold", "Trebuchet MS", system-ui, sans-serif;
    --text: "Onest", system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0;
    background: var(--paper);
    color: var(--ink);
    font: 400 1.125rem/1.6 var(--text);
    -webkit-text-size-adjust: 100%;
  }
  .wrap { max-width: 760px; margin: 0 auto; padding: 0 20px; }
  .wrap.wide { max-width: 1000px; }
  img { display: block; max-width: 100%; height: auto; }
  a { color: inherit; }

  h1, h2, h3 { font-family: var(--display); letter-spacing: -0.01em; margin: 0; }
  h1 { font-weight: 800; font-size: clamp(2.2rem, 9vw, 4rem); line-height: 1.05; }
  h2 { font-weight: 800; font-size: clamp(1.35rem, 3.6vw, 1.9rem); line-height: 1.15; }
  h3 { font-weight: 600; font-size: 1.15rem; line-height: 1.25; }
  p { margin: 0 0 1em; max-width: 62ch; }

  /* buttons */
  .btn {
    display: inline-block;
    font: 600 1.05rem/1 var(--text);
    padding: 1.05em 1.7em;
    border: 3px solid var(--ink);
    border-radius: 999px;
    background: var(--orange);
    color: var(--ink);
    text-decoration: none;
    cursor: pointer;
    transition: transform .2s ease, background-color .2s ease;
  }
  .btn:hover { background: var(--yellow); }
  .btn.dark { background: var(--ink); color: #fff; }
  .btn.dark:hover { background: #222; }
  .btn:disabled { opacity: .6; cursor: default; }
  @media (hover: hover) { .btn:not(:disabled):hover { transform: scale(1.04); } }
  :focus-visible { outline: 3px solid var(--ink); outline-offset: 3px; }

  /* hero */
  .hero { padding-top: 12px; }
  .hero img { width: 100%; }
  .hero h1 { margin-top: 12px; }
  .hero .lead { margin: 22px 0 28px; font-style: italic; color: var(--muted); }

  section { padding: 60px 0 0; }
  section h2 { margin-bottom: 20px; }
  section > .wrap > p:last-child { margin-bottom: 0; }

  /* elements of understanding */
  dl.elements { margin: 0 0 1em; display: grid; gap: 14px; max-width: 62ch; }
  dl.elements dt { font-weight: 600; }
  dl.elements dd { margin: 2px 0 0; color: var(--muted); }
  .accent { font-weight: 700; font-style: italic; }

  .card {
    display: flex;
    flex-direction: column;
    background: #fff;
    border: 3px solid var(--ink);
    border-radius: 40px;
    padding: 32px 28px;
    transition: background-color .25s ease, transform .25s ease;
  }
  @media (hover: hover) {
    .card:hover { background: var(--orange); transform: scale(1.015); }
  }
  .card:has(:focus-visible) { background: var(--orange); }
  .card h3 { font: 800 1.6rem/1.1 var(--display); letter-spacing: -0.01em; margin: 0 0 10px; }
  .card .tagline { margin: 0 0 22px; font-weight: 600; }
  .card dl { margin: 0 0 22px; }
  .card dl > div { margin-bottom: 14px; }
  .card dt { font-size: .95rem; font-weight: 500; color: #2a2a2a; }
  .card dd { margin: 2px 0 0; }
  .card dd ul { margin: 4px 0 0; padding-left: 1.15em; }
  .card dd li { margin-bottom: .4em; }
  .card .btn { margin-top: auto; align-self: flex-start; }
  /* touch screens: orange pours in from the bottom as the card scrolls up */
  @media (hover: none) {
    .card { position: relative; overflow: hidden; isolation: isolate; }
    .card::before {
      content: "";
      position: absolute;
      inset: 0;
      background: var(--orange);
      transform-origin: bottom;
      transform: scaleY(0);
      transition: transform 1s cubic-bezier(.45, 0, .55, 1);
      z-index: -1;
    }
    .card.filled::before { transform: scaleY(1); }
  }

  /* reviews */
  .reviews figure { margin: 0 0 20px; }
  .reviews img { border-radius: 24px; width: 100%; max-width: 661px; }

  /* form */
  .apply { padding-bottom: 72px; }
  .apply h2 { margin-bottom: 10px; }
  .apply .sub { color: var(--muted); margin-bottom: 28px; }
  form { max-width: 560px; scroll-margin-top: 24px; }
  .field { margin-bottom: 22px; }
  label { display: block; font-weight: 600; margin-bottom: 8px; padding: 0; }
  .opt { font-weight: 400; color: var(--muted); }
  input[type=text], textarea {
    width: 100%;
    font: 400 1.05rem/1.4 var(--text);
    color: var(--ink);
    padding: .85em 1em;
    border: 3px solid var(--ink);
    border-radius: 18px;
    background: #fff;
  }
  textarea { min-height: 120px; resize: vertical; }
  input[aria-invalid=true], textarea[aria-invalid=true] { border-color: var(--error); }
  .err { color: var(--error); font-size: .95rem; margin: 6px 0 0; min-height: 1.2em; }
  .hp { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
  .privacy { font-size: .95rem; color: var(--muted); margin: 14px 0 0; }
  #formError { margin-top: 16px; color: var(--error); font-weight: 500; }
  #formError a { font-weight: 600; }
  .done { background: var(--orange); border-radius: 40px; padding: 32px 28px; max-width: 560px; scroll-margin-top: 24px; }
  .done h3 { font: 800 1.5rem/1.2 var(--display); margin: 0 0 10px; }
  .done p { margin: 0; }

  footer { border-top: 3px solid var(--ink); padding: 24px 0 40px; font-size: 1rem; }
  footer .wrap { display: flex; flex-wrap: wrap; gap: 8px 24px; justify-content: space-between; }

  @media (max-width: 520px) {
    .card { padding: 26px 20px; border-radius: 32px; }
  }
  @media (prefers-reduced-motion: reduce) {
    html { scroll-behavior: auto; }
    .btn, .card, .card::before { transition: none; }
    .btn:hover, .card:hover { transform: none !important; }
  }

  /* page text */
  .hero .tagline { font: 600 clamp(1.15rem, 3.4vw, 1.4rem)/1.35 var(--display); margin: 16px 0 0; max-width: 30ch; }
  .skip { font-size: 1rem; color: var(--muted); margin: 18px 0 0; }
  .skip a { font-weight: 600; }
  main h3 { margin: 28px 0 10px; }
  main ul { margin: 0 0 1em; padding-left: 1.2em; max-width: 62ch; }
  main li { margin-bottom: .45em; }
  .callout { background: var(--orange); border: 3px solid var(--ink); border-radius: 28px; padding: 22px 24px; font-weight: 600; max-width: 62ch; }
  .callout p { margin: 0; }
  .steps { list-style: none; padding: 0; display: grid; gap: 14px; }
  .steps li { margin: 0; }
  .steps b { font-family: var(--display); }
</style>
</head>
<body>

<header class="hero">
  <div class="wrap">
    <img src="https://raw.githubusercontent.com/melnikmotion-lab/tg-bot/claude/shared-link-access-95iimd/landing/logo.png" width="1280" height="720" alt="ПриродоВед: улыбающийся человек, нарисованный от руки">
    <h1>Дело, ради которого ты живёшь</h1>
    <p class="tagline">Найдём точное направление вашей реализации за 60 дней</p>
    <p class="lead">Для тех, кто не удовлетворён своей работой, находится в поиске новой деятельности и способа себя реализовать. И особенно для тех, кому 30+, а вы так и не поняли, кем хотите стать, когда вырастете.</p>
    <p class="skip">Ниже будет предложение о совместной работе, поэтому можно <a href="#offer">перелистнуть вниз</a> в любой момент.</p>
  </div>
</header>

<main>
  <section>
    <div class="wrap">
      <div class="callout"><p>💡 В этом месяце я возьму 5 человек в работу, которым помогу перестать играть в угадайку с выбором своей деятельности и понять, кто вы и чем вам заниматься в жизни.</p></div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <h2>В течение следующих 60 дней…</h2>
      <p>Мы наведём порядок в трёх ключевых сферах вашей жизни, чтобы вы поняли, кто вы, нашли свой способ реализации и смогли выстроить жизнь, о которой вы мечтаете. Это не очередные умные лекции, а возможность изменить вашу жизнь.</p>
    </div>
  </section>

  <section>
    <div class="wrap">
      <h2>1. Уберём страх выбрать не то дело</h2>
      <p>Хотите сменить деятельность или начать что-то новое — но страшно. Страшно, потому что это уже не первый раз: мечтали, горели, занимались этим и снова разочаровывались, оказываясь в той же самой начальной точке, где опять приходится выбирать. И с каждым разом этот страх выбора парализует всё сильнее.</p>
      <p>Наша цель — раз и навсегда определить, что конкретно вам подходит, чтобы больше не гадать и не бояться очередной ошибки. И это станет возможным, когда вы узнаете свои врождённые склонности и таланты — и это станет вашим преимуществом, которым многие не пользуются просто потому, что не понимают свою природу. А когда знаешь, то каждое решение, каждый шаг становится уверенным.</p>
      <p>Если вы не понимаете природу своей личности и её самые сильные стороны, то даже смена работы, покупка курса «Как быстро заработать на ИИ в 2026 году без вложений» или новая мотивационная книга не принесут ничего, кроме временного облегчения и нового витка поисков.</p>
      <p>Поэтому в первую очередь мы проведём личную диагностику 1-1, на которой:</p>
      <ul>
        <li>определим вашу индивидуальную природу и разберём, что вам мешает жить в согласии с ней;</li>
        <li>вы поймёте, что вами по-настоящему движет и чего вы хотите на самом деле;</li>
        <li>и увидите, где вы годами боролись не с той причиной: списывая на лень, характер или «не повезло с работой».</li>
      </ul>
    </div>
  </section>

  <section>
    <div class="wrap">
      <h2>2. Найдём ваше место и дело</h2>
      <p>Любая реализация стоит на трёх вещах — природа, деятельность и среда, в которой вы действуете. Когда мы знаем вашу природу — мы соединяем её с деятельностью и находим не абстрактное «дело жизни», а то, где ваши сильные стороны работают без сопротивления. Мы разберём:</p>
      <ul>
        <li>какие ваши качества и склонности сейчас не находят применения и где им действительно место;</li>
        <li>в какой сфере или формате деятельности вы максимально раскрываетесь;</li>
        <li>как использовать то, что у вас уже есть, вместо того чтобы искать что-то принципиально новое.</li>
      </ul>
      <p>Самое прекрасное во всём этом, что у вас уже есть опыт, качества и склонности, которые нужно просто направить в нужную сторону, а не придумывать с нуля.</p>
      <p>Мы не придумываем вам новое занятие. У вас уже есть врождённые качества и таланты — что-то уже раскрыто, что-то наработано опытом. Мы собираем это вместе и направляем туда, где вы раскроетесь сильнее всего.</p>
    </div>
  </section>

  <section>
    <div class="wrap">
      <h2>3. Выстроим фундамент, на который можно опираться всегда</h2>
      <p>Знать свою природу и найти дело — это половина пути. Вторая половина — не растерять это при первой же трудности, не откатиться обратно в старое и привычное мышление.</p>
      <p>Именно поэтому нужно не разовое понимание себя, а фундамент — состояние, из которого вы действуете постоянно, что бы ни происходило вокруг. Такое состояние — ваша опора на всю жизнь. Состояние, управляемое вашим пониманием себя, а не тревогой и сомнениями. Когда вы точно знаете, кто вы. А не пытаетесь в очередной раз угадать, кем стать.</p>
      <p>Состояние складывается из нескольких элементов:</p>
      <ul>
        <li>понимание своей природы — врождённых качеств и склонностей, через которые вы действуете;</li>
        <li>убеждения о себе, через которые вы оцениваете свои решения и возможности;</li>
        <li>привычные способы реагировать на трудности и неудачи.</li>
      </ul>
      <p>Влияя на эти элементы, мы меняем состояние, качество решений и результаты, которые вы получаете в жизни. Цель этой фазы — научиться легко возвращаться в правильное состояние, в котором вы не зависите от обстоятельств. Чтобы вы могли спокойно принимать решения, оставаться собой и жить в удовольствие, даже когда происходит что-то трудное.</p>
    </div>
  </section>

  <section id="offer">
    <div class="wrap">
      <article class="card">
        <h3>Стоимость</h3>
        <p>Полная стоимость работы со мной — $800. Я понимаю, что платить всю сумму сразу, не понимая, как пойдёт, — так себе идея. Поэтому можно неделями.</p>
        <p>Вы платите $100 в неделю и получаете:</p>
        <ul>
          <li>личную диагностику 1-1 — определим вашу индивидуальную природу;</li>
          <li>разбор, что мешает вам жить в согласии с ней;</li>
          <li>план реализации — найдём ваше место и дело;</li>
          <li>работу над состоянием, из которого действовать;</li>
          <li>доступ ко мне в личном чате.</li>
        </ul>
        <p>А дальше уже будете решать — подходит вам наше сотрудничество или нет. Стартуем сразу после оплаты.</p>
        <a class="btn dark" href="#leadForm">Хочу в работу</a>
      </article>
    </div>
  </section>

  <section>
    <div class="wrap">
      <h2>Время до получения результатов</h2>
      <p>Через 60 дней с начала работы у вас будет:</p>
      <ul>
        <li>чёткое понимание своей индивидуальной природы, которое уберёт страх начинать новое раз и навсегда;</li>
        <li>конкретная сфера или формат деятельности, в которых вы раскрываетесь сильнее всего;</li>
        <li>рабочий способ за минуты возвращаться в состояние, в котором вы способны достигать целей, а не реагировать по привычке, теряя способность трезво мыслить.</li>
      </ul>
    </div>
  </section>

  <section>
    <div class="wrap">
      <h2>В двух словах</h2>
      <ol class="steps">
        <li><b>Шаг 1.</b> Уберём страх выбора — узнав свои врождённые склонности и таланты, выбор деятельности перестанет быть лотереей.</li>
        <li><b>Шаг 2.</b> Найдём ваше место и дело — соединим врождённый талант и приобретённые способности с делом, где вы раскроетесь на максимум.</li>
        <li><b>Шаг 3.</b> Выстроим фундамент — научимся легко возвращаться в состояние, в котором вы способны действовать и принимать решения в моменты кризиса.</li>
      </ol>
    </div>
  </section>

  <section class="reviews">
    <div class="wrap">
      <h2>Отзывы</h2>
      <figure><img src="https://raw.githubusercontent.com/melnikmotion-lab/tg-bot/claude/shared-link-access-95iimd/landing/rev1.png" width="661" height="573" alt="Отзыв в Телеграме: после одной сессии появилась ясность в своей природе, а за несколько недель пришли результаты, о которых человек мечтал годами" loading="lazy"></figure>
      <figure><img src="https://raw.githubusercontent.com/melnikmotion-lab/tg-bot/claude/shared-link-access-95iimd/landing/rev2.png" width="616" height="365" alt="Отзыв в Телеграме: подтвердились догадки о своей природе, ушло ощущение самозванца, вопросы были разносторонними и логичными" loading="lazy"></figure>
    </div>
  </section>

  <section class="apply" id="apply">
    <div class="wrap">
      <h2>Как присоединиться?</h2>
      <p class="sub">Оставьте заявку или <a href="https://t.me/Alexey_melnik?text=%D0%94%D0%B5%D0%BB%D0%BE" target="_blank" rel="noopener">напишите мне в Телеграме «Дело»</a>, и я расскажу подробнее все детали.</p>

      <form id="leadForm" novalidate>
        <div class="field">
          <label for="name">Как вас зовут</label>
          <input type="text" id="name" name="name" autocomplete="given-name" maxlength="80" required>
          <p class="err" id="nameErr" aria-live="polite"></p>
        </div>

        <div class="field">
          <label for="contact">Ваш Телеграм</label>
          <input type="text" id="contact" name="contact" placeholder="@ник или номер телефона" autocomplete="off" maxlength="80" required>
          <p class="err" id="contactErr" aria-live="polite"></p>
        </div>

        <div class="field">
          <label for="message">Что сейчас беспокоит <span class="opt">(по желанию)</span></label>
          <textarea id="message" name="message" maxlength="1500"></textarea>
        </div>

        <div class="hp" aria-hidden="true">
          <label for="website">Не заполняйте это поле</label>
          <input type="text" id="website" name="website" tabindex="-1" autocomplete="off">
        </div>

        <button class="btn" type="submit" id="submitBtn">Отправить заявку</button>
        <p class="privacy">Контакты нужны только для того, чтобы вам написать.</p>
        <div id="formError" role="alert"></div>
      </form>

      <div class="done" id="done" hidden tabindex="-1">
        <h3>Заявка отправлена</h3>
        <p>Скоро напишу вам в Телеграме.</p>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="wrap">
    <span>ПриродоВед</span>
    <a href="https://t.me/Prirodo_ved" target="_blank" rel="noopener">Телеграм-канал @Prirodo_ved</a>
  </div>
</footer>

<script>
  var ENDPOINT = "/api/lead";
  var TG_USER  = "Alexey_melnik";
  var TG_TEXT  = "Дело";

  var form = document.getElementById("leadForm");
  var done = document.getElementById("done");
  var btn = document.getElementById("submitBtn");
  var formError = document.getElementById("formError");
  var nameEl = document.getElementById("name");
  var contactEl = document.getElementById("contact");

  if (window.matchMedia && window.matchMedia("(hover: none)").matches && "IntersectionObserver" in window) {
    var fillObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        e.target.classList.toggle("filled", e.isIntersecting || e.boundingClientRect.top < 0);
      });
    }, { rootMargin: "0px 0px -35% 0px" });
    document.querySelectorAll(".card").forEach(function (c) { fillObserver.observe(c); });
  }

  function setErr(input, errId, msg) {
    document.getElementById(errId).textContent = msg;
    if (msg) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
  }

  function showFallback() {
    var html = "Не получилось отправить заявку. Попробуйте ещё раз";
    if (TG_USER) {
      var href = "https://t.me/" + encodeURIComponent(TG_USER) + "?text=" + encodeURIComponent(TG_TEXT);
      html += " или <a href=\\"" + href + "\\" target=\\"_blank\\" rel=\\"noopener\\">напишите мне в Телеграме</a>";
    }
    formError.innerHTML = html + ".";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    formError.textContent = "";

    var name = nameEl.value.trim();
    var contact = contactEl.value.trim();
    var ok = true;

    setErr(nameEl, "nameErr", name ? "" : "Напишите, как к вам обращаться");
    if (!name) ok = false;
    setErr(contactEl, "contactErr", contact.length >= 3 ? "" : "Укажите ник в Телеграме или номер телефона");
    if (contact.length < 3) ok = false;
    if (!ok) { (name ? contactEl : nameEl).focus(); return; }

    btn.disabled = true;
    btn.textContent = "Отправляю…";

    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, 12000);

    fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        contact: contact,
        message: form.elements.message.value.trim(),
        website: form.elements.website.value
      }),
      signal: ctrl.signal
    }).then(function (r) {
      if (!r.ok) throw new Error("http " + r.status);
      form.hidden = true;
      done.hidden = false;
      done.focus();
    }).catch(function () {
      showFallback();
    }).finally(function () {
      clearTimeout(timer);
      btn.disabled = false;
      btn.textContent = "Отправить заявку";
    });
  });
</script>
</body>
</html>
`;

const SERVICE = "Сопровождение";
const USERNAME_RE = /^@?([A-Za-z][A-Za-z0-9_]{4,31})$/;

const RATE_LIMIT = 3;
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

function clean(v: unknown, limit: number): string {
  return String(v ?? "").trim().slice(0, limit);
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

app.get("/", (c) => c.html(HTML));

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

  const name = clean(data?.name, 80);
  const contact = clean(data?.contact, 80);
  const message = clean(data?.message, 1500);

  if (!name || contact.length < 3) {
    return c.json({ ok: false, error: "bad_request" }, 400);
  }

  const ip = c.req.header("x-forwarded-for")?.split(",")[0]?.trim() ?? "?";
  if (rateLimited(ip)) {
    return c.json({ ok: false, error: "too_many" }, 429);
  }

  let text =
    "🆕 <b>Новая заявка с сайта</b>\n\n" +
    `<b>Имя:</b> ${escapeHtml(name)}\n` +
    `<b>Телеграм:</b> ${escapeHtml(contact)}\n` +
    `<b>Интересует:</b> ${SERVICE}`;
  if (message) {
    text += `\n\n<b>Что беспокоит:</b>\n${escapeHtml(message)}`;
  }

  const payload: any = {
    chat_id: Bun.env.OWNER_CHAT_ID,
    text,
    parse_mode: "HTML",
    disable_web_page_preview: true,
  };
  const m = USERNAME_RE.exec(contact);
  if (m) {
    payload.reply_markup = {
      inline_keyboard: [[{ text: "Написать", url: `https://t.me/${m[1]}` }]],
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
      return c.json({ ok: false, error: "telegram" }, 502);
    }
  } catch (e) {
    console.error("telegram sendMessage error", e);
    return c.json({ ok: false, error: "telegram" }, 502);
  }

  return c.json({ ok: true });
});

export default {
  port: Bun.env.PORT,
  fetch: app.fetch,
};

