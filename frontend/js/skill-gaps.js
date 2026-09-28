import { getCareers, getSkillGaps } from "./api.js";
import { ensurePageStatus } from "./common.js";
import { readStudentId } from "./profile.js";

const target = document.querySelector("#feature-content");
const status = ensurePageStatus();
const description = document.querySelector("[data-page-description]");
description.textContent = "Choose a career to compare its required skills with your current self-reported profile.";

function showMessage(message) {
	const copy = document.createElement("p");
	copy.className = "empty-state";
	copy.textContent = message;
	const link = document.createElement("a");
	link.href = "dashboard.html";
	link.className = "button button-dark assessment-link";
	link.textContent = "Open dashboard";
	target.replaceChildren(copy, link);
}

function renderGaps(results, result) {
	if (!result.gaps.length) {
		const complete = document.createElement("p");
		complete.className = "empty-state";
		complete.textContent = `Your profile currently meets the listed required skill levels for ${result.career_name}. This is a profile comparison, not a job-readiness guarantee.`;
		results.replaceChildren(complete);
		return;
	}
	const list = document.createElement("div");
	list.className = "gap-list";
	result.gaps.forEach((gap) => {
		const row = document.createElement("article");
		row.className = "gap-item";
		const heading = document.createElement("div");
		heading.className = "recommendation-title";
		const name = document.createElement("h3");
		name.textContent = gap.skill_name;
		const priority = document.createElement("span");
		priority.className = "recommendation-score";
		priority.textContent = `Priority ${gap.priority.toFixed(2)}`;
		heading.append(name, priority);
		const track = document.createElement("div");
		track.className = "match-track";
		const fill = document.createElement("div");
		fill.className = "match-fill gap-fill";
		fill.style.width = `${Math.max(0, Math.min(100, gap.proficiency * 100))}%`;
		track.append(fill);
		const detail = document.createElement("p");
		detail.className = "recommendation-skills";
		detail.textContent = `Self-reported level: ${Math.round(gap.proficiency * 100)}% · Requirement importance: ${gap.importance}`;
		row.append(heading, track, detail);
		gap.resources.forEach((resource) => {
			if (!resource.url) return;
			const url = new URL(resource.url, window.location.href);
			if (url.protocol !== "https:" && url.protocol !== "http:") return;
			const link = document.createElement("a");
			link.className = "text-link resource-link";
			link.href = url.href;
			link.target = "_blank";
			link.rel = "noopener noreferrer";
			link.textContent = `${resource.title} · ${resource.provider} ↗`;
			row.append(link);
		});
		list.append(row);
	});
	results.replaceChildren(list);
}

async function initialize() {
	const studentId = readStudentId();
	if (!studentId) {
		showMessage("Save a student profile on the dashboard before analyzing skill gaps.");
		return;
	}
	try {
		const careers = await getCareers();
		const form = document.createElement("form");
		form.className = "feature-filter-form";
		const label = document.createElement("label");
		label.textContent = "Career direction";
		const select = document.createElement("select");
		select.name = "career_id";
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
		const button = document.createElement("button");
		button.className = "button button-dark";
		button.type = "submit";
		button.textContent = "Analyze gaps";
		form.append(label, button);
		const results = document.createElement("div");
		results.className = "gap-results";
		target.replaceChildren(form, results);
		form.addEventListener("submit", async (event) => {
			event.preventDefault();
			if (!form.reportValidity()) return;
			button.disabled = true;
			status.textContent = "Comparing your skills with career requirements...";
			try {
				renderGaps(results, await getSkillGaps(studentId, select.value));
				status.textContent = "Skill-gap analysis complete.";
			} catch (error) {
				status.textContent = error.message;
				status.classList.add("status-error");
			} finally {
				button.disabled = false;
			}
		});
	} catch (error) {
		showMessage(error.message);
	}
}

initialize();