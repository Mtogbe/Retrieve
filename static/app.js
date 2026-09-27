// Retrieve front-end logic (Person 3)

const NA_FACULTY = "Faculty Information Not Applicable";
const NA = "Not Applicable";

// Treat the data pipeline's "not found" placeholder as absent
function isMissing(value) {
  return value == null || value === "" || String(value).trim().toLowerCase() === "not found";
}

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

// Accepting-students status line - only shown when we actually know the answer
function statusHtml(value) {
  if (value === "yes") return '<span class="status status-yes">Taking students</span>';
  if (value === "no") return '<span class="status status-no">Not taking students</span>';
  return "";
}

// Research area chips, or a single "Not Applicable" chip if none are real
function areaChipsHtml(researchAreas, tagName) {
  const real = (researchAreas || []).filter((a) => !isMissing(a));
  if (!real.length) return `<span class="area-chip">${escapeHtml(NA)}</span>`;
  if (tagName === "button") {
    return real
      .map((a) => `<button type="button" class="area-chip" data-area="${escapeHtml(a)}">${escapeHtml(a)}</button>`)
      .join("");
  }
  return real.map((a) => `<span class="lab-tag">${escapeHtml(a)}</span>`).join("");
}

// One lab row in the results list
function labRow(lab) {
  const areas = areaChipsHtml(lab.research_areas, "button");
  const pi = `<span class="lab-pi">${escapeHtml(isMissing(lab.pi_name) ? NA_FACULTY : lab.pi_name)}</span>`;
  const desc = `<p class="lab-desc">${escapeHtml(isMissing(lab.description) ? NA_FACULTY : lab.description)}</p>`;
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

// Labs page: search, department filter, area tags
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

      // Count how many labs use each area, then show every tag that's
      // actually used (skip the "not found" placeholder so it never
      // becomes a filter chip), most-used first.
      const counts = {};
      labs.forEach((lab) => {
        (lab.research_areas || []).forEach((a) => {
          if (isMissing(a)) return;
          counts[a] = (counts[a] || 0) + 1;
        });
      });
      topAreas = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
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

  // Clicking a tag on a lab card filters by that area
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

// Match page: resume upload, interests, AI results, email drafts
function initMatchPage() {
  const form = document.getElementById("match-form");
  const resumeInput = document.getElementById("resume-input");
  const interestsInput = document.getElementById("interests-input");
  const button = document.getElementById("match-button");
  const errorBox = document.getElementById("match-error");
  const loading = document.getElementById("match-loading");
  const count = document.getElementById("match-count");
  const results = document.getElementById("match-results");

  const dialog = document.getElementById("email-dialog");
  const emailTo = document.getElementById("email-to");
  const emailLoading = document.getElementById("email-loading");
  const emailError = document.getElementById("email-error");
  const emailDraft = document.getElementById("email-draft");
  const copyButton = document.getElementById("email-copy");

  let labsById = {};    // lab id -> full lab record
  let resumeText = "";  // saved for the email draft step
  let emailRequestId = 0;

  // Download all labs once so we can show full details for each match
  async function loadLabs() {
    const labs = await getJson("/api/labs");
    labs.forEach((lab) => { labsById[lab.id] = lab; });
  }

  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("d-none");
  }

  // One matched lab, with the AI's reason near the top
  function matchRow(match) {
    const lab = labsById[match.lab_id];
    if (!lab) return "";  // never show a lab that isn't in our data

    const tags = areaChipsHtml(lab.research_areas, "span");
    const pi = `<span class="lab-pi">${escapeHtml(isMissing(lab.pi_name) ? NA_FACULTY : lab.pi_name)}</span>`;
    const desc = `<p class="lab-desc">${escapeHtml(isMissing(lab.description) ? NA_FACULTY : lab.description)}</p>`;
    const email = isMissing(lab.contact_email)
      ? `<div class="lab-email">Email: ${escapeHtml(NA_FACULTY)}</div>`
      : `<div class="lab-email">Email: <a href="mailto:${escapeHtml(lab.contact_email)}">${escapeHtml(lab.contact_email)}</a></div>`;
    const link = `/lab/${encodeURIComponent(lab.id)}`;

    return `
      <li class="lab-row">
        <div class="lab-main">
          <h2 class="lab-name"><a href="${link}">${escapeHtml(lab.name)}</a></h2>
          <div class="lab-meta">${pi}<span class="lab-dept">${escapeHtml(lab.department)}</span></div>
          <div class="match-reason"><strong>Why this matches you:</strong> ${escapeHtml(match.reason)}</div>
          ${desc}
          ${email}
          <div class="lab-areas mt-2">${tags}</div>
        </div>
        <div class="lab-side">
          ${statusHtml(lab.accepting_students)}
          <button type="button" class="btn btn-retrieve apply-btn" data-lab-id="${escapeHtml(lab.id)}">Apply</button>
        </div>
      </li>`;
  }

  // Open the popup and ask the server to draft an email for one lab
  async function openEmailDraft(labId) {
    const lab = labsById[labId];
    if (!lab) return;

    const myId = ++emailRequestId;
    emailTo.textContent = !isMissing(lab.contact_email)
      ? `To: ${!isMissing(lab.pi_name) ? lab.pi_name : lab.name} (${lab.contact_email})`
      : `For: ${lab.name} (${NA_FACULTY})`;
    emailError.classList.add("d-none");
    emailDraft.classList.add("d-none");
    emailDraft.value = "";
    emailLoading.classList.remove("d-none");
    copyButton.disabled = true;
    copyButton.textContent = "Copy email";
    dialog.showModal();

    try {
      const res = await getJson("/api/email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lab_id: labId, resume_text: resumeText }),
      });
      if (myId !== emailRequestId) return;  // they opened a different lab meanwhile
      emailDraft.value = res.draft || "";
      emailDraft.classList.remove("d-none");
      copyButton.disabled = false;
    } catch (err) {
      if (myId !== emailRequestId) return;
      console.log("Email draft failed:", err);
      emailError.textContent = `Couldn't write the draft: ${err.message}`;
      emailError.classList.remove("d-none");
    } finally {
      if (myId === emailRequestId) emailLoading.classList.add("d-none");
    }
  }

  // Apply buttons are created after the page loads, so listen on the list that holds them
  results.addEventListener("click", (e) => {
    const btn = e.target.closest(".apply-btn");
    if (btn) openEmailDraft(btn.dataset.labId);
  });

  document.getElementById("email-close").addEventListener("click", () => dialog.close());

  // Clicking the dark area outside the popup closes it
  dialog.addEventListener("click", (e) => {
    if (e.target === dialog) dialog.close();
  });

  copyButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(emailDraft.value);
      copyButton.textContent = "Copied";
    } catch (err) {
      console.log("Copy failed:", err);
      emailDraft.select();  // highlight it so they can press Ctrl+C
      copyButton.textContent = "Press Ctrl+C to copy";
    }
    setTimeout(() => { copyButton.textContent = "Copy email"; }, 2000);
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();  // stop the browser from reloading the page
    errorBox.classList.add("d-none");

    const file = resumeInput.files[0];
    const interests = interestsInput.value.trim();

    // Check the input before bothering the server
    if (!file && !interests) {
      showError("Upload resume or type at least one interest.");
      return;
    }
    if (file && file.type !== "application/pdf") {
      showError("Resume needs to be PDF");
      return;
    }

    // Package the file and text the way /api/match expects
    const data = new FormData();
    if (file) data.append("resume", file);
    if (interests) data.append("interests", interests);

    button.disabled = true;
    loading.classList.remove("d-none");
    count.textContent = "";
    results.innerHTML = "";

    try {
      if (!Object.keys(labsById).length) await loadLabs();
      const res = await getJson("/api/match", { method: "POST", body: data });
      resumeText = res.resume_text || "";

      const rows = (res.matches || []).map(matchRow).filter(Boolean);
      count.textContent = `${rows.length} match${rows.length === 1 ? "" : "es"} found`;
      results.innerHTML = rows.length
        ? rows.join("")
        : '<li class="empty-state">No matches yet. Add more interests, or upload your resume for better matches.</li>';
      button.textContent = "Update matches";
    } catch (err) {
      console.log("Match failed:", err);
      showError(`Couldn't get matches: ${err.message}`);
    } finally {
      button.disabled = false;
      loading.classList.add("d-none");
    }
  });
}
// Floating chat panel (on every page)
function initChat() {
  const toggle = document.getElementById("chat-toggle");
  const panel = document.getElementById("chat-panel");
  const closeBtn = document.getElementById("chat-close");
  const messages = document.getElementById("chat-messages");
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const send = document.getElementById("chat-send");

  let history = [];      // past messages, sent with each new question
  let labsById = null;   // loaded the first time the AI mentions a lab

  function openChat() {
    panel.classList.remove("d-none");
    toggle.setAttribute("aria-expanded", "true");
    input.focus();
  }

  function closeChat() {
    panel.classList.add("d-none");
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
  }

  toggle.addEventListener("click", () => {
    if (panel.classList.contains("d-none")) openChat();
    else closeChat();
  });
  closeBtn.addEventListener("click", closeChat);
  panel.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeChat();
  });

  // Add one message bubble and scroll down to it
  function addMessage(role, text) {
    const bubble = document.createElement("div");
    bubble.className = `chat-msg ${role === "user" ? "chat-user" : "chat-ai"}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
  }

  // Show links to the labs the AI mentioned (only ones in our data)
  async function addLabLinks(bubble, labIds) {
    if (!labIds || !labIds.length) return;
    try {
      if (!labsById) {
        const map = {};
        const labs = await getJson("/api/labs");
        labs.forEach((lab) => { map[lab.id] = lab; });
        labsById = map;
      }
      const links = labIds
        .filter((id) => labsById[id])
        .map((id) => `<a class="chat-lab-link" href="/lab/${encodeURIComponent(id)}">${escapeHtml(labsById[id].name)}</a>`);
      if (links.length) {
        bubble.insertAdjacentHTML("beforeend", `<div class="chat-labs">${links.join("")}</div>`);
        messages.scrollTop = messages.scrollHeight;
      }
    } catch (err) {
      console.log("Could not load lab links:", err);
    }
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;

    addMessage("user", text);
    input.value = "";
    send.disabled = true;
    const thinking = addMessage("assistant", "Thinking...");
    thinking.classList.add("chat-thinking");

    try {
      const res = await getJson("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: history }),
      });
      thinking.remove();

      const reply = res.reply || "No answer came back. Try asking another way.";
      const bubble = addMessage("assistant", reply);

      // Remember this exchange so follow-up questions make sense
      history.push({ role: "user", content: text });
      history.push({ role: "assistant", content: reply });
      history = history.slice(-20);  // keep only the last 20 messages

      addLabLinks(bubble, res.lab_ids);
    } catch (err) {
      thinking.remove();
      console.log("Chat failed:", err);
      addMessage("assistant", `Couldn't get an answer: ${err.message}`).classList.add("chat-error");
    } finally {
      send.disabled = false;
      input.focus();
    }
  });
}
// Run the right code for whichever page is open
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("search-page")) initSearchPage();
  if (document.getElementById("match-page")) initMatchPage();
  if (document.getElementById("chat-panel")) initChat();
});