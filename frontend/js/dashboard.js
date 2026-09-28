import { createStudent, getRecommendations, getStudent, updateStudent } from "./api.js";
import { forgetStudentId, readStudentId, rememberStudentId, splitProfileList } from "./profile.js";
import "./common.js";

const form = document.querySelector("#profile-form");
const profileStatus = document.querySelector("#profile-status");
const summary = document.querySelector("#profile-summary");
const recommendationsList = document.querySelector("#recommendations-list");
const chartEmpty = document.querySelector("#chart-empty");
const apiStatus = document.querySelector("#api-status");
let currentStudent = null;
let skillChart = null;

function setStatus(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("status-error", isError);
}

function fillForm(student) {
  form.elements.name.value = student.name || "";
  form.elements.email.value = student.email || "";
  form.elements.major.value = student.major || "";
  form.elements.graduation_year.value = student.graduation_year || "";
  form.elements.target_role.value = student.target_role || "";
  form.elements.skills.value = (student.skills || []).map((skill) => skill.name).join(", ");
  form.elements.interests.value = (student.interests || []).join(", ");
}

function collectProfile() {
  const formData = new FormData(form);
  const oldSkills = new Map((currentStudent?.skills || []).map((skill) => [skill.name.toLocaleLowerCase(), skill.proficiency]));
  const skills = splitProfileList(String(formData.get("skills") || "")).map((name) => ({
    name,
    proficiency: oldSkills.get(name.toLocaleLowerCase()) ?? 0.5,
  }));
  const yearText = String(formData.get("graduation_year") || "").trim();
  return {
    name: String(formData.get("name") || "").trim(),
    email: String(formData.get("email") || "").trim(),
    major: String(formData.get("major") || "").trim() || null,
    graduation_year: yearText ? Number(yearText) : null,
    target_role: String(formData.get("target_role") || "").trim() || null,
    skills,
    interests: splitProfileList(String(formData.get("interests") || "")),
    soft_skills: currentStudent?.soft_skills || [],
    learning_goals: currentStudent?.learning_goals || [],
    academic_performance: currentStudent?.academic_performance || {},
  };
}

function renderSkills(student) {
  summary.textContent = student.skills?.length
    ? `${student.skills.length} self-reported skill${student.skills.length === 1 ? "" : "s"} · ${student.major || "Field of study not set"}`
    : "Profile saved · add skills to see your skill snapshot";
  const canvas = document.querySelector("#skills-chart");
  if (skillChart) skillChart.destroy();
  const skills = student.skills || [];
  chartEmpty.hidden = skills.length > 0;
  canvas.hidden = skills.length === 0;
  if (!skills.length || !window.Chart) return;
  skillChart = new window.Chart(canvas, {
    type: "bar",
    data: {
      labels: skills.map((skill) => skill.name),
      datasets: [{
        data: skills.map((skill) => skill.proficiency),
        backgroundColor: skills.map((_, index) => index % 3 === 1 ? "#e5745b" : "#67876b"),
        borderRadius: 3,
        barThickness: 13,
      }],
    },
    options: {
      indexAxis: "y",
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: (item) => `${Math.round(item.raw * 100)}% self-reported` } } },
      scales: {
        x: { min: 0, max: 1, ticks: { stepSize: 0.25, callback: (value) => `${Math.round(value * 100)}%` }, grid: { color: "#edf0eb" }, border: { display: false } },
        y: { grid: { display: false }, border: { display: false } },
      },
    },
  });
}

function renderRecommendations(recommendations) {
  if (!recommendations.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No career requirements are available yet. Seed the career catalog and add skills to your profile.";
    recommendationsList.replaceChildren(empty);
    return;
  }
  const fragment = document.createDocumentFragment();
  recommendations.slice(0, 6).forEach((item) => {
    const card = document.createElement("article");
    card.className = "recommendation-item";
    const title = document.createElement("div");
    title.className = "recommendation-title";
    const heading = document.createElement("h3");
    heading.textContent = item.career_name;
    const score = document.createElement("span");
    score.className = "recommendation-score";
    score.textContent = `${Math.round(item.match_score * 100)}% overlap`;
    title.append(heading, score);
    const track = document.createElement("div");
    track.className = "match-track";
    track.setAttribute("role", "img");
    track.setAttribute("aria-label", `${Math.round(item.match_score * 100)} percent weighted skills overlap`);
    const fill = document.createElement("div");
    fill.className = "match-fill";
    fill.style.width = `${Math.max(0, Math.min(100, item.match_score * 100))}%`;
    track.append(fill);
    const skillDetail = document.createElement("p");
    skillDetail.className = "recommendation-skills";
    skillDetail.textContent = `Matched: ${item.matched_skills.join(", ") || "none yet"} | Missing: ${item.missing_skills.join(", ") || "none"}`;
    card.append(title, track, skillDetail);
    fragment.append(card);
  });
  recommendationsList.replaceChildren(fragment);
}

async function loadRecommendations(studentId) {
  try {
    renderRecommendations(await getRecommendations(studentId));
  } catch (error) {
    setStatus(apiStatus, error.message, true);
  }
}

async function loadProfile() {
  const studentId = readStudentId();
  if (!studentId) return;
  try {
    currentStudent = await getStudent(studentId);
    fillForm(currentStudent);
    renderSkills(currentStudent);
    setStatus(profileStatus, "Profile loaded from the CareerAI API.");
    await loadRecommendations(studentId);
  } catch (error) {
    if (error.message === "Student not found") forgetStudentId();
    setStatus(apiStatus, error.message, true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const submitButton = form.querySelector("button[type=submit]");
  submitButton.disabled = true;
  setStatus(profileStatus, "Saving profile...");
  setStatus(apiStatus, "");
  try {
    const payload = collectProfile();
    currentStudent = readStudentId()
      ? await updateStudent(readStudentId(), payload)
      : await createStudent(payload);
    rememberStudentId(currentStudent.id);
    fillForm(currentStudent);
    renderSkills(currentStudent);
    setStatus(profileStatus, "Profile saved to the CareerAI database.");
    await loadRecommendations(currentStudent.id);
  } catch (error) {
    setStatus(profileStatus, error.message, true);
  } finally {
    submitButton.disabled = false;
  }
});

loadProfile();