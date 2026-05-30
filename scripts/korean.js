/* Korean section — search + multi-row chip filtering + load-more.
   Activates on any page that has a [data-kr-grid] element. */
(function () {
  const grid = document.querySelector("[data-kr-grid]");
  if (!grid) return;

  const items     = Array.from(grid.querySelectorAll("[data-kr-item]"));
  const filterEl  = document.querySelector("[data-kr-filters]");
  const searchEl  = document.querySelector("[data-kr-search]");
  const countEl   = document.querySelector("[data-kr-count]");
  const emptyEl   = document.querySelector("[data-kr-empty]");
  const loadMore  = document.querySelector("[data-kr-loadmore]");
  const loadBtn   = document.querySelector("[data-kr-loadmore-btn]");

  const pageSize  = parseInt(grid.dataset.krPageSize || "0", 10); // 0 = no pagination
  let shownCount  = pageSize > 0 ? pageSize : Infinity;

  // Active filter state — { rowName: "all" | "<value>" }
  const filters = {};
  if (filterEl) {
    filterEl.querySelectorAll("[data-kr-row]").forEach(row => {
      filters[row.dataset.krRow] = "all";
    });
  }
  let searchTerm = "";

  function matches(item) {
    // Filter rows — AND across rows.
    for (const row in filters) {
      const wanted = filters[row];
      if (wanted === "all") continue;

      const raw = item.dataset[row] || "";
      // Multi-value fields (topics, usage, hanja) come in as CSV.
      if (row === "topics" || row === "usage" || row === "topic" || row === "hanja") {
        // Note: data attr for "topic" filter row is data-topics; others match their row name.
        const attrKey = (row === "topic") ? "topics" : row;
        const values = (item.dataset[attrKey] || "").split(",").map(s => s.trim()).filter(Boolean);
        if (!values.includes(wanted)) return false;
      } else if (row === "level") {
        // "any" level items match every level filter.
        if (raw !== wanted && raw !== "any") return false;
      } else {
        if (raw !== wanted) return false;
      }
    }
    // Search.
    if (searchTerm) {
      const blob = item.dataset.search || "";
      if (!blob.includes(searchTerm)) return false;
    }
    return true;
  }

  function apply() {
    let matchCount = 0;
    let shown = 0;
    items.forEach(it => {
      if (matches(it)) {
        matchCount++;
        if (shown < shownCount) {
          it.classList.remove("is-hidden");
          shown++;
        } else {
          it.classList.add("is-hidden");
        }
      } else {
        it.classList.add("is-hidden");
      }
    });

    if (countEl) {
      if (matchCount === items.length) {
        countEl.textContent = `${matchCount} ${matchCount === 1 ? "item" : "items"}`;
      } else {
        countEl.textContent = `${matchCount} of ${items.length} shown`;
      }
    }

    if (emptyEl) emptyEl.hidden = matchCount > 0;

    if (loadMore) {
      loadMore.hidden = matchCount <= shownCount;
    }
  }

  // Chip clicks (single-select per row, "All" resets the row).
  if (filterEl) {
    filterEl.addEventListener("click", e => {
      const chip = e.target.closest(".kr-chip");
      if (!chip) return;
      const row = chip.closest("[data-kr-row]");
      if (!row) return;

      const rowName = row.dataset.krRow;
      const value   = chip.dataset.krValue;
      filters[rowName] = value;

      row.querySelectorAll(".kr-chip").forEach(c => c.classList.toggle("is-active", c === chip));

      // Reset paging when filters change.
      if (pageSize > 0) shownCount = pageSize;
      apply();
    });
  }

  // Search input (debounced).
  if (searchEl) {
    let t;
    searchEl.addEventListener("input", () => {
      clearTimeout(t);
      t = setTimeout(() => {
        searchTerm = searchEl.value.trim().toLowerCase();
        if (pageSize > 0) shownCount = pageSize;
        apply();
      }, 120);
    });
  }

  // Load more.
  if (loadBtn) {
    loadBtn.addEventListener("click", () => {
      shownCount += pageSize;
      apply();
    });
  }

  apply();
})();
