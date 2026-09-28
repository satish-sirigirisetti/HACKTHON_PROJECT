const localApiBase = `${window.location.protocol}//${window.location.hostname}:8000/api`;
const defaultApiBase = window.location.port === "5500" ? localApiBase : "/api";
const API_BASE = (window.CAREERAI_API_BASE || defaultApiBase).replace(/\/$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch {
    throw new Error("Could not reach the CareerAI API. Start the backend and try again.");
  }
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail;
    throw new Error(typeof detail === "string" ? detail : `Request failed (${response.status}).`);
  }
  return payload;
}

export function getStudent(studentId) {
  return request(`/students/${encodeURIComponent(studentId)}`);
}

export function createStudent(student) {
  return request("/students", { method: "POST", body: JSON.stringify(student) });
}

export function updateStudent(studentId, student) {
  return request(`/students/${encodeURIComponent(studentId)}`, {
    method: "PUT",
    body: JSON.stringify(student),
  });
}

export function getCareers() {
  return request("/careers");
}

export function getRecommendations(studentId) {
  return request(`/recommendations/${encodeURIComponent(studentId)}`);
}

export function getAssessmentQuestions() {
  return request("/assessment/questions");
}

export function submitAssessment(submission) {
  return request("/assessment/submit", {
    method: "POST",
    body: JSON.stringify(submission),
  });
}

export function getSkillGaps(studentId, careerId) {
  return request(`/skill-gaps/${encodeURIComponent(studentId)}?career_id=${encodeURIComponent(careerId)}`);
}

export function getRoadmap(studentId) {
  return request(`/roadmaps/${encodeURIComponent(studentId)}`);
}

export function generateRoadmap(studentId, careerId) {
  return request(`/roadmaps/${encodeURIComponent(studentId)}`, {
    method: "POST",
    body: JSON.stringify({ career_id: careerId }),
  });
}

export function updateRoadmapItem(studentId, roadmapId, itemId, completed) {
  return request(`/roadmaps/${encodeURIComponent(studentId)}/${encodeURIComponent(roadmapId)}/items/${encodeURIComponent(itemId)}`, {
    method: "PATCH",
    body: JSON.stringify({ completed }),
  });
}

export function getProjects() {
  return request("/projects");
}

export function getCertifications() {
  return request("/certifications");
}

export function getInternships() {
  return request("/internships");
}

export function getTrends() {
  return request("/trends");
}

export function getCareerDetail(careerId) {
  return request(`/careers/${encodeURIComponent(careerId)}`);
}

export function compareCareers(studentId, careerIds) {
  const params = new URLSearchParams({ student_id: String(studentId) });
  careerIds.forEach((careerId) => params.append("career_ids", careerId));
  return request(`/comparison?${params.toString()}`);
}

export function getSkills() {
  return request("/skills");
}

export function simulateCareer(studentId, hypotheticalSkills) {
  return request(`/simulator/${encodeURIComponent(studentId)}`, {
    method: "POST",
    body: JSON.stringify({ skills: hypotheticalSkills }),
  });
}

export function askAssistant(studentId, message) {
  return request("/assistant", {
    method: "POST",
    body: JSON.stringify({ student_id: Number(studentId), message }),
  });
}