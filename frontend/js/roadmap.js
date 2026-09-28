import { generateRoadmap, getCareers, getRoadmap, updateRoadmapItem } from "./api.js";
import { ensurePageStatus } from "./common.js";
import { readStudentId } from "./profile.js";

const target = document.querySelector("#feature-content");
const status = ensurePageStatus();
document.querySelector("[data-page-description]").textContent = "Generate an ordered learning plan from a career's required skills, then track each step as you complete it.";

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

function renderRoadmap(roadmap) {
	if (!roadmap) {
		const empty = document.createElement("p");
		empty.className = "empty-state roadmap-empty";
		empty.textContent = "Choose a career above to generate your first learning plan.";
		target.append(empty);
		return;
	}
	const section = document.createElement("section");
	section.className = "roadmap-view";
	const heading = document.createElement("div");
	heading.className = "roadmap-heading";
	const title = document.createElement("h3");
	title.textContent = roadmap.title;
	const progress = document.createElement("p");
	progress.className = "panel-description";
	const completedCount = roadmap.items.filter((item) => item.completed).length;
	progress.textContent = `${completedCount} of ${roadmap.items.length} steps complete`;
	heading.append(title, progress);
	section.append(heading);
	if (!roadmap.items.length) {
		const complete = document.createElement("p");
		complete.className = "empty-state";
		complete.textContent = "Your current profile meets the listed skill levels for this career. No gap-based steps were generated.";
		section.append(complete);
	}
	const list = document.createElement("ol");
	list.className = "roadmap-list";
	roadmap.items.forEach((item) => {
		const row = document.createElement("li");
		row.className = "roadmap-step";
		const label = document.createElement("label");
		label.className = "roadmap-check";
		const checkbox = document.createElement("input");
		checkbox.type = "checkbox";
		checkbox.checked = item.completed;
		checkbox.setAttribute("aria-label", `Mark ${item.title} ${item.completed ? "incomplete" : "complete"}`);
		const title = document.createElement("strong");
		title.textContent = item.title;
		label.append(checkbox, title);
		const copy = document.createElement("p");
		copy.textContent = item.description;
		row.append(label, copy);
		if (item.resource?.url) {
			const link = document.createElement("a");
			link.href = item.resource.url;
			link.target = "_blank";
			link.rel = "noopener noreferrer";
			link.className = "text-link resource-link";
			link.textContent = `${item.resource.title} · ${item.resource.provider} ↗`;
			row.append(link);
		}
		checkbox.addEventListener("change", async () => {
			checkbox.disabled = true;
			try {
				const updated = await updateRoadmapItem(studentId, roadmap.id, item.id, checkbox.checked);
				target.querySelector(".roadmap-view")?.remove();
				renderRoadmap(updated);
			} catch (error) {
				checkbox.checked = item.completed;
				status.textContent = error.message;
				status.classList.add("status-error");
			}
		});
		list.append(row);
	});
	section.append(list);
	target.append(section);
}

const studentId = readStudentId();
if (!studentId) {
	showMessage("Save a student profile on the dashboard before creating a roadmap.");
} else {
	try {
		const careers = await getCareers();
		const form = document.createElement("form");
		form.className = "feature-filter-form";
		const label = document.createElement("label");
		label.textContent = "Target career";
		const select = document.createElement("select");
		select.required = true;
		select.name = "career_id";
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
		button.textContent = "Generate roadmap";
		form.append(label, button);
		target.replaceChildren(form);
		const previous = await getRoadmap(studentId);
		if (previous) {
			const option = [...select.options].find((item) => item.textContent === previous.target_role);
			if (option) select.value = option.value;
			renderRoadmap(previous);
		} else {
			renderRoadmap(null);
		}
		form.addEventListener("submit", async (event) => {
			event.preventDefault();
			if (!form.reportValidity()) return;
			button.disabled = true;
			status.textContent = "Building a roadmap from required skill gaps...";
			try {
				const roadmap = await generateRoadmap(studentId, select.value);
				target.querySelector(".roadmap-view")?.remove();
				renderRoadmap(roadmap);
				status.textContent = "Roadmap saved.";
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