import { getProjects } from "./api.js";
import { renderCatalogEntries } from "./common.js";

document.querySelector("[data-page-description]").textContent = "Browse project ideas mapped to the skills they let you practice. These are starting points, not assigned coursework.";
const target = document.querySelector("#feature-content");
target.classList.remove("planned-panel");
target.classList.add("feature-grid");
try {
	renderCatalogEntries(target, await getProjects(), {
		title: "title",
		description: "description",
		skills: "skill_names",
		badge: () => "Project idea",
		sourceUrl: "source_url",
	});
} catch (error) {
	target.textContent = error.message;
}