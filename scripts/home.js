// Theme toggle — shares the 'theme' localStorage key with main.js
// so the choice persists across the home and inner pages.
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

// Mobile menu toggle
const menuToggle = document.querySelector(".menu-toggle");
const nav = document.querySelector(".nav");
if (menuToggle && nav) {
  menuToggle.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    if (open) {
      nav.style.display = "flex";
      nav.style.position = "absolute";
      nav.style.top = "72px";
      nav.style.left = "0";
      nav.style.right = "0";
      nav.style.margin = "0";
      nav.style.padding = "20px";
      nav.style.flexDirection = "column";
      nav.style.background = "var(--orange)";
    } else {
      nav.removeAttribute("style");
    }
  });
}

// Footer year (if any element has id="year")
const yearEl = document.getElementById("year");
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Back-to-top — explicit JS so it works regardless of #top anchor quirks
const backTop = document.querySelector(".back-top");
if (backTop) {
  backTop.addEventListener("click", (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}
