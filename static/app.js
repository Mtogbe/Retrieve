// Retrieve front-end logic (Person 3)

// Escape text before putting it into HTML
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

// Fetch JSON and turn API errors into readable messages
async function getJson(url, options) {
  const res = await fetch(url, options);
  let data = null;
  try { data = await res.json(); } catch (e) { data = null; }
  if (!res.ok) throw new Error((data && data.error) || `Request failed (${res.status})`);
  return data;
}

// Accepting-students status line
function statusHtml(value) {
  if (value === "yes") return '<span class="status status-yes">Taking students</span>';
  if (value === "no") return '<span class="status status-no">Not taking students</span>';
  return '<span class="status">Ask about openings</span>';
}

// One lab row in the results list
function labRow(lab) {
  const areas = (lab.research_areas || [])
    .map((a) => `<button type="button" class="area-chip" data-area="${escapeHtml(a)}">${escapeHtml(a)}</button>`)
    .join("");
  const pi = lab.pi_name ? `<span class="lab-pi">${escapeHtml(lab.pi_name)}</span>` : "";
  const desc = lab.description ? `<p class="lab-desc">${escapeHtml(lab.description)}</p>` : "";
  const link = `/lab/${encodeURIComponent(lab.id)}`;

  return `
    <li class="lab-row">
      <div class="lab-main">
        <h2 class="lab-name"><a href="${link}">${escapeHtml(lab.name)}</a></h2>
        <div class="lab-meta">${pi}<span class="lab-dept">${escapeHtml(lab.department)}</span></div>
        ${desc}
        <div class="lab-areas">${areas}</div>
      </div>
      <div class="lab-side">
        ${statusHtml(lab.accepting_students)}
        <a class="btn btn-retrieve" href="${link}">View lab</a>
      </div>
    </li>`;
}

// Home page: search, department filter, area chips
function initSearchPage() {
  const input = document.getElementById("search-input");
  const deptSelect = document.getElementById("department-select");
  const results = document.getElementById("results");
  const count = document.getElementById("result-count");
  const areaFilter = document.getElementById("area-filter");
  const areaTags = document.getElementById("area-tags");

  let currentArea = "";
  let timer = null;
  let requestId = 0;
  let topAreas = [];

  async function runSearch() {
    const params = new URLSearchParams();
    if (input.value.trim()) params.set("q", input.value.trim());
    if (deptSelect.value) params.set("department", deptSelect.value);
    if (currentArea) params.set("area", currentArea);

    const myId = ++requestId;
    count.textContent = "Searching...";
    try {
      const labs = await getJson("/api/labs?" + params.toString());
      if (myId !== requestId) return; // a newer search already started
      renderResults(labs);
    } catch (err) {
      if (myId !== requestId) return;
      console.log("Search failed:", err);
      count.textContent = "";
      results.innerHTML = `<li class="empty-state">Couldn't load labs: ${escapeHtml(err.message)}. Check that the Flask server is running, then refresh.</li>`;
    }
  }

  function renderResults(labs) {
    count.textContent = `${labs.length} lab${labs.length === 1 ? "" : "s"} found`;
    if (!labs.length) {
      results.innerHTML = '<li class="empty-state">No labs match that search. Try a shorter term or choose All departments.</li>';
      return;
    }
    results.innerHTML = labs.map(labRow).join("");
  }

  function setArea(area) {
    currentArea = area;
    if (area) {
      areaFilter.innerHTML = `Area: <strong>${escapeHtml(area)}</strong><button type="button" id="clear-area">Clear</button>`;
      areaFilter.classList.remove("d-none");
    } else {
      areaFilter.innerHTML = "";
      areaFilter.classList.add("d-none");
    }
    renderAreaTags();
    runSearch();
  }

  // Fill the department dropdown and the area tags from the full lab list
  async function loadFilters() {
    try {
      const labs = await getJson("/api/labs");

      const depts = [...new Set(labs.map((l) => l.department).filter(Boolean))].sort();
      deptSelect.innerHTML = '<option value="">All departments</option>' +
        depts.map((d) => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join("");

      // Count how many labs use each area, then keep the 12 most common
      const counts = {};
      labs.forEach((lab) => {
        (lab.research_areas || []).forEach((a) => {
          counts[a] = (counts[a] || 0) + 1;
        });
      });
      topAreas = Object.keys(counts).sort((a, b) => counts[b] - counts[a]).slice(0, 12);
      renderAreaTags();
    } catch (err) {
      console.log("Could not load filters:", err);
    }
  }

  // Draw the tags at the top, highlighting the selected one
  function renderAreaTags() {
    areaTags.innerHTML = topAreas
      .map((a) => `<button type="button" class="area-chip${a === currentArea ? " active" : ""}" data-area="${escapeHtml(a)}">${escapeHtml(a)}</button>`)
      .join("");
  }

    // Fill the department dropdown and the area tags from the full lab list
  async function loadFilters() {
    try {
      const labs = await getJson("/api/labs");

      const depts = [...new Set(labs.map((l) => l.department).filter(Boolean))].sort();
      deptSelect.innerHTML = '<option value="">All departments</option>' +
        depts.map((d) => `<option value="${escapeHtml(d)}">${escapeHtml(d)}</option>`).join("");

      // Count how many labs use each area, then keep the 12 most common
      const counts = {};
      labs.forEach((lab) => {
        (lab.research_areas || []).forEach((a) => {
          counts[a] = (counts[a] || 0) + 1;
        });
      });
      topAreas = Object.keys(counts).sort((a, b) => counts[b] - counts[a]).slice(0, 12);
      renderAreaTags();
    } catch (err) {
      console.log("Could not load filters:", err);
    }
  }

  // Draw the tags at the top, highlighting the selected one
  function renderAreaTags() {
    areaTags.innerHTML = topAreas
      .map((a) => `<button type="button" class="area-chip${a === currentArea ? " active" : ""}" data-area="${escapeHtml(a)}">${escapeHtml(a)}</button>`)
      .join("");
  }
  // Wait until typing pauses before searching
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(runSearch, 250);
  });

  deptSelect.addEventListener("change", runSearch);

  // Clicking an area chip filters by that area
  results.addEventListener("click", (e) => {
    const chip = e.target.closest(".area-chip");
    if (chip) setArea(chip.dataset.area);
  });

  // Clicking a top tag filters; clicking it again clears
  areaTags.addEventListener("click", (e) => {
    const chip = e.target.closest(".area-chip");
    if (!chip) return;
    setArea(chip.dataset.area === currentArea ? "" : chip.dataset.area);
  });

  areaFilter.addEventListener("click", (e) => {
    if (e.target.id === "clear-area") setArea("");
  });

  loadFilters();
  runSearch();
}

// Run the right code for whichever page is open
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("search-page")) initSearchPage();
});
