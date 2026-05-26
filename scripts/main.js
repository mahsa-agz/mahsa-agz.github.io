// ===== Year =====
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// ===== Scroll progress =====
const progress = document.querySelector(".scroll-progress span");
if (progress) {
  const update = () => {
    const h = document.documentElement;
    const max = h.scrollHeight - h.clientHeight;
    const pct = max > 0 ? (h.scrollTop / max) * 100 : 0;
    progress.style.width = pct + "%";
  };
  document.addEventListener("scroll", update, { passive: true });
  update();
}

// ===== Scroll reveal =====
const revealEls = document.querySelectorAll("[data-reveal]");
if ("IntersectionObserver" in window && revealEls.length) {
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
  );
  revealEls.forEach((el) => io.observe(el));
} else {
  revealEls.forEach((el) => el.classList.add("is-visible"));
}

// ===== Theme toggle =====
const themeBtn = document.querySelector("[data-theme-toggle]");
if (themeBtn) {
  const root = document.documentElement;
  const getCurrent = () => {
    const stored = localStorage.getItem("theme");
    if (stored === "dark" || stored === "light") return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  };
  themeBtn.addEventListener("click", () => {
    const next = getCurrent() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {
      localStorage.setItem("theme", next);
    } catch (e) {}
  });
}

// ===== Category filter (used on /blog/) =====
document.querySelectorAll("[data-filter]").forEach((filter) => {
  const group = filter.getAttribute("data-filter");
  const chips = Array.from(filter.querySelectorAll("[data-filter-value]"));
  const list = document.querySelector(`[data-filterable="${group}"]`);
  if (!list) return;
  const items = Array.from(list.querySelectorAll("[data-category]"));
  const empty = list.querySelector("[data-filter-empty]");

  const apply = (value) => {
    let shown = 0;
    items.forEach((item) => {
      const match =
        value === "all" || item.getAttribute("data-category") === value;
      item.hidden = !match;
      if (match) shown++;
    });
    if (empty) empty.hidden = shown !== 0;
  };

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => {
        const on = c === chip;
        c.classList.toggle("is-active", on);
        c.setAttribute("aria-pressed", on ? "true" : "false");
      });
      apply(chip.getAttribute("data-filter-value"));
    });
  });
});

// ===== Tabs (ARIA) =====
document.querySelectorAll("[data-tabs]").forEach((tabsRoot) => {
  const tabs = Array.from(tabsRoot.querySelectorAll('[role="tab"]'));
  const panels = tabs.map((t) =>
    document.getElementById(t.getAttribute("aria-controls"))
  );

  const activate = (idx) => {
    tabs.forEach((t, i) => {
      const selected = i === idx;
      t.setAttribute("aria-selected", selected ? "true" : "false");
      t.setAttribute("tabindex", selected ? "0" : "-1");
      if (panels[i]) {
        if (selected) panels[i].removeAttribute("hidden");
        else panels[i].setAttribute("hidden", "");
      }
    });
  };

  tabs.forEach((tab, idx) => {
    tab.addEventListener("click", () => {
      activate(idx);
      tab.focus();
    });
    tab.addEventListener("keydown", (e) => {
      let next = idx;
      if (e.key === "ArrowRight") next = (idx + 1) % tabs.length;
      else if (e.key === "ArrowLeft")
        next = (idx - 1 + tabs.length) % tabs.length;
      else if (e.key === "Home") next = 0;
      else if (e.key === "End") next = tabs.length - 1;
      else return;
      e.preventDefault();
      activate(next);
      tabs[next].focus();
    });
  });
});
