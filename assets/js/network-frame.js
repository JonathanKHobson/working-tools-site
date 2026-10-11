const basePath = window.location.hostname === "jonathankhobson.github.io" ? "/compass-suite/" : "/";

const frameMarkup = `
  <div class="network-nav-inner">
    <a class="network-nav-brand" href="https://working-tools.jkylehobson.chatgpt.site/">
      <img class="network-nav-mark" data-network-brand-mark src="${basePath}assets/brand/working-tools-mark-64.png" width="32" height="32" alt="">
      <span class="network-nav-wordmark">Working Tools<span aria-hidden="true">.</span></span>
    </a>
    <button class="network-nav-toggle" type="button" aria-expanded="false" aria-controls="network-nav-menu" data-network-nav-toggle>Menu</button>
    <div class="network-nav-links" id="network-nav-menu" data-network-nav-links>
      <a class="network-nav-link" data-network-path="/" href="https://working-tools.jkylehobson.chatgpt.site/#library">Plugin catalog</a>
      <a class="network-nav-link" href="https://github.com/JonathanKHobson/working-tools-plugins">Plugin source &amp; releases</a>
      <a class="network-nav-link" data-network-path="/behind-the-tools/" href="https://working-tools.jkylehobson.chatgpt.site/behind-the-tools/">Behind the tools</a>
      <a class="network-nav-link" data-network-path="/legacy/" href="https://working-tools.jkylehobson.chatgpt.site/legacy/">Legacy library</a>
      <a class="network-nav-link" href="https://jonathankhobson.github.io/shareables/s/understanding-ai-2026/">AI Basics</a>
      <a class="network-nav-link" href="https://jonathankhobson.github.io/what-is-an-mcp/">MCP Basics</a>
    </div>
  </div>`;

document
  .querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]')
  .forEach((link) => link.remove());

const favicon = document.createElement("link");
favicon.rel = "icon";
favicon.type = "image/png";
favicon.sizes = "32x32";
favicon.href = `${basePath}assets/brand/working-tools-favicon-32.png`;
document.head.append(favicon);

const touchIcon = document.createElement("link");
touchIcon.rel = "apple-touch-icon";
touchIcon.sizes = "180x180";
touchIcon.href = `${basePath}assets/brand/working-tools-icon-180.png`;
document.head.append(touchIcon);

let networkNav = document.querySelector("[data-network-nav]");

if (!networkNav) {
  networkNav = document.createElement("nav");
  networkNav.className = "network-nav";
  networkNav.dataset.networkNav = "";
  networkNav.setAttribute("aria-label", "Working Tools network");
  networkNav.innerHTML = frameMarkup;

  const legacyFrame = document.querySelector(
    "body > .site-nav, body > .site-header, body > .network-bar, body > .bar",
  );
  const sharedFrame = document.querySelector(".kh-network");
  if (sharedFrame) {
    sharedFrame.insertAdjacentElement("afterend", networkNav);
    legacyFrame?.remove();
  } else if (legacyFrame) {
    legacyFrame.replaceWith(networkNav);
  } else {
    const skipLink = document.querySelector("body > .skip-link");
    if (skipLink) skipLink.insertAdjacentElement("afterend", networkNav);
    else document.body.insertAdjacentElement("afterbegin", networkNav);
  }
}

if (networkNav) {
  const toggle = networkNav.querySelector("[data-network-nav-toggle]");
  const links = networkNav.querySelector("[data-network-nav-links]");
  const currentPath = window.location.pathname
    .replace(/^\/shareables-redesign\//, "/shareables/")
    .replace(/^\/compass-suite\//, "/")
    .replace(/\/+$/, "/");
  const legacyPaths = new Set(["/critical-compass/", "/prompt-compass/", "/ux-heuristic-compass/", "/job-application-compass/", "/creative-writing-studio/", "/marketing-social-studio/", "/career-grants-studio/", "/ttrpg-gm-director/", "/ux-design-toolkit/", "/builder-tools/"]);

  networkNav.querySelectorAll("[data-network-path]").forEach((link) => {
    const path = link.dataset.networkPath;
    const isLibrary = path === "/" && currentPath === "/";
    const isCurrent = path !== "/" && currentPath.startsWith(path);
    const isLegacy = path === "/legacy/" && legacyPaths.has(currentPath);
    if (isLibrary || isCurrent || isLegacy) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });

  if (!networkNav.querySelector('[aria-current="page"]')) {
    networkNav
      .querySelector('[data-network-path="/"]')
      ?.setAttribute("aria-current", "page");
  }

  const close = () => {
    if (!toggle || !links) return;
    toggle.setAttribute("aria-expanded", "false");
    links.classList.remove("is-open");
  };

  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      links.classList.toggle("is-open", open);
    });
    links.querySelectorAll("a").forEach((link) => link.addEventListener("click", close));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") close();
    });
    document.addEventListener("click", (event) => {
      if (!networkNav.contains(event.target)) close();
    });
  }

  networkNav.classList.add("network-nav-ready");
}
