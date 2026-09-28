import { getSkills, simulateCareer } from "./api.js";
import { ensurePageStatus } from "./common.js";
import { readStudentId } from "./profile.js";

const target = document.querySelector("#feature-content");
const status = ensurePageStatus();
document.querySelector("[data-page-description]").textContent = "Add hypothetical skill levels to see how catalog-based career matches could change. Scenario ratings are not saved to your profile.";
target.classList.remove("planned-panel");
target.classList.add("simulator-content");

function renderScenario(list, skills) {
	list.replaceChildren();
	skills.forEach((skill, index) => {
		const item = document.createElement("li");
		item.className = "scenario-skill";
		const name = document.createElement("strong");
		name.textContent = skill.name;
		const level = document.createElement("span");
		level.textContent = `${Math.round(skill.proficiency * 100)}%`;
		const remove = document.createElement("button");
		remove.className = "scenario-remove";
		remove.type = "button";
		remove.title = `Remove ${skill.name}`;
		remove.setAttribute("aria-label", `Remove ${skill.name}`);
		remove.textContent = "×";
		remove.addEventListener("click", () => {
			skills.splice(index, 1);
			renderScenario(list, skills);
		});
		item.append(name, level, remove);
		list.append(item);
	});
}

function renderRankings(container, result) {
	const columns = document.createElement("div");
	columns.className = "scenario-columns";
	[["Current profile", result.baseline], ["With hypothetical skills", result.simulated]].forEach(([title, careers]) => {
		const column = document.createElement("section");
		column.className = "scenario-column";
		const heading = document.createElement("h3");
		heading.textContent = title;
		column.append(heading);
		careers.slice(0, 6).forEach((career, index) => {
			const item = document.createElement("div");
			item.className = "scenario-rank";
			const name = document.createElement("strong");
			name.textContent = `${index + 1}. ${career.career_name}`;
			const score = document.createElement("span");
			score.textContent = `${Math.round(career.match_score * 100)}%`;
			item.append(name, score);
			column.append(item);
		});
		columns.append(column);
	});
	const note = document.createElement("p");
	note.className = "panel-description";
	note.textContent = result.method;
	container.replaceChildren(columns, note);
}

async function initialize() {
	const studentId = readStudentId();
	if (!studentId) {
		target.textContent = "Save a student profile on the dashboard before running a what-if scenario.";
		return;
	}
	try {
		const skills = await getSkills();
		const form = document.createElement("form");
		form.className = "scenario-builder";
		const skillLabel = document.createElement("label");
		skillLabel.textContent = "Skill to add or adjust";
		const select = document.createElement("select");
		select.required = true;
		select.name = "skill_id";
		skills.forEach((skill) => {
			const option = document.createElement("option");
			option.value = skill.name;
			option.textContent = `${skill.name} · ${skill.category}`;
			select.append(option);
		});
		skillLabel.append(select);
		const proficiencyLabel = document.createElement("label");
		proficiencyLabel.textContent = "Hypothetical proficiency";
		const range = document.createElement("input");
		range.type = "range";
		range.min = "0";
		range.max = "1";
		range.step = "0.25";
		range.value = "0.75";
		const output = document.createElement("output");
		output.textContent = "75%";
		range.addEventListener("input", () => {
			output.textContent = `${Math.round(Number(range.value) * 100)}%`;
		});
		proficiencyLabel.append(range, output);
		const add = document.createElement("button");
		add.className = "button button-light";
		add.type = "button";
		add.textContent = "Add scenario skill";
		form.append(skillLabel, proficiencyLabel, add);

		const scenario = [];
		const list = document.createElement("ul");
		list.className = "scenario-skill-list";
		const run = document.createElement("button");
		run.className = "button button-dark";
		run.type = "button";
		run.textContent = "Compare recommendations";
		run.disabled = true;
		const results = document.createElement("div");
		results.className = "scenario-results";
		add.addEventListener("click", () => {
			const name = select.value;
			const existing = scenario.find((item) => item.name.toLocaleLowerCase() === name.toLocaleLowerCase());
			if (existing) existing.proficiency = Number(range.value);
			else scenario.push({ name, proficiency: Number(range.value) });
			renderScenario(list, scenario);
			run.disabled = scenario.length === 0;
		});
		run.addEventListener("click", async () => {
			run.disabled = true;
			status.textContent = "Recalculating recommendations for this scenario...";
			status.classList.remove("status-error");
			try {
				const result = await simulateCareer(studentId, scenario);
				renderRankings(results, result);
				status.textContent = "Scenario comparison complete. Your profile was not changed.";
			} catch (error) {
				status.textContent = error.message;
				status.classList.add("status-error");
			} finally {
				run.disabled = scenario.length === 0;
			}
		});
		target.replaceChildren(form, list, run, results);
	} catch (error) {
		target.textContent = error.message;
	}
}

initialize();