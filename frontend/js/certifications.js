import { getCertifications } from "./api.js";
import { renderCatalogEntries } from "./common.js";

document.querySelector("[data-page-description]").textContent = "Browse structured learning paths from the catalog. Verify provider details and current availability before enrolling.";
const target = document.querySelector("#feature-content");
target.classList.remove("planned-panel");
target.classList.add("feature-grid");
try {
	renderCatalogEntries(target, await getCertifications(), {
		title: "name",
		description: "description",
		subtitle: "provider",
		skills: "skills",
		badge: () => "Learning path",
		sourceUrl: "url",
	});
} catch (error) {
	target.textContent = error.message;
}