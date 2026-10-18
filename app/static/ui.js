// Shared UI pieces for login.html and index.html: icons, the assistant character, theme switching.
"use strict";

const UI = (() => {
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---------------------------------------------------------------- icons (24px stroke)
  const PATHS = {
    policy: '<path d="M12 3l8 3v6c0 4.4-3.4 8.2-8 9-4.6-.8-8-4.6-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    book: '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11"/>',
    ticket: '<path d="M4 7h16v3a2 2 0 0 0 0 4v3H4v-3a2 2 0 0 0 0-4z"/><path d="M14 7v10"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 7l8.5 6 8.5-6"/>',
    hash: '<path d="M5 9h14M5 15h14M10 4L8 20M16 4l-2 16"/>',
    scale: '<path d="M12 4v16M7 20h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
    split: '<path d="M8 4v16M16 4v16"/><path d="M5 7l3-3 3 3M13 17l3 3 3-3"/>',
    lock: '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.6 2.6L16 9.5"/>',
    tick: '<path d="M6 12.5l4 4L18 8"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    help: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6v.6M12 17v.01"/>',
    userx: '<circle cx="10" cy="8" r="4"/><path d="M3 20a7 7 0 0 1 13-3.5M17 14l4 4M21 14l-4 4"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    key: '<circle cx="8" cy="15" r="4"/><path d="M11 12l8-8M16 7l3 3"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    x: '<path d="M6 6l12 12M18 6L6 18"/>',
    menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    chev: '<path d="M6 9l6 6 6-6"/>',
    right: '<path d="M9 6l6 6-6 6"/>',
    up: '<path d="M12 19V5M6 11l6-6 6 6"/>',
    out: '<path d="M15 4h4a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-4"/><path d="M10 16l-4-4 4-4M6 12h10"/>',
    copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/>',
    route: '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="12" r="2"/><path d="M8 6h4a4 4 0 0 1 4 4M8 18h4a4 4 0 0 0 4-4"/>',
    moon: '<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    trash: '<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13"/>',
    alert: '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5M12 16v.01"/>',
    eye: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    eyeoff: '<path d="M3 3l18 18"/><path d="M10.6 5.1A10 10 0 0 1 12 5c6.4 0 10 7 10 7a17 17 0 0 1-3.2 4.2M6.6 6.6A17 17 0 0 0 2 12s3.6 7 10 7a9.6 9.6 0 0 0 5.4-1.6"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
    logo: '<path d="M3 13c5 0 8.5-3 10-8.5 1 4.5 4 7.5 8 8.5-4 .8-7 3.8-8 7.5-1.5-4-5-7.5-10-7.5z"/>',
  };
  const icon = (name, cls = "ic") => `<svg class="${cls}" viewBox="0 0 24 24" aria-hidden="true">${PATHS[name] || ""}</svg>`;

  // ---------------------------------------------------------------- the assistant character
  // Light: sunglasses (pushed up while searching). Dark: holding a candle. Both are drawn; CSS shows the one
  // matching the theme, and a `.searching` ancestor switches on the search animation.
  let uid = 0;
  const BODY_L = (g) => `
    <ellipse class="b-shadow" cx="100" cy="221" rx="50" ry="7" fill="#14213D" opacity=".12"/>
    <g class="b-float">
      <ellipse cx="150" cy="162" rx="12" ry="25" transform="rotate(-20 150 162)" fill="url(#${g})" stroke="#1B2333" stroke-width="3.5"/>
      <ellipse cx="50" cy="162" rx="12" ry="25" transform="rotate(20 50 162)" fill="url(#${g})" stroke="#1B2333" stroke-width="3.5"/>
      <path d="M100 114C134 114 149 142 149 170C149 198 128 214 100 214C72 214 51 198 51 170C51 142 66 114 100 114Z" fill="url(#${g})" stroke="#1B2333" stroke-width="3.5"/>
      <rect x="87" y="134" width="26" height="7" rx="3.5" fill="#8FD3F4"/>
      <path d="M70 164Q100 154 130 164Q128 186 100 192Q72 186 70 164Z" fill="none" stroke="#1B2333" stroke-width="2.5" opacity=".4"/>
      <g class="b-head">
        <path d="M80 46L71 22M120 46L129 22" stroke="#1B2333" stroke-width="3.5" stroke-linecap="round"/>
        <circle class="b-tip" cx="70" cy="18" r="6.5" fill="#FFFFFF" stroke="#1B2333" stroke-width="3.5"/>
        <circle class="b-tip r" cx="130" cy="18" r="6.5" fill="#FFFFFF" stroke="#1B2333" stroke-width="3.5"/>
        <ellipse cx="100" cy="84" rx="60" ry="46" fill="url(#${g})" stroke="#1B2333" stroke-width="3.5"/>
        <path d="M60 66Q70 48 92 43" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <g class="b-eyes"><g class="b-blink">
          <ellipse cx="79" cy="86" rx="12" ry="14" fill="#141A26"/><ellipse cx="121" cy="86" rx="12" ry="14" fill="#141A26"/>
          <circle cx="75" cy="80" r="4" fill="#FFFFFF"/><circle cx="117" cy="80" r="4" fill="#FFFFFF"/>
        </g></g>
        <path d="M93 106Q100 112 107 106" fill="none" stroke="#1B2333" stroke-width="3" stroke-linecap="round"/>
        <g class="b-shades">
          <path d="M42 72H158" stroke="#141A26" stroke-width="5" stroke-linecap="round"/>
          <path d="M47 71H96V84Q96 100 79 100H64Q47 100 47 84Z" fill="#141A26"/>
          <path d="M104 71H153V84Q153 100 136 100H121Q104 100 104 84Z" fill="#141A26"/>
          <path class="b-glint" d="M56 78L66 78M113 78L123 78" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
        </g>
      </g>
    </g>`;
  const BODY_D = (g, h) => `
    <ellipse class="b-shadow" cx="100" cy="221" rx="54" ry="8" fill="#000000" opacity=".35"/>
    <g class="b-float">
      <ellipse cx="150" cy="162" rx="12" ry="25" transform="rotate(-20 150 162)" fill="url(#${g})" stroke="#0A1226" stroke-width="3.5"/>
      <path d="M100 114C134 114 149 142 149 170C149 198 128 214 100 214C72 214 51 198 51 170C51 142 66 114 100 114Z" fill="url(#${g})" stroke="#0A1226" stroke-width="3.5"/>
      <rect x="87" y="134" width="26" height="7" rx="3.5" fill="#8FD3F4"/>
      <path d="M70 164Q100 154 130 164Q128 186 100 192Q72 186 70 164Z" fill="none" stroke="#0A1226" stroke-width="2.5" opacity=".4"/>
      <rect x="88" y="176" width="24" height="5" rx="2.5" fill="#8FD3F4" opacity=".8"/>
      <g class="b-head">
        <path d="M80 46L71 22M120 46L129 22" stroke="#0A1226" stroke-width="3.5" stroke-linecap="round"/>
        <circle class="b-tip" cx="70" cy="18" r="6.5" fill="#FFFFFF" stroke="#0A1226" stroke-width="3.5"/>
        <circle class="b-tip r" cx="130" cy="18" r="6.5" fill="#FFFFFF" stroke="#0A1226" stroke-width="3.5"/>
        <ellipse cx="100" cy="84" rx="60" ry="46" fill="url(#${g})" stroke="#0A1226" stroke-width="3.5"/>
        <rect x="152" y="70" width="10" height="26" rx="5" fill="#8FD3F4" stroke="#0A1226" stroke-width="3"/>
        <path d="M60 66Q70 48 92 43" fill="none" stroke="#FFFFFF" stroke-width="5" stroke-linecap="round"/>
        <g class="b-eyes"><g class="b-blink">
          <ellipse cx="78" cy="84" rx="15" ry="17" fill="#0A1226"/><ellipse cx="122" cy="84" rx="15" ry="17" fill="#0A1226"/>
          <circle cx="73" cy="77" r="5" fill="#FFFFFF"/><circle cx="117" cy="77" r="5" fill="#FFFFFF"/>
          <circle cx="83" cy="91" r="2" fill="#FFFFFF" opacity=".7"/><circle cx="127" cy="91" r="2" fill="#FFFFFF" opacity=".7"/>
        </g></g>
        <path d="M93 108Q100 114 107 108" fill="none" stroke="#0A1226" stroke-width="3" stroke-linecap="round"/>
      </g>
      <g class="b-candle">
        <circle class="b-halo" cx="31" cy="100" r="48" fill="url(#${h})"/>
        <rect x="22" y="114" width="18" height="30" rx="4" fill="#F7E6C4" stroke="#0A1226" stroke-width="3"/>
        <path d="M22 120Q26 126 29 120Q31 128 34 121" fill="none" stroke="#E8CB92" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M31 114V108" stroke="#0A1226" stroke-width="2.5" stroke-linecap="round"/>
        <g class="b-flame">
          <path d="M31 88C37 97 39 103 35 108C33 110 29 110 27 108C23 103 25 97 31 88Z" fill="#FFC94D"/>
          <path d="M31 97C33 101 33.5 104 31 107C28.5 104 29 101 31 97Z" fill="#FFF4CC"/>
        </g>
        <ellipse cx="44" cy="150" rx="22" ry="11" transform="rotate(25 44 150)" fill="url(#${g})" stroke="#0A1226" stroke-width="3.5"/>
      </g>
    </g>`;

  function bot() {
    const n = ++uid, gl = `kc-gl${n}`, gd = `kc-gd${n}`, h = `kc-h${n}`;
    return `<svg class="bot bot-light" viewBox="0 0 200 230" aria-hidden="true"><defs>
        <linearGradient id="${gl}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#D8E5F1"/></linearGradient>
      </defs>${BODY_L(gl)}</svg>` +
      `<svg class="bot bot-dark" viewBox="0 0 200 230" aria-hidden="true"><defs>
        <linearGradient id="${gd}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F6F9FF"/><stop offset="1" stop-color="#C5D5EC"/></linearGradient>
        <radialGradient id="${h}"><stop offset="0" stop-color="#FFC94D" stop-opacity=".55"/><stop offset=".5" stop-color="#FFB637" stop-opacity=".18"/><stop offset="1" stop-color="#FFB637" stop-opacity="0"/></radialGradient>
      </defs>${BODY_D(gd, h)}</svg>`;
  }

  // Head-only avatar beside each answer.
  const MINI_L = '<svg class="bot-light" viewBox="0 0 40 40" aria-hidden="true"><path d="M14 11L11 5M26 11L29 5" stroke="#1B2333" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="4.5" r="2.2" fill="#FFFFFF" stroke="#1B2333" stroke-width="1.6"/><circle cx="29" cy="4.5" r="2.2" fill="#FFFFFF" stroke="#1B2333" stroke-width="1.6"/><ellipse cx="20" cy="22" rx="16" ry="13" fill="#F4F8FC" stroke="#1B2333" stroke-width="2"/><path d="M5 19.5H35" stroke="#141A26" stroke-width="2"/><path d="M7 19H19V22.5Q19 27 15 27H11Q7 27 7 22.5Z" fill="#141A26"/><path d="M21 19H33V22.5Q33 27 29 27H25Q21 27 21 22.5Z" fill="#141A26"/><path d="M17.5 31Q20 33 22.5 31" stroke="#1B2333" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>';
  const MINI_D = '<svg class="bot-dark" viewBox="0 0 40 40" aria-hidden="true"><path d="M14 11L11 5M26 11L29 5" stroke="#8FD3F4" stroke-width="2" stroke-linecap="round"/><circle cx="11" cy="4.5" r="2.2" fill="#8FD3F4"/><circle cx="29" cy="4.5" r="2.2" fill="#8FD3F4"/><ellipse cx="20" cy="22" rx="16" ry="13" fill="#EEF4FD" stroke="#0A1226" stroke-width="2"/><ellipse cx="14.5" cy="22" rx="3.6" ry="4.4" fill="#0A1226"/><ellipse cx="25.5" cy="22" rx="3.6" ry="4.4" fill="#0A1226"/><circle cx="13.2" cy="20.4" r="1.2" fill="#FFFFFF"/><circle cx="24.2" cy="20.4" r="1.2" fill="#FFFFFF"/><path d="M17.5 29Q20 31 22.5 29" stroke="#0A1226" stroke-width="1.8" fill="none" stroke-linecap="round"/></svg>';
  const mini = () => `<span class="mini" aria-hidden="true">${MINI_L}${MINI_D}</span>`;

  // Source cards that fly into the bot while it searches.
  const FLY = [["policy", "Policies", -96, -70], ["book", "Confluence", 92, -60], ["ticket", "ServiceNow", -100, 36],
               ["mail", "Email", 98, 44], ["hash", "Slack", 0, 92]];
  const flyCards = () => FLY.map(([ic, label, x, y], i) =>
    `<span class="fly" style="--fx:${x}px;--fy:${y}px;animation-delay:${i}s">${icon(ic)}${label}</span>`).join("");

  // ---------------------------------------------------------------- theme
  const root = document.documentElement;
  const theme = () => (root.dataset.theme === "dark" ? "dark" : "light");
  function syncToggles() {
    document.querySelectorAll("[data-theme-toggle]").forEach((b) => {
      const label = theme() === "dark" ? "Switch to light theme" : "Switch to dark theme";
      b.setAttribute("aria-label", label);
      b.title = label;
    });
  }
  function setTheme(t) {
    root.dataset.theme = t;
    try { localStorage.setItem("kc-theme", t); } catch (e) { /* private mode: theme still applies for this page */ }
    syncToggles();
  }
  const themeButtonInner = () => `${icon("moon", "ic lg bot-light")}${icon("sun", "ic lg bot-dark")}`;
  document.addEventListener("click", (e) => {
    if (e.target.closest("[data-theme-toggle]")) setTheme(theme() === "dark" ? "light" : "dark");
  });
  document.addEventListener("DOMContentLoaded", syncToggles);

  return { esc, icon, bot, mini, flyCards, themeButtonInner, syncToggles };
})();
