const navigationGroups = [
  { label: "Workspace", links: [["dashboard.html", "Dashboard", "D"], ["assessment.html", "Assessment", "A"], ["careers.html", "Career catalog", "C"], ["skill-gaps.html", "Skill gaps", "S"], ["roadmap.html", "Roadmap", "R"]] },
  { label: "Build experience", links: [["projects.html", "Projects", "P"], ["certifications.html", "Certifications", "C"], ["internships.html", "Internships", "I"]] },
  { label: "Explore", links: [["trends.html", "Industry trends", "T"], ["compare.html", "Compare careers", "↔"], ["simulator.html", "What-if simulator", "?"], ["assistant.html", "Career assistant", "AI"]] },
];

export function mountSidebar() {
  const mount = document.querySelector("#sidebar-mount");
  if (!mount) return;
  const currentPage = document.body.dataset.page;
  const brand = document.createElement("a");
  brand.className = "sidebar-brand";
  brand.href = "index.html";
  brand.innerHTML = '<span class="brand-mark">C</span>career<span class="brand-ai">ai</span>';
  mount.append(brand);

  navigationGroups.forEach((group) => {
    const label = document.createElement("p");
    label.className = "sidebar-group-label";
    label.textContent = group.label;
    mount.append(label);
    const nav = document.createElement("nav");
    nav.className = "sidebar-nav";
    nav.setAttribute("aria-label", group.label);
    group.links.forEach(([href, title, glyph]) => {
      const link = document.createElement("a");
      link.className = "sidebar-link";
      link.href = href;
      if (href.replace(".html", "") === currentPage) link.setAttribute("aria-current", "page");
      const icon = document.createElement("span");
      icon.className = "sidebar-glyph";
      icon.setAttribute("aria-hidden", "true");
      icon.textContent = glyph;
      const text = document.createElement("span");
      text.textContent = title;
      link.append(icon, text);
      nav.append(link);
    });
    mount.append(nav);
  });

  const footer = document.createElement("p");
  footer.className = "sidebar-bottom";
  footer.textContent = "CareerAI · Student workspace";
  mount.append(footer);
  
  const pageDescription = document.querySelector("[data-page-description]");
  if (pageDescription) pageDescription.textContent = document.body.dataset.description || "";
}

export function renderPlannedState(title, description) {
  const target = document.querySelector("#feature-content");
  if (!target) return;
  const label = document.createElement("span");
  label.className = "planned-label";
  label.textContent = "Planned module";
  const heading = document.createElement("h3");
  heading.textContent = title;
  const copy = document.createElement("p");
  copy.textContent = description;
  target.replaceChildren(label, heading, copy);
}

export function renderCatalogEntries(target, entries, config) {
  if (!entries.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No catalog entries are available yet. Run the seed script from the project directory.";
    target.replaceChildren(empty);
    return;
  }
  const fragment = document.createDocumentFragment();
  entries.forEach((entry) => {
    const card = document.createElement("article");
    card.className = "feature-card";
    const badge = document.createElement("span");
    badge.className = "feature-card-badge";
    badge.textContent = config.badge(entry);
    const title = document.createElement("h3");
    title.textContent = entry[config.title];
    const description = document.createElement("p");
    description.textContent = entry[config.description];
    card.append(badge, title, description);
    if (config.subtitle && entry[config.subtitle]) {
      const subtitle = document.createElement("p");
      subtitle.className = "feature-card-subtitle";
      subtitle.textContent = entry[config.subtitle];
      card.append(subtitle);
    }
    if (config.skills) {
      const skills = entry[config.skills] || [];
      const list = document.createElement("ul");
      list.className = "skill-tags";
      skills.forEach((name) => {
        const item = document.createElement("li");
        item.textContent = name;
        list.append(item);
      });
      if (skills.length) card.append(list);
    }
    if (config.sourceUrl && entry[config.sourceUrl]) {
      const url = new URL(entry[config.sourceUrl], window.location.href);
      if (url.protocol === "https:" || url.protocol === "http:") {
        const link = document.createElement("a");
        link.className = "text-link feature-card-link";
        link.href = url.href;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.textContent = "Open resource ↗";
        card.append(link);
      }
    }
    fragment.append(card);
  });
  target.replaceChildren(fragment);
}

export function ensurePageStatus() {
  let status = document.querySelector("#feature-status");
  if (status) return status;
  const main = document.querySelector(".dashboard-main");
  if (!main) return null;
  status = document.createElement("p");
  status.id = "feature-status";
  status.className = "api-status";
  status.setAttribute("role", "status");
  status.setAttribute("aria-live", "polite");
  main.append(status);
  return status;
}

mountSidebar();