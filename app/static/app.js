// TouchStone: chat client. Talks only to this server's /api (session cookie auth).
"use strict";

const $ = (id) => document.getElementById(id);
const { esc, icon } = UI;

// source_system -> [icon, display name]; policies are recognised by their POL- id.
const SYS = { confluence: ["book", "Confluence"], servicenow: ["ticket", "ServiceNow"], outlook: ["mail", "Email"], slack: ["hash", "Slack"] };
const sourceOf = (system, id, type) =>
  (type === "policy" || /^POL-/i.test(id || "")) ? ["policy", "Policy"] : (SYS[system] || ["book", system]);
const FLAG = { out_of_date: ["amber", "policy differs from practice"], conflict: ["red", "conflicting past answers"],
               withheld: ["violet", "some records withheld"] };
// Thinking steps, advanced by elapsed time while the real request runs (answers take ~15-25 s).
const STEPS = [
  [0, "Checking your access", "Your roles decide which records are searched"],
  [3, "Searching policies and Confluence", "The written rules"],
  [7, "Reading tickets, email and Slack", "What actually happened"],
  [11, "Comparing policy, practice and past answers", "Looking for gaps and disagreements"],
  [15, "Finding who to ask", "Skipping anyone who has left"],
];
const EXAMPLES = ["How do I get access to Salesforce?", "How long does a replacement laptop take?",
                  "Are we allowed to deploy to production on a Friday?", "What is the deadline for submitting expense claims?"];

let chatId = null;  // the open conversation; null = a new chat that hasn't been asked yet
let chats = [];
let busy = false;
let drawerOpener = null;

const roleLabel = (r) => { const s = r.replaceAll("_", " "); return s[0].toUpperCase() + s.slice(1); };
const initials = (name) => name.split(/\s+/).map((w) => w[0]).slice(0, 2).join("").toUpperCase();
const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;

// ------------------------------------------------------------------ boot
async function boot() {
  $("logo-mark").innerHTML = icon("logo", "ic lg");
  $("close-nav").innerHTML = icon("x", "ic lg");
  $("nav-toggle").innerHTML = icon("menu", "ic lg");
  $("new-chat").innerHTML = `${icon("plus")}New chat`;
  $("signout").innerHTML = `${icon("out")}Sign out`;
  $("ask").innerHTML = `${icon("up")}<span class="ask-label">Ask</span>`;
  $("ask").setAttribute("aria-label", "Ask");
  $("d-close").innerHTML = icon("x", "ic lg");
  $("d-copy").innerHTML = `${icon("copy")}Copy reference`;
  $("hint-lock").insertAdjacentHTML("afterbegin", icon("lock"));
  $("srcs").innerHTML = `Searching ${["policy", "book", "ticket", "mail", "hash"].map((i) => icon(i)).join("")}`;
  $("srcs").setAttribute("aria-label", "Searching policies, Confluence, ServiceNow, email and Slack");
  document.querySelectorAll("[data-theme-toggle]").forEach((b) => { b.innerHTML = UI.themeButtonInner(); });
  UI.syncToggles();
  $("empty-bot").innerHTML = UI.bot();
  $("suggest").innerHTML = EXAMPLES.map((q) => `<button type="button" data-ask="${esc(q)}">${esc(q)}</button>`).join("");

  const r = await fetch("/api/me");
  if (r.status === 401) { location.replace("/login.html"); return; }
  renderMe(await r.json());
  loadChats();
}

function renderMe(u) {
  $("me-avatar").textContent = initials(u.name);
  $("me-name").textContent = u.name;
  $("me-title").textContent = `${u.title} · ${u.department}`;
  $("me-roles").innerHTML = u.roles.map((r) => `<span class="role">${esc(roleLabel(r))}</span>`).join("");
  const { confidential_visible: v, confidential_total: t } = u.scope;
  const pct = t ? (100 * v / t) : 0;
  $("me-scope").innerHTML = `<span>Confidential records you can see: <b>${v} of ${t}</b></span>` +
    `<div class="meter" role="img" aria-label="${v} of ${t} confidential records"><i style="width:${pct.toFixed(1)}%"></i></div>` +
    (u.hrbp_departments.length ? `<span>HR partner for: ${esc(u.hrbp_departments.join(", "))}</span>` : "");
  $("me-grants").innerHTML = u.role_details.map((r) => `<li><b>${esc(roleLabel(r.role))}</b>: ${esc(r.grants)}</li>`).join("");
}

// ------------------------------------------------------------------ chats (sidebar)
function dayGroup(iso) {
  const d = new Date(iso), now = new Date();
  const days = Math.round((new Date(now.toDateString()) - new Date(d.toDateString())) / 86400000);
  return days <= 0 ? "Today" : days === 1 ? "Yesterday" : "Earlier";
}
function when(iso) {
  const d = new Date(iso);
  return dayGroup(iso) === "Earlier" ? d.toLocaleDateString(undefined, { day: "numeric", month: "short" })
                                     : d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

async function loadChats() {
  const r = await fetch("/api/chats");
  if (!r.ok) return;
  chats = await r.json();
  $("chats-empty").hidden = chats.length > 0;
  $("clear-history").hidden = chats.length === 0;
  let group = null, html = "";
  for (const c of chats) {
    const g = dayGroup(c.updated_at);
    if (g !== group) { html += `<li class="grp" aria-hidden="true">${g}</li>`; group = g; }
    const flags = (c.flags || []).filter((f) => FLAG[f]);
    const current = c.chat_id === chatId;
    html += `<li class="chat-row"><button type="button" class="chat-item" data-chat="${esc(c.chat_id)}"${current ? ' aria-current="true"' : ""}>` +
      `<span class="t">${esc(c.title)}</span><span class="m">${esc(when(c.updated_at))} · ${plural(c.turn_count || 0, "question")}` +
      (flags.length ? `<span class="flags">${flags.map((f) => `<i class="dot ${FLAG[f][0]}"></i>`).join("")}</span>` +
                      `<span class="sr">Flags: ${flags.map((f) => FLAG[f][1]).join(", ")}</span>` : "") +
      `</span></button><button type="button" class="del" data-del="${esc(c.chat_id)}" aria-label="Delete chat: ${esc(c.title)}">${icon("trash")}</button></li>`;
  }
  $("chat-list").innerHTML = html;
  updateHeader();
}

function updateHeader() {
  const c = chats.find((x) => x.chat_id === chatId);
  $("chat-title").textContent = c ? c.title : "New chat";
  $("chat-count").textContent = c ? `${plural(c.turn_count || 0, "question")} ·` : "";
  document.title = c ? `${c.title} · TouchStone` : "TouchStone";
}

function clearThread() {
  [...$("thread-inner").children].forEach((c) => { if (c.id !== "empty") c.remove(); });
}

function newChat() {
  if (busy) return;
  chatId = null;
  clearThread();
  $("empty").hidden = false;
  closeNav();
  loadChats();
  $("q").focus();
}

async function openChat(id) {
  if (busy) return;
  const r = await fetch(`/api/chats/${encodeURIComponent(id)}`);
  if (r.status === 401) { location.replace("/login.html"); return; }
  if (!r.ok) { loadChats(); return; }
  const chat = await r.json();
  chatId = chat.chat_id;
  clearThread();
  $("empty").hidden = true;
  for (const t of chat.turns) {
    addUser(t.question);
    if (t.response) {
      addCard(renderAnswer(t.response), "card answer-card", "Answer");
    } else {  // stored answer not shown: the user's access changed since it was given
      addCard(`<p class="note">This answer isn't shown because your access has changed since it was given.</p>` +
        `<button type="button" class="btn sm" data-reask="${esc(t.question)}">Ask again</button>`, "card hidden-answer");
    }
  }
  closeNav();
  loadChats();
  scrollDown();
}

async function deleteChat(id) {
  await fetch(`/api/chats/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (id === chatId) newChat(); else loadChats();
}

// ------------------------------------------------------------------ phone side panel
function openNav() {
  $("app").classList.add("nav-open"); $("scrim").hidden = false; $("nav-toggle").setAttribute("aria-expanded", "true");
  $("close-nav").focus();
}
function closeNav() {
  if (!$("app").classList.contains("nav-open")) return;
  $("app").classList.remove("nav-open"); $("scrim").hidden = true; $("nav-toggle").setAttribute("aria-expanded", "false");
}

// ------------------------------------------------------------------ markdown (escape first, then format)
function inline(s) {
  return s.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*]+)\*/g, "$1<em>$2</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[(\d+)\]/g, '<button type="button" class="cite" data-n="$1" aria-label="Open source $1">$1</button>');
}

function md(text) {
  const lines = esc(text).split("\n");
  let html = "", list = null, table = [];
  const closeList = () => { if (list) { html += `</${list}>`; list = null; } };
  const flushTable = () => {
    if (!table.length) return;
    const rows = table.filter((r) => !/^\s*\|?\s*:?-{3,}/.test(r)).map((r) => r.trim().replace(/^\||\|$/g, "").split("|"));
    html += `<div style="overflow-x:auto"><table class="md">` + rows.map((cells, i) =>
      `<tr>${cells.map((c) => `<${i ? "td" : "th"}>${inline(c.trim())}</${i ? "td" : "th"}>`).join("")}</tr>`).join("") + "</table></div>";
    table = [];
  };
  for (const raw of lines) {
    const l = raw.trimEnd();
    if (/^\s*\|.*\|\s*$/.test(l)) { closeList(); table.push(l); continue; }
    flushTable();
    let m;
    if ((m = l.match(/^#{1,4}\s+(.*)/))) { closeList(); html += `<h4>${inline(m[1])}</h4>`; }
    else if ((m = l.match(/^\s*[-*]\s+(.*)/))) { if (list !== "ul") { closeList(); html += "<ul>"; list = "ul"; } html += `<li>${inline(m[1])}</li>`; }
    else if ((m = l.match(/^\s*\d+\.\s+(.*)/))) { if (list !== "ol") { closeList(); html += "<ol>"; list = "ol"; } html += `<li>${inline(m[1])}</li>`; }
    else if (!l.trim()) { closeList(); }
    else { closeList(); html += `<p>${inline(l)}</p>`; }
  }
  flushTable(); closeList();
  return html;
}

// ------------------------------------------------------------------ rendering an answer
function statusChips(r) {
  const kinds = new Set(r.conflicts.map((c) => c.kind));
  const chips = [];
  if (kinds.has("policy_vs_practice") || kinds.has("source_vs_source") || r.staleness.length) chips.push(["amber", "scale", "Policy differs from practice"]);
  if (kinds.has("conflicting_resolutions")) chips.push(["red", "split", "Conflicting past answers"]);
  if (r.access_note) chips.push(["violet", "lock", "Some records withheld"]);
  if (r.meta && r.meta.confidence === "low") chips.push(["grey", "help", "Low confidence"]);
  if (!chips.some(([c]) => c !== "grey")) chips.unshift(["green", "check", "Sources agree"]);
  return `<div class="chips" aria-label="Answer status">${chips.map(([c, i, t]) => `<span class="chip ${c}">${icon(i)}${esc(t)}</span>`).join("")}</div>`;
}

function noteLines(r) {
  const NOTE = { policy_vs_practice: ["amber", "scale", "Policy vs practice:"], source_vs_source: ["amber", "scale", "Sources disagree:"],
                 conflicting_resolutions: ["red", "split", "Past answers disagree:"] };
  const notes = r.conflicts.map((c) => { const [cls, ic, head] = NOTE[c.kind] || NOTE.source_vs_source; return [cls, ic, head, c.summary]; });
  if (!r.conflicts.length) for (const s of r.staleness) notes.push(["amber", "clock", `${s.record_id} may be out of date:`, s.reason]);
  if (r.access_note) notes.push(["violet", "lock", "Records withheld:", r.access_note]);
  if (!notes.length) return "";
  return `<ul class="notes" aria-label="Why these flags">` + notes.map(([cls, ic, head, text]) =>
    `<li class="note-line ${cls}">${icon(ic)}<span><b>${esc(head)}</b> ${inline(esc(text))}</span></li>`).join("") + `</ul>`;
}

function contactBlock(f) {
  if (!f || !f.contact_name) return "";
  return `<section aria-label="Who to ask"><p class="label">Who to ask</p><div class="contact">` +
    `<span class="avatar teal" aria-hidden="true">${esc(initials(f.contact_name))}</span>` +
    `<div class="main-col"><div class="name">${esc(f.contact_name)}</div>` +
    (f.contact_role ? `<div class="role">${esc(f.contact_role)}</div>` : "") +
    (f.reason ? `<div class="why">${esc(f.reason)}</div>` : "") + `</div></div></section>`;
}

function referenceList(r) {
  if (!r.citations.length) return "";
  const stale = new Set(r.staleness.map((s) => s.record_id));
  return `<section aria-label="References"><p class="label">References</p><ol class="refs">` + r.citations.map((c) => {
    const [ic, sys] = sourceOf(c.source_system, c.record_id);
    const basis = c.access_basis ? roleLabel(c.access_basis) : "";
    const tags = (stale.has(c.record_id) ? `<span class="badge amber">${icon("clock")}May be out of date</span>` : "") +
      (c.confidential ? `<span class="badge violet" title="Confidential. You can see it because of: ${esc(basis)}">${icon("lock")}Confidential · ${esc(basis)}</span>` : "");
    const title = c.title.split(" — ")[0];
    return `<li><button type="button" class="ref" data-record="${esc(c.record_id)}" data-n="${c.n}" ` +
      `aria-label="Open source ${c.n}: ${esc(title)}${c.confidential ? ", confidential" : ""}">` +
      `<span class="n">${c.n}</span><span class="src" aria-hidden="true">${icon(ic)}</span>` +
      `<span class="main-col"><span class="t">${esc(title)}</span><span class="meta">${esc(sys)} · <span class="mono">${esc(c.record_id)}</span> · ${esc(c.date)}</span></span>` +
      (tags ? `<span class="tags">${tags}</span>` : "") + `${icon("right", "ic go")}</button></li>`;
  }).join("") + `</ol></section>`;
}

function renderAnswer(r) {
  const m = r.meta || {};
  const facts = [m.cached ? "cached answer" : (m.latency_s != null ? `answered in ${m.latency_s} s` : ""),
                 r.citations.length ? plural(r.citations.length, "source") : ""].filter(Boolean).join(" · ");
  let h = `<div class="who">${UI.mini()}<b>TouchStone</b><span>${esc(facts)}</span></div>` +
    statusChips(r) + `<div class="answer">${md(r.answer)}</div>` + noteLines(r) + contactBlock(r.fallback) + referenceList(r);
  if (r.trace.length) {
    h += `<div class="answer-foot"><details><summary>${icon("route")}How I found this <span class="sum">${plural(r.trace.length, "step")}</span>${icon("chev", "ic chev")}</summary>` +
      `<ol class="steps">` + r.trace.map((t) => {
        const args = Object.values(t.args || {}).map((v) => (typeof v === "string" ? v : JSON.stringify(v))).join(", ");
        return `<li><div><code>${esc(t.tool)}</code> ${esc(args)} <span>→ ${esc(t.summary)}</span></div></li>`;
      }).join("") + `</ol></details></div>`;
  }
  return h;
}

// ------------------------------------------------------------------ conversation
function scrollDown() { const t = $("thread"); t.scrollTop = t.scrollHeight; }

function addUser(q) {
  $("empty").hidden = true;
  const d = document.createElement("p");
  d.className = "msg-user"; d.textContent = q;
  $("thread-inner").appendChild(d);
}

function addCard(html, cls, label) {
  const d = document.createElement("article");
  d.className = cls;
  if (label) d.setAttribute("aria-label", label);
  d.innerHTML = html;
  $("thread-inner").appendChild(d);
  return d;
}

function addThinking() {
  const d = addCard(
    `<div class="bot-stage searching" aria-hidden="true">${UI.bot()}${UI.flyCards()}</div>` +
    `<div><p class="label" style="margin-bottom:12px">Working on it</p><ol class="think-steps">` +
    STEPS.map(([, t, s]) => `<li class="think-step"><span class="tick" aria-hidden="true">${icon("tick")}</span>` +
      `<span>${esc(t)}<small style="display:block;color:var(--muted);font-size:12.5px;font-weight:400">${esc(s)}</small></span></li>`).join("") +
    `</ol><div class="progress"><div class="meter"><i style="width:2%"></i></div><span class="t">0 s · usually 15–25 s</span></div>` +
    `<p class="sr" aria-live="polite"></p></div>`, "card think", "TouchStone is working");
  d.setAttribute("aria-busy", "true");
  const items = d.querySelectorAll(".think-step"), live = d.querySelector("[aria-live]");
  let shown = -1;
  const tick = () => {
    const s = (Date.now() - start) / 1000;
    const active = STEPS.reduce((a, [at], i) => (s >= at ? i : a), 0);
    items.forEach((li, i) => { li.className = "think-step" + (i < active ? " done" : i === active ? " active" : ""); });
    if (active !== shown) { live.textContent = STEPS[active][1]; shown = active; }
    d.querySelector(".meter > i").style.width = `${Math.min(95, 2 + s / 22 * 93).toFixed(1)}%`;
    d.querySelector(".t").textContent = `${Math.floor(s)} s · usually 15–25 s`;
  };
  const start = Date.now();
  tick();
  const timer = setInterval(tick, 500);
  return { el: d, stop: () => clearInterval(timer) };
}

async function ask(q) {
  q = q.trim();
  if (!q || busy) return;
  busy = true; $("ask").disabled = true;
  addUser(q);
  const pending = addThinking();
  scrollDown();
  try {
    const res = await fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" },
                                           body: JSON.stringify({ question: q, chat_id: chatId }) });
    if (res.status === 401) { location.replace("/login.html"); return; }
    const j = await res.json();
    if (!res.ok) throw new Error(j.detail || `Request failed (${res.status})`);
    chatId = j.chat_id || chatId;  // the first answer creates the chat; follow-ups stay in it
    pending.stop();
    pending.el.className = "card answer-card";
    pending.el.setAttribute("aria-label", "Answer");
    pending.el.removeAttribute("aria-busy");
    pending.el.innerHTML = renderAnswer(j);
    loadChats();
  } catch (e) {
    pending.stop();
    pending.el.className = "card err-card";
    pending.el.removeAttribute("aria-busy");
    pending.el.setAttribute("role", "alert");
    pending.el.innerHTML = `<span>Couldn't get an answer: ${esc(e.message)}</span><button type="button" class="btn sm" data-retry="${esc(q)}">Try again</button>`;
  } finally {
    busy = false; $("ask").disabled = false; scrollDown();
  }
}

// ------------------------------------------------------------------ source drawer
const refLink = (id) => `<button type="button" class="ref-link" data-record="${esc(id)}">${esc(id)}</button>`;
let drawerRecord = null;

async function openRecord(id, opener) {
  if ($("drawer-wrap").hidden) drawerOpener = opener || document.activeElement;
  drawerRecord = id;
  $("drawer-wrap").hidden = false;
  $("d-icon").innerHTML = icon("book", "ic lg");
  $("d-kind").textContent = "Loading…"; $("d-title").textContent = id; $("d-tags").innerHTML = ""; $("d-body").innerHTML = "";
  $("d-close").focus();
  const res = await fetch(`/api/records/${encodeURIComponent(id)}`);
  if (res.status === 401) { location.replace("/login.html"); return; }
  const r = await res.json();
  if (drawerRecord !== id) return;  // another record was opened meanwhile
  if (!res.ok) { $("d-kind").textContent = ""; $("d-body").innerHTML = `<p class="note">${esc(r.detail)}</p>`; return; }

  const [ic, sys] = sourceOf(r.source_system, r.record_id, r.source_type);
  const s = r.signals;
  $("d-icon").innerHTML = icon(ic, "ic lg");
  $("d-kind").innerHTML = `${esc(sys)} · <span class="mono">${esc(r.record_id)}</span>`;
  $("d-title").textContent = r.title;
  $("d-tags").innerHTML =
    (s.days_since_update > 365 ? `<span class="badge amber">${icon("clock")}${s.days_since_update} days old</span>` : "") +
    (r.confidential ? `<span class="badge violet">${icon("lock")}Confidential</span>` : `<span class="badge teal">Visible company-wide</span>`);

  const warn = [];
  if (r.confidential) {
    warn.push(["violet", "lock", "Confidential.", `${r.confidential_reason ? r.confidential_reason + ". " : ""}You can see it because of: ${roleLabel(r.access_basis || "")}. This view is logged.`]);
  }
  if (s.days_since_update > 365) warn.push(["amber", "clock", `Not updated in ${s.days_since_update} days.`, `Last updated ${r.last_updated}. Check that it still applies.`]);
  const left = (r.inactive_people || []);
  if (left.length) {
    const gone = left.every((p) => p.status === "exited");
    warn.push(["amber", "userx", gone ? "Names someone who has left." : "Names someone who isn't active.",
      left.map((p) => `${p.name} (${p.status === "exited" ? "has left" : p.status})`).join(", ") + ". Don't contact them about this."]);
  }
  const inactiveOwners = r.owners.filter((o) => !o.active);
  if (inactiveOwners.length) warn.push(["amber", "userx", "Owner no longer active.", inactiveOwners.map((o) => o.name).join(", ")]);
  if (s.open_update_request_ids.length) warn.push(["amber", "alert", "Update requested.", null, s.open_update_request_ids.map(refLink).join(" ")]);

  const meta = [["System", sys], ["Record", r.record_id], ["Status", r.status], ["Created", r.created_date],
                ["Last updated", r.last_updated],
                ["Owner", r.owners.map((o) => o.active ? esc(o.name) : `<s>${esc(o.name)}</s> · not active`).join(", "), true]]
    .filter(([, v]) => v);
  const body = ["policy", "confluence"].includes(r.source_type) ? `<div class="answer">${md(r.text)}</div>` : `<pre>${esc(r.text)}</pre>`;
  $("d-body").innerHTML =
    (warn.length ? `<ul class="notes" aria-label="Warnings about this record">` + warn.map(([cls, i, head, text, html]) =>
      `<li class="note-line ${cls}">${icon(i)}<span><b>${esc(head)}</b> ${html || esc(text)}</span></li>`).join("") + `</ul>` : "") +
    `<dl class="d-meta">${meta.map(([k, v, raw]) => `<div><dt>${k}</dt><dd>${raw ? v : esc(v)}</dd></div>`).join("")}</dl>` +
    `<div><p class="label">Record</p><div class="doc">${body}</div></div>`;
  $("d-body").scrollTop = 0;
}

function closeDrawer() {
  if ($("drawer-wrap").hidden) return false;
  $("drawer-wrap").hidden = true;
  drawerRecord = null;
  if (drawerOpener && document.contains(drawerOpener)) drawerOpener.focus();
  return true;
}

// Keep Tab inside the open drawer.
$("drawer").addEventListener("keydown", (e) => {
  if (e.key !== "Tab") return;
  const f = [...$("drawer").querySelectorAll("button, a[href], [tabindex]:not([tabindex='-1'])")].filter((x) => x.offsetParent);
  if (!f.length) return;
  if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
  else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
});

// ------------------------------------------------------------------ events
document.addEventListener("click", (e) => {
  const t = e.target.closest("button");
  if (!t) return;
  if (t.dataset.chat) openChat(t.dataset.chat);
  else if (t.dataset.del) deleteChat(t.dataset.del);
  else if (t.dataset.reask) ask(t.dataset.reask);
  else if (t.dataset.ask) ask(t.dataset.ask);
  else if (t.dataset.record) openRecord(t.dataset.record, t);
  else if (t.classList.contains("cite")) {
    const card = t.closest(".answer-card");
    const src = card && card.querySelector(`.ref[data-n="${t.dataset.n}"]`);
    if (src) openRecord(src.dataset.record, t);
  } else if (t.dataset.retry) { t.closest(".err-card").remove(); ask(t.dataset.retry); }
});
$("clear-history").onclick = async () => {
  if (!confirm("Delete all your chats? This can't be undone.")) return;
  await fetch("/api/chats", { method: "DELETE" });
  if (chatId) newChat(); else loadChats();
};
$("d-close").onclick = closeDrawer;
$("d-scrim").onclick = closeDrawer;
$("d-copy").onclick = async () => {
  if (!drawerRecord) return;
  try { await navigator.clipboard.writeText(drawerRecord); $("d-copy").innerHTML = `${icon("tick")}Copied`; }
  catch (err) { $("d-copy").innerHTML = `${icon("copy")}Copy failed`; }
  setTimeout(() => { $("d-copy").innerHTML = `${icon("copy")}Copy reference`; }, 1600);
};
document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !closeDrawer()) closeNav(); });
$("nav-toggle").onclick = () => ($("app").classList.contains("nav-open") ? closeNav() : openNav());
$("close-nav").onclick = () => { closeNav(); $("nav-toggle").focus(); };
$("scrim").onclick = closeNav;
$("ask-form").addEventListener("submit", (e) => { e.preventDefault(); const q = $("q").value; $("q").value = ""; autosize(); ask(q); });
$("q").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); $("ask-form").requestSubmit(); } });
const autosize = () => { const q = $("q"); q.style.height = "auto"; q.style.height = Math.min(q.scrollHeight, 160) + "px"; };
$("q").addEventListener("input", autosize);
$("new-chat").onclick = newChat;
$("signout").onclick = async () => { await fetch("/api/logout", { method: "POST" }); location.replace("/login.html"); };

if (location.protocol.startsWith("http")) boot();
else $("empty").innerHTML = "<h2>Open this through the app server</h2><p>Run the server and go to http://localhost:8010.</p>";
