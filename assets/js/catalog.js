const JOB_LABELS = {
  all: "All work",
  write: "Write",
  research: "Research",
  design: "Design",
  build: "Build",
  career: "Career",
  teach: "Teach",
  table: "Run a game"
};

const HIDDEN_PERSONAL_OR_PRIVATE_PACKAGES = new Set(["discord", "oppia-research-compass"]);
const GUIDE_HISTORY_IDS = {
  "participatory-defense-field-guide": ["participatory-defense-assistant", "grounded-legal-research"],
  "understanding-ai-2026": ["understanding-ai-2026"],
  "mcp-basics": ["safe-install-review"]
};

function installationAsset(release) {
  if (!release || release.distribution_status !== "available" || !["stable", "release"].includes(release.channel)) return null;
  return release.assets?.find((asset) => asset.role === "installation" && asset.url?.startsWith("https://")) || null;
}

function currentRelease(product) {
  return product?.releases?.find((release) => release.release_key === product.current_release_key) || null;
}

function releaseDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : new Intl.DateTimeFormat("en", {year: "numeric", month: "short", day: "numeric", timeZone: "UTC"}).format(date);
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

const CATALOG_GROUPS = [
  {
    id: "studios",
    title: "Studios",
    description: "Focused creative and professional workflows that help you move from a real brief to work you can review."
  },
  {
    id: "templates",
    title: "Template Libraries",
    description: "Find a strong starting point, adapt it to your project, and keep the editable source close."
  },
  {
    id: "toolkits",
    title: "Toolkits",
    description: "Focused tools for clearer decisions, creative production, research, and everyday operations."
  },
  {
    id: "workflows",
    title: "Workflows",
    description: "Reliable support for planning, operations, and getting the next step over the line."
  },
  {
    id: "resources",
    title: "Free Guides",
    description: "Short, useful resources you can open and use right away."
  }
];

function groupFor(item) {
  if (item.kind === "Installable plugin" || item.kind === "Optional integration") return item.family || "workflows";
  return "resources";
}

function createSkillDetails(skills) {
  const details = document.createElement("details");
  const summary = element("summary", "", `${skills.length} included ${skills.length === 1 ? "skill" : "skills"}`);
  const list = element("ul", "skill-list");
  skills.forEach((skill) => {
    const item = document.createElement("li");
    item.append(element("code", "", skill));
    list.append(item);
  });
  details.append(summary, list);
  return details;
}

function createDownloadDetails(downloads) {
  const available = downloads.filter((download) => download.availability === "available");
  if (!available.length) return null;

  const details = document.createElement("details");
  const summary = element("summary", "", `${available.length} verified ${available.length === 1 ? "download" : "downloads"}`);
  const list = element("ul", "download-list");

  available.forEach((download) => {
    const item = document.createElement("li");
    const link = element("a", "", download.label);
    link.href = download.url;
    link.setAttribute("download", "");
    const audience = element("small", "", download.recommended_for || download.filename);
    item.append(link, audience);
    if (download.checksum) item.append(element("code", "", `SHA-256 ${download.checksum}`));
    list.append(item);
  });

  details.append(summary, list);
  return details;
}

function createPackageDetails(item) {
  const details = document.createElement("details");
  const summary = element("summary", "", "Package details");
  const list = document.createElement("ul");
  list.className = "package-detail-list";
  if (item.description) {
    const row = document.createElement("li");
    row.append(element("strong", "", "Package overview"), element("span", "", item.description));
    list.append(row);
  }
  if (item.requirements?.length) {
    const row = document.createElement("li");
    row.append(element("strong", "", "What you need"), element("span", "", item.requirements.join("; ")));
    list.append(row);
  }
  if (item.edition) {
    const row = document.createElement("li");
    row.append(element("strong", "", "Package scope"), element("span", "", item.edition));
    list.append(row);
  }
  if (item.ownership_note) {
    const row = document.createElement("li");
    row.append(element("strong", "", "Included capability"), element("span", "", item.ownership_note));
    list.append(row);
  }
  if (item.license) {
    const row = document.createElement("li");
    row.append(element("strong", "", "License"), element("span", "", item.license));
    list.append(row);
  }
  details.append(summary, list);
  return details;
}

function createRow(item, accessLabels) {
  const row = element("article", "library-row");
  row.id = `product-${item.id}`;
  row.dataset.access = item.access;

  const meta = element("div", "library-meta");
  const statusText = item.kind === "Installable plugin" || item.kind === "Optional integration" ? "Available now" : accessLabels[item.access];
  const status = element("span", "status-label", statusText);
  status.dataset.access = item.access;
  meta.append(status);

  const main = element("div", "library-main");
  main.append(element("h3", "", item.name));
  if (item.currentRelease) {
    const published = releaseDate(item.currentRelease.published_at);
    main.append(element("p", "library-release-meta", `Current v${item.currentRelease.version}${published ? ` · ${published}` : ""}`));
  }
  if (item.storefront_tagline || item.tagline) main.append(element("p", "library-tagline", item.storefront_tagline || item.tagline));
  main.append(element("p", "library-description", item.storefront_description || item.description));
  const side = element("div", "library-side");
  const exactDownload = installationAsset(item.currentRelease);
  if (exactDownload || ((item.release_url || item.href) && item.action)) {
    const action = exactDownload ? `Download v${item.currentRelease.version} ZIP` : item.action;
    const link = element("a", "button button-primary", action);
    link.href = exactDownload?.url || item.release_url || item.href;
    side.append(link);
  }
  (item.historyProducts || []).forEach((product) => {
    const count = product.releases?.length || 0;
    const label = item.kind === "Installable plugin" || item.kind === "Optional integration"
      ? `Details and ${count} ${count === 1 ? "history record" : "history records"}`
      : `${product.name}: files and history`;
    const history = element("a", "library-history-link", label);
    history.href = `plugins/${encodeURIComponent(product.id)}/`;
    side.append(history);
  });

  if (item.description || item.requirements?.length || item.edition || item.license) side.append(createPackageDetails(item));
  if (item.skills?.length) side.append(createSkillDetails(item.skills));
  if (item.downloads?.length) {
    const downloadDetails = createDownloadDetails(item.downloads);
    if (downloadDetails) side.append(downloadDetails);
  }

  row.append(meta, main, side);
  return row;
}

export async function startCatalog() {
  const list = document.querySelector("[data-library-list]");
  const search = document.querySelector("[data-library-search]");
  const filters = [...document.querySelectorAll("[data-library-filter]")];
  const status = document.querySelector("[data-library-status]");
  const empty = document.querySelector("[data-library-empty]");
  const error = document.querySelector("[data-library-error]");
  if (!list || !search || !status) return;

  const initialHash = window.location.hash;
  const state = { job: "all", query: search.value };
  let render = () => {};

  search.addEventListener("input", () => {
    state.query = search.value;
    render();
  });

  filters.forEach((button) => {
    button.addEventListener("click", () => {
      state.job = button.dataset.libraryFilter;
      filters.forEach((candidate) => candidate.setAttribute("aria-pressed", String(candidate === button)));
      render();
    });
  });

  document.querySelectorAll("[data-job-link]").forEach((link) => {
    link.addEventListener("click", () => {
      const job = link.dataset.jobLink;
      const button = filters.find((candidate) => candidate.dataset.libraryFilter === job);
      if (button) button.click();
    });
  });

  try {
    const [libraryResponse, pluginResponse, historyResponse] = await Promise.all([
      fetch("data/tool-library.json?v=phase3-ux8"),
      fetch("data/plugin-releases.json?v=phase3-ux8"),
      fetch("data/release-history.json?v=phase3-release-history-1")
    ]);
    if (!libraryResponse.ok || !pluginResponse.ok) throw new Error("Catalog source unavailable");
    const library = await libraryResponse.json();
    const releases = await pluginResponse.json();
    let releaseHistory = {products: []};
    if (historyResponse.ok) {
      const candidate = await historyResponse.json();
      if (candidate.schema_version === "working-tools.releases.v1" && Array.isArray(candidate.products)) releaseHistory = candidate;
    }
    if (!releaseHistory.products.length) {
      error.textContent = "Release history is temporarily unavailable. Current GitHub release links still work.";
      error.hidden = false;
    }
    const historyById = new Map(releaseHistory.products.map((product) => [product.id, product]));
    const plugins = releases.packages
      .filter((p) => !HIDDEN_PERSONAL_OR_PRIVATE_PACKAGES.has(p.id))
      .map((p) => {
        const historyProduct = historyById.get(p.id);
        const integration = historyProduct?.kind === "integration";
        return {...p, kind: integration ? "Optional integration" : "Installable plugin", access: "public-download", href: integration ? `https://github.com/JonathanKHobson/working-tools-plugins/tree/main/integrations/${p.id}` : `https://github.com/JonathanKHobson/working-tools-plugins/tree/main/plugins/${p.id}`, action: "Open current release", skills: p.skill_names, status: "Released", historyProducts: historyProduct ? [historyProduct] : [], currentRelease: currentRelease(historyProduct)};
      });
    const currentResources = library.items
      .filter((item) => Object.hasOwn(GUIDE_HISTORY_IDS, item.id))
      .map((item) => ({...item, historyProducts: GUIDE_HISTORY_IDS[item.id].map((id) => historyById.get(id)).filter(Boolean)}));
    const items = [...plugins, ...currentResources];

    render = () => {
      const query = state.query.trim().toLowerCase();
      const matches = items.filter((item) => {
        const jobMatch = state.job === "all" || item.jobs.includes(state.job);
        const haystack = [item.name, item.kind, item.tagline, item.description, item.ownership_note, ...(item.skills || []), item.family]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        return jobMatch && (!query || haystack.includes(query));
      });

      const sections = CATALOG_GROUPS.map((group) => {
        const groupItems = matches.filter((item) => groupFor(item) === group.id);
        if (!groupItems.length) return null;
        const section = element("section", "library-group");
        section.setAttribute("aria-labelledby", `library-group-${group.id}`);
        const heading = element("h3", "library-group-title", group.title);
        heading.id = `library-group-${group.id}`;
        section.append(heading, element("p", "library-group-description", group.description));
        section.append(...groupItems.map((item) => createRow(item, library.access_labels)));
        return section;
      }).filter(Boolean);
      list.replaceChildren(...sections);
      status.textContent = `${matches.length} ${matches.length === 1 ? "product" : "products"} shown · ${JOB_LABELS[state.job]}`;
      empty.hidden = matches.length !== 0;
    };


    render();

    if (initialHash) {
      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          document.querySelector(initialHash)?.scrollIntoView();
        });
      });
    }
  } catch (catalogError) {
    console.error(catalogError);
    error.hidden = false;
    status.textContent = "Library unavailable";
  }
}
