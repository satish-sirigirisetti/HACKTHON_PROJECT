import { getInternships } from "./api.js";
import { renderCatalogEntries } from "./common.js";

document.querySelector("[data-page-description]").textContent = "These entries are sample records for interface development, not live vacancies. No applications or employer listings are connected.";
const target = document.querySelector("#feature-content");
target.classList.remove("planned-panel");
target.classList.add("feature-grid");
try {
	renderCatalogEntries(target, await getInternships(), {
		title: "title",
		description: "description",
		subtitle: "organization",
		skills: "skills",
		badge: (entry) => entry.is_sample ? "Sample listing" : "Listing",
		sourceUrl: "source_url",
	});
} catch (error) {
	target.textContent = error.message;
}