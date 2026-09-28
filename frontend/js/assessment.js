import { getAssessmentQuestions, getStudent, submitAssessment } from "./api.js";
import "./common.js";
import { forgetStudentId, readStudentId } from "./profile.js";

const target = document.querySelector("#feature-content");
const status = document.querySelector("#assessment-status");
const proficiencyFormatter = new Intl.NumberFormat(undefined, { style: "percent", maximumFractionDigits: 0 });

function showMessage(title, message, linkText, linkHref) {
	const heading = document.createElement("h3");
	heading.textContent = title;
	const copy = document.createElement("p");
	copy.textContent = message;
	const link = document.createElement("a");
	link.className = "button button-dark assessment-link";
	link.href = linkHref;
	link.textContent = linkText;
	target.replaceChildren(heading, copy, link);
}

function renderQuestions(questions, studentId) {
	const intro = document.createElement("p");
	intro.className = "assessment-instructions";
	intro.textContent = "Choose the option that best reflects your current experience. These ratings are self-reported, not exam scores.";

	const form = document.createElement("form");
	form.id = "assessment-form";
	form.className = "assessment-form";

	questions.forEach((question, index) => {
		const fieldset = document.createElement("fieldset");
		fieldset.className = "assessment-question";
		const legend = document.createElement("legend");
		legend.textContent = `${String(index + 1).padStart(2, "0")} / ${String(questions.length).padStart(2, "0")}  ·  ${question.skill_name}`;
		const prompt = document.createElement("p");
		prompt.className = "question-prompt";
		prompt.textContent = question.prompt;
		const options = document.createElement("div");
		options.className = "rating-options";
		options.setAttribute("role", "radiogroup");
		options.setAttribute("aria-label", `${question.skill_name} self-rating`);

		question.options.forEach((option) => {
			const label = document.createElement("label");
			label.className = "rating-option";
			const input = document.createElement("input");
			input.type = "radio";
			input.name = `question-${question.id}`;
			input.value = String(option.proficiency);
			input.required = true;
			const text = document.createElement("span");
			text.textContent = option.label;
			const value = document.createElement("small");
			value.textContent = proficiencyFormatter.format(option.proficiency);
			label.append(input, text, value);
			options.append(label);
		});

		fieldset.append(legend, prompt, options);
		form.append(fieldset);
	});

	const actions = document.createElement("div");
	actions.className = "assessment-actions";
	const submit = document.createElement("button");
	submit.className = "button button-dark";
	submit.type = "submit";
	submit.textContent = "Save skill ratings";
	actions.append(submit);
	form.append(actions);
	form.addEventListener("submit", (event) => handleSubmit(event, form, questions, studentId, submit));
	target.replaceChildren(intro, form);
}

async function handleSubmit(event, form, questions, studentId, submitButton) {
	event.preventDefault();
	if (!form.reportValidity()) return;
	submitButton.disabled = true;
	status.textContent = "Saving your self-assessment...";
	status.classList.remove("status-error");
	const formData = new FormData(form);
	const answers = questions.map((question) => ({
		question_id: question.id,
		proficiency: Number(formData.get(`question-${question.id}`)),
	}));
	try {
		const result = await submitAssessment({ student_id: Number(studentId), answers });
		const score = document.createElement("strong");
		score.className = "assessment-result-score";
		score.textContent = proficiencyFormatter.format(result.score);
		const message = document.createElement("p");
		message.textContent = `Self-reported snapshot saved for ${result.skills_updated.join(", ")}. Your dashboard recommendations now use these ratings.`;
		const resultPanel = document.createElement("div");
		resultPanel.className = "assessment-result";
		resultPanel.setAttribute("role", "status");
		resultPanel.append(score, message);
		target.querySelector(".assessment-result")?.remove();
		target.prepend(resultPanel);
		status.textContent = "Assessment saved to your profile.";
	} catch (error) {
		status.textContent = error.message;
		status.classList.add("status-error");
	} finally {
		submitButton.disabled = false;
	}
}

async function initializeAssessment() {
	const studentId = readStudentId();
	if (!studentId) {
		showMessage(
			"Create your student profile first",
			"Assessment ratings are saved to a student profile so they can inform your career matches.",
			"Go to dashboard",
			"dashboard.html",
		);
		return;
	}
	try {
		await getStudent(studentId);
		const questions = await getAssessmentQuestions();
		if (!questions.length) {
			showMessage(
				"Assessment questions are not seeded yet",
				"Load the question catalog, then return here to complete your self-assessment.",
				"Go to dashboard",
				"dashboard.html",
			);
			return;
		}
		renderQuestions(questions, studentId);
	} catch (error) {
		if (error.message === "Student not found") {
			forgetStudentId();
			showMessage(
				"Student profile not found",
				"Create or save your profile before starting an assessment.",
				"Go to dashboard",
				"dashboard.html",
			);
			return;
		}
		showMessage("Could not load the assessment", error.message, "Try again", "assessment.html");
	}
}

initializeAssessment();