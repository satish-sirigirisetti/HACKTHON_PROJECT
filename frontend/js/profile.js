const STUDENT_ID_KEY = "careerai.studentId";

export function readStudentId() {
  return window.localStorage.getItem(STUDENT_ID_KEY);
}

export function rememberStudentId(studentId) {
  window.localStorage.setItem(STUDENT_ID_KEY, String(studentId));
}

export function forgetStudentId() {
  window.localStorage.removeItem(STUDENT_ID_KEY);
}

export function splitProfileList(value) {
  return [...new Set(value.split(",").map((item) => item.trim()).filter(Boolean))];
}