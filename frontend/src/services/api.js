const configuredApiBase = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL;
const API_BASE_URL = (configuredApiBase || (import.meta.env.DEV ? "http://127.0.0.1:8000" : "")).replace(/\/+$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      credentials: "include",
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch {
    throw new Error("FastAPI is not reachable. Start the backend and try again.");
  }

  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = body.detail;
    const message = typeof detail === "string"
      ? detail
      : Array.isArray(detail)
        ? detail.map((item) => item.msg || "Check the submitted information.").join(" ")
        : `Request failed (${response.status}).`;
    if (response.status === 401) {
      window.dispatchEvent(new CustomEvent("ssdt:unauthorized", { detail: { path } }));
    }
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return body;
}

export const api = {
  register: (account) => request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(account),
  }),
  login: (credentials) => request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  }),
  logout: () => request("/api/auth/logout", { method: "POST" }),
  me: () => request("/api/auth/me"),
  health: () => request("/api/health"),
  databaseHealth: () => request("/api/health/database"),
  groqHealth: () => request("/api/health/groq"),
  skillAnalysis: () => request("/api/insights/analysis"),
  recommendations: () => request("/api/insights/recommendations"),
  generateRecommendations: () => request("/api/insights/recommendations/generate", { method: "POST" }),
  skills: () => request("/api/skills"),
  assessmentQuestions: (skillId) => request(`/api/assessments/questions?skill_id=${encodeURIComponent(skillId)}`),
  createStudent: (student) => request("/api/students", {
    method: "POST",
    body: JSON.stringify(student),
  }),
  student: (id) => request(`/api/students/${id}`),
  studentSkills: (id) => request(`/api/students/${id}/skills`),
  assessments: (id) => request(`/api/students/${id}/assessments`),
  createAssessment: (assessment) => request("/api/assessments", {
    method: "POST",
    body: JSON.stringify(assessment),
  }),
  progress: (id) => request(`/api/students/${id}/progress`),
};
