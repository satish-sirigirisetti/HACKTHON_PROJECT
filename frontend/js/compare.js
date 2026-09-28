import { compareCareers, getCareers } from "./api.js";
import { ensurePageStatus } from "./common.js";
import { readStudentId } from "./profile.js";

const target = document.querySelector("#feature-content");
const status = ensurePageStatus();
document.querySelector("[data-page-description]").textContent = "Compare required skills across roles and see how your current self-reported profile aligns. This is profile context, not a hiring prediction.";
target.classList.remove("planned-panel");
target.classList.add("compare-content");

function addCareerSelect(form, labelText, careers, name) {
	const label = document.createElement("label");
	label.textContent = labelText;
	const select = document.createElement("select");
	select.name = name;
	select.required = true;
	const prompt = document.createElement("option");
	prompt.value = "";
	prompt.textContent = "Choose a career";
	select.append(prompt);
	careers.forEach((career) => {
		const option = document.createElement("option");
		option.value = career.id;
		option.textContent = career.name;
		select.append(option);
	});
	label.append(select);
	form.append(label);
	return select;
}

function renderComparison(result) {
	const common = document.createElement("div");
	common.className = "comparison-common";
	const commonTitle = document.createElement("strong");
	commonTitle.textContent = "Shared required skills";
	const commonSkills = document.createElement("p");
	commonSkills.textContent = result.shared_required_skills.join(", ") || "No shared required skills in this catalog comparison.";
	common.append(commonTitle, commonSkills);

	const columns = document.createElement("div");
	columns.className = "comparison-columns";
	result.careers.forEach((career) => {
		const column = document.createElement("article");
		column.className = "comparison-column";
		const heading = document.createElement("div");
		heading.className = "feature-card-badge";
		heading.textContent = career.category;
		const title = document.createElement("h3");
		title.textContent = career.name;
		const description = document.createElement("p");
		description.className = "comparison-description";
		description.textContent = career.description;
		column.append(heading, title, description);
		career.required_skills.forEach((skill) => {
			const row = document.createElement("div");
			row.className = "comparison-skill";
			const label = document.createElement("div");
			label.className = "comparison-skill-label";
			const name = document.createElement("strong");
			name.textContent = skill.name;
			const level = result.student_skill_levels[skill.name] ?? 0;
			const value = document.createElement("span");
			value.textContent = `${skill.required ? "Required" : "Optional"} · ${Math.round(level * 100)}%`;
			label.append(name, value);
			const track = document.createElement("div");
			track.className = "match-track";
			const fill = document.createElement("div");
			fill.className = "match-fill";
			fill.style.width = `${Math.max(0, Math.min(100, level * 100))}%`;
			track.append(fill);
			row.append(label, track);
			column.append(row);
		});
		columns.append(column);
	});
	target.querySelector(".comparison-results")?.replaceChildren(common, columns);
}

async function initialize() {
	const studentId = readStudentId();
	if (!studentId) {
		target.textContent = "Save a student profile on the dashboard before comparing career fit.";
		return;
	}
	try {
		const careers = await getCareers();
		const form = document.createElement("form");
		form.className = "feature-filter-form compare-form";
		const first = addCareerSelect(form, "First career", careers, "career_one");
		const second = addCareerSelect(form, "Second career", careers, "career_two");
		const button = document.createElement("button");
		button.className = "button button-dark";
		button.type = "submit";
		button.textContent = "Compare careers";
		form.append(button);
		const results = document.createElement("div");
		results.className = "comparison-results";
		target.replaceChildren(form, results);
		form.addEventListener("submit", async (event) => {
			event.preventDefault();
			if (!form.reportValidity()) return;
			if (first.value === second.value) {
				status.textContent = "Choose two different careers to compare.";
				status.classList.add("status-error");
				return;
			}
			button.disabled = true;
			status.textContent = "Comparing career requirements...";
			status.classList.remove("status-error");
			try {
				renderComparison(await compareCareers(studentId, [first.value, second.value]));
				status.textContent = "Career comparison updated.";
			} catch (error) {
				status.textContent = error.message;
				status.classList.add("status-error");
			} finally {
				button.disabled = false;
			}
		});
	} catch (error) {
		target.textContent = error.message;
	}
}

initialize();