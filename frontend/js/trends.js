import { getTrends } from "./api.js";
import { renderCatalogEntries } from "./common.js";

document.querySelector("[data-page-description]").textContent = "Sample placeholders are labeled below. No hiring, salary, demand, or employment statistics are currently shown.";
const target = document.querySelector("#feature-content");
target.classList.remove("planned-panel");
target.classList.add("feature-grid");
try {
	renderCatalogEntries(target, await getTrends(), {
		title: "topic",
		description: "summary",
		subtitle: "source",
		badge: (entry) => entry.is_sample ? "Sample only" : "Sourced observation",
	});
} catch (error) {
	target.textContent = error.message;
}