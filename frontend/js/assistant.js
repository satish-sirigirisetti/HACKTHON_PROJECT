import { askAssistant } from "./api.js";
import { ensurePageStatus } from "./common.js";
import { readStudentId } from "./profile.js";

const target = document.querySelector("#feature-content");
const status = ensurePageStatus();
document.querySelector("[data-page-description]").textContent = "Ask about careers, skills, and learning resources. Answers use retrieved catalog context; Gemini generation requires a backend-only API key.";
target.classList.remove("planned-panel");
target.classList.add("assistant-workspace");

function showProfileRequired() {
	const message = document.createElement("p");
	message.className = "empty-state";
	message.textContent = "Save a student profile on the dashboard before asking for personalized guidance.";
	const link = document.createElement("a");
	link.href = "dashboard.html";
	link.className = "button button-dark assessment-link";
	link.textContent = "Open dashboard";
	target.replaceChildren(message, link);
}

function addMessage(thread, role, text) {
	const article = document.createElement("article");
	article.className = `assistant-message assistant-${role}`;
	const label = document.createElement("span");
	label.className = "feature-card-badge";
	label.textContent = role === "user" ? "Your question" : "CareerAI response";
	const body = document.createElement("p");
	body.textContent = text;
	article.append(label, body);
	thread.append(article);
	return article;
}

function appendSources(message, sources) {
	if (!sources.length) return;
	const heading = document.createElement("h4");
	heading.className = "assistant-sources-title";
	heading.textContent = "Retrieved context";
	const list = document.createElement("ul");
	list.className = "assistant-sources";
	sources.forEach((source) => {
		const item = document.createElement("li");
		const title = document.createElement("strong");
		title.textContent = `${source.title} · ${source.source_type}`;
		const excerpt = document.createElement("p");
		excerpt.textContent = source.excerpt;
		item.append(title, excerpt);
		if (source.url) {
			const url = new URL(source.url, window.location.href);
			if (url.protocol === "https:" || url.protocol === "http:") {
				const link = document.createElement("a");
				link.href = url.href;
				link.target = "_blank";
				link.rel = "noopener noreferrer";
				link.className = "text-link";
				link.textContent = "Open source ↗";
				item.append(link);
			}
		}
		list.append(item);
	});
	message.append(heading, list);
}

function renderAssistant(studentId) {
	const thread = document.createElement("div");
	thread.className = "assistant-thread";
	const welcome = addMessage(
		thread,
		"assistant",
		"I can retrieve career profiles, required skills, project ideas, and learning resources from the current catalog. Ask a specific question to see the sources used.",
	);
	const welcomeNote = document.createElement("p");
	welcomeNote.className = "assistant-disclosure";
	welcomeNote.textContent = "Responses without a configured Gemini key show retrieved context only; they are not generated answers.";
	welcome.append(welcomeNote);

	const form = document.createElement("form");
	form.className = "assistant-form";
	const label = document.createElement("label");
	label.htmlFor = "assistant-question";
	label.textContent = "Your question";
	const input = document.createElement("textarea");
	input.id = "assistant-question";
	input.name = "message";
	input.required = true;
	input.maxLength = 4000;
	input.rows = 3;
	input.placeholder = "e.g. What skills are required for an ML Engineer?";
	const submit = document.createElement("button");
	submit.className = "button button-dark";
	submit.type = "submit";
	submit.textContent = "Ask CareerAI";
	form.append(label, input, submit);
	form.addEventListener("submit", async (event) => {
		event.preventDefault();
		if (!form.reportValidity()) return;
		const question = input.value.trim();
		if (!question) return;
		addMessage(thread, "user", question);
		submit.disabled = true;
		status.textContent = "Retrieving career context...";
		status.classList.remove("status-error");
		try {
			const result = await askAssistant(studentId, question);
			const response = addMessage(thread, "assistant", result.answer);
			appendSources(response, result.sources);
			status.textContent = result.generation_status === "generated"
				? "Answer generated from retrieved catalog context."
				: "Retrieved sources shown; Gemini generation is not configured.";
			input.value = "";
		} catch (error) {
			addMessage(thread, "assistant", error.message);
			status.textContent = error.message;
			status.classList.add("status-error");
		} finally {
			submit.disabled = false;
		}
	});
	target.replaceChildren(thread, form);
}

const studentId = readStudentId();
if (studentId) renderAssistant(studentId);
else showProfileRequired();