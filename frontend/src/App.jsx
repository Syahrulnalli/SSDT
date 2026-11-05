import React, { useEffect, useState } from "react";
import CATALOG from "../../skill_catalog.json";
import { api } from "./api.js";
import brandLogo from "./assets/logo/ssdt-logo.png";
import brandMark from "./assets/logo/ssdt-mark.png";
import pythonImage from "./assets/skills/python.png";
import machineLearningImage from "./assets/skills/machine-learning.png";
import artificialIntelligenceImage from "./assets/skills/artificial-intelligence.png";
import sqlDatabasesImage from "./assets/skills/sql-databases.png";
import webDevelopmentImage from "./assets/skills/web-development.png";
import problemSolvingImage from "./assets/skills/problem-solving-algorithms.png";
import assessmentImage from "./assets/features/skill-assessment.png";
import skillGapsImage from "./assets/features/skill-gaps.png";
import recommendationsImage from "./assets/features/recommendations.png";
import progressImage from "./assets/features/progress-tracking.png";
import achievementsImage from "./assets/features/achievements.png";
import dashboardImage from "./assets/features/dashboard.png";
import studentGrowthImage from "./assets/features/student-growth.png";
import studentGrowthHeroImage from "./assets/features/student-growth-hero.png";

const SKILL_IMAGES = {
  python: pythonImage,
  "machine-learning": machineLearningImage,
  "artificial-intelligence": artificialIntelligenceImage,
  "sql-databases": sqlDatabasesImage,
  "web-development": webDevelopmentImage,
  "problem-solving-algorithms": problemSolvingImage,
};

const SKILL_DESCRIPTIONS = {
  python: "Build programming fundamentals.",
  "machine-learning": "Find patterns in data.",
  "artificial-intelligence": "Explore intelligent systems.",
  "sql-databases": "Work with structured data.",
  "web-development": "Build for the web.",
  "problem-solving-algorithms": "Break problems into steps.",
};

const NAV = [
  ["home", "Home", "home"], ["skills", "Skills", "layers"],
  ["assessment", "Assessment", "clipboard"], ["dashboard", "Dashboard", "grid"],
  ["progress", "Progress", "chart"], ["recommendations", "Recommendations", "spark"],
];

const PAGE_PATHS = {
  home: "/",
  login: "/login",
  register: "/register",
  skills: "/skills",
  assessment: "/assessment",
  dashboard: "/dashboard",
  progress: "/progress",
  recommendations: "/recommendations",
  profile: "/profile",
};
const PRIVATE_PAGES = new Set(["skills", "assessment", "dashboard", "progress", "recommendations", "profile"]);

function pageFromPath() {
  const path = window.location.pathname.replace(/\/$/, "") || "/";
  return Object.entries(PAGE_PATHS).find(([, value]) => value === path)?.[0] || "home";
}

function Icon({ name, size = 18 }) {
  const shapes = {
    home: <><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9M9 20v-7h6v7"/></>,
    layers: <><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></>,
    clipboard: <><rect x="5" y="4.5" width="14" height="17" rx="2"/><path d="M9 4.5v-1h6v1M8.5 10h7M8.5 14h7M8.5 18h4"/></>,
    grid: <><rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/><rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/><rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/></>,
    chart: <><path d="M4 19V5M4 19h17"/><path d="m7 15 4-4 3 2 6-7"/></>,
    spark: <><path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3Z"/><path d="m19 16 .9 2.1L22 19l-2.1.9L19 22l-.9-2.1L16 19l2.1-.9L19 16Z"/></>,
    arrow: <><path d="M5 12h14M13 6l6 6-6 6"/></>,
    chevron: <path d="m9 18 6-6-6-6"/>,
    moon: <path d="M20.5 14.1A8.5 8.5 0 0 1 9.9 3.5 8.5 8.5 0 1 0 20.5 14.1Z"/>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/></>,
    check: <path d="m5 12 4 4L19 6"/>,
    book: <><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v16H6.5A2.5 2.5 0 0 0 4 21V5.5Z"/><path d="M4 17.5A2.5 2.5 0 0 1 6.5 15H20M8 7h8M8 10h6"/></>,
    menu: <><path d="M4 7h16M4 12h16M4 17h16"/></>,
    close: <><path d="m6 6 12 12M18 6 6 18"/></>,
    warning: <><path d="M10.3 3.9 2.8 17a2 2 0 0 0 1.7 3h15a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4m0 4h.01"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{shapes[name]}</svg>;
}

function App() {
  const [page, setPage] = useState(pageFromPath);
  const [theme, setTheme] = useState(() => localStorage.getItem("skilltrack.theme") || "light");
  const [mobileOpen, setMobileOpen] = useState(false);
  const [authState, setAuthState] = useState("loading");
  const [account, setAccount] = useState(null);
  const [returnPage, setReturnPage] = useState(null);
  const [authError, setAuthError] = useState("");
  const [apiState, setApiState] = useState("checking");
  const [groqStatus, setGroqStatus] = useState({ state: "idle", model: "openai/gpt-oss-20b" });
  const [skills, setSkills] = useState(CATALOG);
  const [skillsState, setSkillsState] = useState("loading");
  const [student, setStudent] = useState(null);
  const [studentId, setStudentId] = useState(null);
  const [studentLoading, setStudentLoading] = useState(false);
  const [studentSkills, setStudentSkills] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [progress, setProgress] = useState([]);
  const [dataError, setDataError] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [analysisState, setAnalysisState] = useState("idle");
  const [analysisError, setAnalysisError] = useState("");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("skilltrack.theme", theme);
  }, [theme]);

  useEffect(() => {
    let live = true;
    api.me().then((session) => {
      if (!live) return;
      setAccount(session.user);
      setStudent(session.student);
      setStudentId(session.student.id);
      setAuthState("authenticated");
    }).catch(() => {
      if (!live) return;
      setAccount(null);
      setStudent(null);
      setStudentId(null);
      setAuthState("anonymous");
    });
    return () => { live = false; };
  }, []);

  useEffect(() => {
    const syncRoute = () => {
      setPage(pageFromPath());
      setMobileOpen(false);
    };
    window.addEventListener("popstate", syncRoute);
    return () => window.removeEventListener("popstate", syncRoute);
  }, []);

  useEffect(() => {
    if (authState === "loading") return;
    if (PRIVATE_PAGES.has(page) && authState !== "authenticated") {
      setReturnPage(page);
      setPage("login");
      window.history.replaceState({}, "", PAGE_PATHS.login);
    } else if ((page === "login" || page === "register") && authState === "authenticated") {
      setPage("dashboard");
      window.history.replaceState({}, "", PAGE_PATHS.dashboard);
    }
  }, [authState, page]);

  useEffect(() => {
    function handleUnauthorized() {
      if (authState !== "authenticated") return;
      if (PRIVATE_PAGES.has(page)) setReturnPage(page);
      setAccount(null);
      setStudent(null);
      setStudentId(null);
      setStudentSkills([]);
      setAssessments([]);
      setProgress([]);
      setAnalysis(null);
      setAnalysisState("idle");
      setAuthState("anonymous");
      setAuthError("Your session expired. Please sign in again.");
      setRoute("login", true);
    }
    window.addEventListener("ssdt:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("ssdt:unauthorized", handleUnauthorized);
  }, [authState, page]);

  useEffect(() => {
    let live = true;
    api.health().then(async (health) => {
      if (!live) return;
      if (!health.database_configured) {
        setApiState("setup");
        return;
      }
      try {
        await api.databaseHealth();
        if (live) setApiState("connected");
      } catch {
        if (live) setApiState("database-down");
      }
    }).catch(() => live && setApiState("offline"));
    api.skills().then((data) => {
      if (!live) return;
      if (!Array.isArray(data)) throw new Error("The skills response was not a list.");
      setSkills(data);
      setSkillsState(data.length ? "ready" : "empty");
    }).catch(() => {
      if (!live) return;
      // Keep the canonical catalog available as a clearly marked offline reference.
      setSkills(CATALOG);
      setSkillsState("error");
    });
    return () => { live = false; };
  }, []);

  useEffect(() => {
    if (studentId) loadStudent(studentId);
  }, [studentId]);

  async function loadStudent(id) {
    setStudentLoading(true);
    setDataError("");
    setAnalysisState("loading");
    setAnalysisError("");
    const [recordsResult, analysisResult] = await Promise.allSettled([
      Promise.all([api.student(id), api.studentSkills(id), api.assessments(id), api.progress(id)]),
      api.skillAnalysis(),
    ]);
    if (recordsResult.status === "fulfilled") {
      const [profile, levels, history, timeline] = recordsResult.value;
      setStudent(profile);
      setStudentSkills(levels);
      setAssessments(history);
      setProgress(timeline);
    } else {
      const error = recordsResult.reason;
      setStudent(null);
      setStudentSkills([]);
      setAssessments([]);
      setProgress([]);
      setDataError(error.message);
    }
    if (analysisResult.status === "fulfilled") {
      setAnalysis(analysisResult.value);
      setAnalysisState("ready");
    } else {
      setAnalysis(null);
      setAnalysisState("error");
      setAnalysisError(analysisResult.reason.message);
    }
    setStudentLoading(false);
  }

  function setRoute(nextPage, replace = false) {
    setPage(nextPage);
    const method = replace ? "replaceState" : "pushState";
    window.history[method]({}, "", PAGE_PATHS[nextPage] || PAGE_PATHS.home);
    setMobileOpen(false);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function navigate(nextPage, context = null) {
    if (PRIVATE_PAGES.has(nextPage) && authState !== "authenticated") {
      setReturnPage(nextPage);
      setRoute("login");
      return;
    }
    setRoute(nextPage);
    if (nextPage === "assessment" && context) window.history.replaceState({}, "", `${PAGE_PATHS.assessment}?skill=${encodeURIComponent(context)}`);
  }

  function completeAuthentication(session) {
    setAccount(session.user);
    setStudent(session.student);
    setStudentId(session.student.id);
    setAuthState("authenticated");
    setAuthError("");
    const destination = returnPage && PRIVATE_PAGES.has(returnPage) ? returnPage : "dashboard";
    setReturnPage(null);
    setRoute(destination);
  }

  async function logout() {
    setAuthError("");
    try {
      await api.logout();
      setAccount(null);
      setStudent(null);
      setStudentId(null);
      setStudentSkills([]);
      setAssessments([]);
      setProgress([]);
      setAnalysis(null);
      setAnalysisState("idle");
      setAuthState("anonymous");
      setReturnPage(null);
      setRoute("home", true);
    } catch (error) {
      setAuthError(error.message);
    }
  }

  async function checkGroq() {
    setGroqStatus((current) => ({ ...current, state: "checking", error: "" }));
    try {
      const result = await api.groqHealth();
      setGroqStatus({ ...result, state: result.connected ? "connected" : result.configured ? "unavailable" : "unconfigured" });
    } catch {
      setGroqStatus({ state: "offline", model: "openai/gpt-oss-20b", error: "FastAPI could not complete the Groq check." });
    }
  }

  async function submitAssessment(payload) {
    if (!studentId) throw new Error("Create a student profile before submitting an assessment.");
    const result = await api.createAssessment(payload);
    await loadStudent(studentId);
    return result;
  }

  const activeLabel = NAV.find(([id]) => id === page)?.[1] || "Home";
  return <div className="app-shell">
    <a className="skip-link" href="#main-content">Skip to main content</a>
    <header className="topbar">
      <a className="brand" href="/" onClick={(event) => { event.preventDefault(); navigate("home"); }} aria-label="Student Skill Tracker home">
        <img className="brand-logo" src={brandLogo} alt="Student Skill Development Tracker" />
      </a>
      <button className="mobile-menu" type="button" aria-label={mobileOpen ? "Close navigation" : "Open navigation"} aria-expanded={mobileOpen} aria-controls="main-navigation" onClick={() => setMobileOpen(!mobileOpen)}><Icon name={mobileOpen ? "close" : "menu"} /></button>
      <nav id="main-navigation" className={`main-nav ${mobileOpen ? "is-open" : ""}`} aria-label="Main navigation">
        {NAV.filter(([id]) => authState === "authenticated" || id === "home").map(([id, label, icon]) => <button className={`nav-link ${page === id ? "is-active" : ""}`} key={id} type="button" aria-current={page === id ? "page" : undefined} onClick={() => navigate(id)}><Icon name={icon} size={16} /><span>{label}</span></button>)}
      </nav>
      <div className="header-actions">
        <span className={`api-status api-${apiState}`} title={apiStateLabel(apiState)}><i /> <span>{apiStateLabel(apiState)}</span></span>
        <button className="theme-toggle" type="button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`} title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}><Icon name={theme === "dark" ? "sun" : "moon"} size={17} /></button>
        {authState === "authenticated" ? <><button className="profile-button" type="button" onClick={() => navigate("profile")}><span className="avatar">{student?.name?.[0]?.toUpperCase() || "S"}</span><span>{student?.name || account?.username || "Student"}</span></button><button className="button button-quiet auth-logout" type="button" onClick={logout}>Log out</button></> : authState === "loading" ? <span className="auth-loading-label">Checking session…</span> : <><button className="button button-quiet auth-header-link" type="button" onClick={() => navigate("login")}>Sign in</button><button className="button button-primary auth-header-link" type="button" onClick={() => navigate("register")}>Create account</button></>}
      </div>
    </header>

    <main id="main-content" className="page-container">
      {authError && <Notice type="warning" message={authError} />}
      {authState === "loading" && PRIVATE_PAGES.has(page) ? <div className="auth-loading panel" role="status">Checking your sign-in…</div> : <>
        {page === "home" && <Home onNavigate={navigate} skills={skills} skillsState={skillsState} />}
        {(page === "login" || page === "register") && authState === "anonymous" && <AuthPage mode={page} onNavigate={navigate} onLogin={async (payload) => completeAuthentication(await api.login(payload))} onRegister={async (payload) => completeAuthentication(await api.register(payload))} />}
        {page === "skills" && authState === "authenticated" && <Skills skills={skills} skillsState={skillsState} studentSkills={studentSkills} analysis={analysis} onNavigate={navigate} />}
        {page === "assessment" && authState === "authenticated" && <Assessment onNavigate={navigate} skills={skills} studentId={studentId} studentSkills={studentSkills} assessments={assessments} onSubmit={submitAssessment} />}
      {page === "dashboard" && authState === "authenticated" && <Dashboard onNavigate={navigate} onRetry={() => loadStudent(studentId)} onGroqCheck={checkGroq} groqStatus={groqStatus} skills={skills} student={student} studentLoading={studentLoading} studentSkills={studentSkills} assessments={assessments} progress={progress} dataError={dataError} studentId={studentId} analysis={analysis} analysisState={analysisState} analysisError={analysisError} />}
        {page === "progress" && authState === "authenticated" && <Progress student={student} progress={progress} assessments={assessments} skills={skills} onNavigate={navigate} />}
        {page === "recommendations" && authState === "authenticated" && <Recommendations studentSkills={studentSkills} student={student} onNavigate={navigate} />}
        {page === "profile" && authState === "authenticated" && <Profile student={student} onNavigate={navigate} />}
      </>}
    </main>

    <footer className="site-footer"><span className="footer-brand"><img src={brandMark} alt="" /> SSDT</span><span>BCA Capstone <i /> Student growth, made visible</span><span className="footer-note"><i /> No generated scores</span></footer>
  </div>;
}

function apiStateLabel(state) {
  return ({ checking: "Checking API", connected: "API connected", setup: "Database setup needed", "database-down": "Database unavailable", offline: "API unavailable" })[state] || "API status";
}

function AuthPage({ mode, onNavigate, onLogin, onRegister }) {
  const registering = mode === "register";
  const [form, setForm] = useState({ username_or_email: "", username: "", email: "", name: "", program: "", batch: "", password: "", confirmPassword: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setError("");
    if (registering && form.password !== form.confirmPassword) {
      setError("The passwords do not match.");
      return;
    }
    setBusy(true);
    try {
      if (registering) {
        const { confirmPassword, username_or_email, ...accountData } = form;
        await onRegister(accountData);
      } else {
        await onLogin({ username_or_email: form.username_or_email, password: form.password });
      }
    } catch (submitError) {
      setError(submitError.message || "Authentication could not be completed.");
    } finally {
      setBusy(false);
    }
  }

  function update(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
    setError("");
  }

  return <section className="auth-page" aria-labelledby="auth-title">
    <div className="auth-aside">
      <img src={brandMark} alt="" />
      <Eyebrow>STUDENT SKILL DEVELOPMENT TRACKER</Eyebrow>
      <h1>{registering ? <>Start with a clear<br /><span>baseline.</span></> : <>Welcome back<br /><span>to your growth.</span></>}</h1>
      <p>{registering ? "Create your account to keep assessments and progress connected to your student profile." : "Sign in to review your skill dashboard, assessment results, and progress."}</p>
      <div className="auth-aside-note"><Icon name="check" size={15} /><span>Your student records stay connected to your account.</span></div>
    </div>
    <div className="auth-card panel">
      <div className="auth-card-heading"><Eyebrow>{registering ? "NEW ACCOUNT" : "ACCOUNT ACCESS"}</Eyebrow><h2 id="auth-title">{registering ? "Create your account" : "Sign in"}</h2><p>{registering ? "Your account creates a private student profile for your tracker." : "Use your username or email address to continue."}</p></div>
      <form className="auth-form" onSubmit={submit}>
        {registering ? <>
          <label className="auth-field">Username<input autoComplete="username" required minLength="3" maxLength="32" pattern="[A-Za-z0-9._-]+" value={form.username} onChange={(event) => update("username", event.target.value)} placeholder="Choose a username" /></label>
          <label className="auth-field">Email address<input type="email" autoComplete="email" required maxLength="255" value={form.email} onChange={(event) => update("email", event.target.value)} placeholder="you@example.com" /></label>
          <label className="auth-field auth-field-wide">Full name<input autoComplete="name" required maxLength="120" value={form.name} onChange={(event) => update("name", event.target.value)} placeholder="Your name" /></label>
          <div className="auth-form-grid"><label className="auth-field">Program<input required maxLength="100" value={form.program} onChange={(event) => update("program", event.target.value)} placeholder="e.g. BCA" /></label><label className="auth-field">Batch<input required maxLength="20" value={form.batch} onChange={(event) => update("batch", event.target.value)} placeholder="e.g. 2024" /></label></div>
          <label className="auth-field auth-field-wide">Password<input type="password" autoComplete="new-password" required minLength="12" maxLength="128" value={form.password} onChange={(event) => update("password", event.target.value)} placeholder="At least 12 characters" /><small>Use at least 12 characters.</small></label>
          <label className="auth-field auth-field-wide">Confirm password<input type="password" autoComplete="new-password" required minLength="12" maxLength="128" value={form.confirmPassword} onChange={(event) => update("confirmPassword", event.target.value)} placeholder="Enter the same password again" /></label>
        </> : <>
          <label className="auth-field auth-field-wide">Username or email<input autoComplete="username" required minLength="3" maxLength="255" value={form.username_or_email} onChange={(event) => update("username_or_email", event.target.value)} placeholder="Username or email address" /></label>
          <label className="auth-field auth-field-wide">Password<input type="password" autoComplete="current-password" required maxLength="128" value={form.password} onChange={(event) => update("password", event.target.value)} placeholder="Your password" /></label>
        </>}
        {error && <Notice type="warning" message={error} />}
        <button className="button button-primary auth-submit" type="submit" disabled={busy}>{busy ? (registering ? "Creating account…" : "Signing in…") : (registering ? "Create account" : "Sign in")}<Icon name="arrow" size={16} /></button>
      </form>
      <p className="auth-switch">{registering ? "Already have an account?" : "New to the tracker?"} <button type="button" className="text-button" onClick={() => onNavigate(registering ? "login" : "register")}>{registering ? "Sign in" : "Create an account"}</button></p>
    </div>
  </section>;
}

function Eyebrow({ children }) { return <p className="eyebrow"><span className="eyebrow-dot" />{children}</p>; }
function SectionTitle({ eyebrow, title, detail, action }) { return <div className="section-title-row"><div>{eyebrow && <p className="eyebrow">{eyebrow}</p>}<h2>{title}</h2>{detail && <p className="section-detail">{detail}</p>}</div>{action}</div>; }
function EmptyState({ icon = "chart", title, detail, action }) { return <div className="empty-state"><span className="empty-state-icon"><Icon name={icon} size={21} /></span><h3>{title}</h3><p>{detail}</p>{action}</div>; }
function SkillApiStatus({ state }) {
  if (state === "loading") return <div className="notice" role="status">Loading official skills…</div>;
  if (state === "error") return <Notice type="warning" message="Could not load skills from FastAPI. Showing the canonical catalog for reference." />;
  if (state === "empty") return <div className="notice" role="status">FastAPI returned no skill records.</div>;
  return null;
}

function Home({ onNavigate, skills, skillsState }) {
  return <>
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero-copy"><Eyebrow>STUDENT SKILL DEVELOPMENT TRACKER</Eyebrow><h1 id="hero-title">Build skills.<br /><span>Track progress.</span><br />Grow smarter.</h1><p>Six technical skills. One place to see your progress.</p><div className="hero-actions"><button className="button button-primary" onClick={() => onNavigate("assessment")}>Explore assessment <Icon name="arrow" size={17} /></button><button className="button button-secondary" onClick={() => onNavigate("dashboard")}>View dashboard</button></div><div className="hero-footnote"><span><Icon name="check" size={13} /></span> Six official skill areas</div></div>
      <div className="hero-visual" aria-label="Student growth illustration"><div className="visual-orbit orbit-outer" /><div className="visual-orbit orbit-inner" /><img className="hero-growth-image" src={studentGrowthHeroImage} alt="A student climbing toward a milestone flag along a rising path" /><span className="float-chip chip-top"><span><Icon name="layers" size={15} /></span>6 skill areas</span><span className="float-chip chip-bottom"><span><Icon name="chart" size={15} /></span>Progress tracking</span></div>
    </section>
    <section className="landing-section skills-showcase" aria-labelledby="landing-skills"><SkillApiStatus state={skillsState} /><SectionTitle eyebrow="THE SKILL FRAMEWORK" title="Six skills. One clear path." detail="A shared foundation for your development." action={<button className="text-button" onClick={() => onNavigate("skills")}>Explore all skills <Icon name="arrow" size={15} /></button>} /><div className="landing-skill-grid">{skills.map((skill,index)=><button className="landing-skill" key={skill.id} onClick={()=>onNavigate("skills")}><img className={`skill-symbol-image tone-${index+1}`} src={SKILL_IMAGES[skill.id]} alt="" /><span><strong>{skill.name}</strong><small>{SKILL_DESCRIPTIONS[skill.id]}</small></span><Icon name="chevron" size={15} /></button>)}</div></section>
    <section className="landing-section how-section" aria-labelledby="how-title"><div className="section-intro"><Eyebrow>THE LEARNING LOOP</Eyebrow><h2 id="how-title">Know what comes<br /><span>next.</span></h2><p>Four parts of a steady learning journey.</p></div><div className="journey-grid"><Feature number="01" title="Skill assessment" detail="Set a real baseline." image={assessmentImage} alt="Student reviewing a skill assessment" state="Ready to take" /><Feature number="02" title="Skill gaps" detail="See where to focus." image={skillGapsImage} alt="Skill gap chart" state="Needs assessment" /><Feature number="03" title="Recommendations" detail="Choose a useful next step." image={recommendationsImage} alt="A route from current skills toward development goals" state="Method to be defined" /><Feature number="04" title="Progress tracking" detail="Review recorded results." image={progressImage} alt="Progress timeline with completed checkpoints" state="After first assessment" /></div></section>
    <section className="landing-cta"><div><Eyebrow>START HERE</Eyebrow><h2>Begin with a clear picture.</h2><p>Check your current skills with a server-scored baseline.</p></div><button className="button button-light" onClick={()=>onNavigate("assessment")}>Explore assessment <Icon name="arrow" size={16} /></button></section>
  </>;
}

function Feature({ number, title, detail, image, alt, state }) { return <article className="feature-card"><div className="feature-top"><img src={image} alt={alt} /><span>{number}</span></div><h3>{title}</h3><p>{detail}</p><small><i />{state}</small></article>; }

function Dashboard({ onNavigate, onRetry, onGroqCheck, groqStatus, skills, student, studentLoading, studentSkills, assessments, progress, dataError, studentId, analysis, analysisState, analysisError }) {
  const latestAssessment = assessments[0];
  const assessedSkills = analysis?.skills?.filter((item) => item.attempts > 0) || [];
  const nextSkill = analysis?.skills?.filter((item) => item.classification === "needs_attention").sort((a,b) => a.latest_score-b.latest_score)[0] || analysis?.skills?.filter((item) => item.classification === "developing").sort((a,b) => a.latest_score-b.latest_score)[0];
  const activity = [...(progress || [])].sort((a, b) => new Date(b.assessed_at) - new Date(a.assessed_at));
  return <section className="app-page dashboard-page" aria-labelledby="dashboard-title">
    <div className="page-heading dashboard-page-heading"><div><Eyebrow>STUDENT WORKSPACE</Eyebrow><h1 id="dashboard-title">{student ? `Welcome, ${student.name.split(" ")[0]}.` : "Your learning, in one place."}</h1><p>{student ? "A clear view of your saved assessments and what to focus on next." : "Create a student profile to connect your assessment history."}</p></div><button className="button button-primary" onClick={() => onNavigate(student ? "assessment" : "profile")}>{student ? "Start an assessment" : "Create profile"}<Icon name="arrow" size={16} /></button></div>
    {studentLoading && <div className="notice" role="status">Loading your saved progress…</div>}
    {dataError && <div className="dashboard-error"><Notice type="warning" message={dataError} /><button className="button button-secondary" type="button" onClick={onRetry}>Try loading again</button></div>}
    {!studentLoading && !dataError && <>
      {!student && <div className="profile-callout"><div><span className="callout-icon"><Icon name="book" size={20} /></span><strong>No student profile yet</strong><p>Your profile connects your account to saved assessment records.</p></div><button className="button button-secondary" onClick={() => onNavigate("profile")}>Set up profile<Icon name="arrow" size={15} /></button></div>}
      <div className="dashboard-metrics">
        <Metric label="Skills assessed" value={analysis ? `${analysis.attempted_skills} / 6` : "—"} detail={analysis ? "Skills with a saved quiz" : analysisState === "error" ? "Analysis unavailable" : "Loading saved results"} icon="layers" tone="blue" />
        <Metric label="Assessments completed" value={String(assessments.length)} detail="Saved quiz attempts" icon="clipboard" tone="green" />
        <Metric label="Latest activity" value={latestAssessment ? new Date(latestAssessment.assessed_at).toLocaleDateString() : "None yet"} detail={latestAssessment ? "Most recent saved quiz" : "Take a quiz to begin"} icon="chart" tone="violet" />
        <Metric label={nextSkill ? "Good focus for next" : "Strongest assessed skill"} value={nextSkill?.skill_name || assessedSkills.filter((item) => item.classification === "strength").sort((a, b) => b.latest_score - a.latest_score)[0]?.skill_name || "Not assessed"} detail={nextSkill ? `${Math.round(nextSkill.latest_score)}% latest score` : "Based on saved results"} icon="spark" tone="blue" />
      </div>
      <GroqConnectionCard status={groqStatus} onCheck={onGroqCheck} />
      <div className="dashboard-main-grid">
        <section className="panel dashboard-section dashboard-skills" aria-labelledby="dashboard-skills-title">
          <SectionTitle eyebrow="YOUR SIX SKILLS" title="Latest scores" detail="Each bar uses the same 0–100% scale. Missing results stay unassessed." action={<button className="text-button" onClick={() => onNavigate("skills")}>All skills<Icon name="arrow" size={14} /></button>} />
          {analysisState === "error" ? <InlineRetry message={analysisError} onRetry={onRetry} /> : analysisState === "loading" || analysisState === "idle" ? <p className="quiet-empty" role="status">Loading your skill results…</p> : <SkillScoreBars skills={analysis.skills} />}
        </section>
        <aside className="dashboard-aside">
          <ProfileCard student={student} onClick={() => onNavigate("profile")} />
          <section className="panel dashboard-section dashboard-next-step"><Eyebrow>YOUR NEXT STEP</Eyebrow><h2>{nextSkill ? `Spend a little time on ${nextSkill.skill_name}.` : assessedSkills.length ? "Keep building on your results." : "Start with one short quiz."}</h2><p>{nextSkill ? `Your latest score is ${Math.round(nextSkill.latest_score)}%. A focused practice session gives you a useful next checkpoint.` : "An individual skill quiz creates a baseline for your personal progress."}</p><button className="button button-secondary" onClick={() => onNavigate(nextSkill ? "recommendations" : "assessment")}>{nextSkill ? "View next steps" : "Choose a quiz"}<Icon name="arrow" size={15} /></button></section>
        </aside>
      </div>
      <div className="dashboard-lower-grid">
        <section className="panel dashboard-section"><SectionTitle eyebrow="SAVED RESULTS" title="Progress over time" detail={progress.length > 1 ? "A trend appears only when a skill has multiple attempts." : "Complete another quiz in the same skill to compare results."} /><ScoreTrendChart points={progress} /></section>
        <section className="panel dashboard-section"><SectionTitle eyebrow="RECENT ACTIVITY" title="Your latest quizzes" action={<button className="text-button" onClick={() => onNavigate("progress")}>Full history<Icon name="arrow" size={14} /></button>} />{activity.length ? <RecentActivity points={activity.slice(0, 5)} /> : <EmptyState icon="clipboard" title="Nothing recorded yet" detail="Your quiz results will appear here after you complete an assessment." action={<button className="text-button" onClick={() => onNavigate("assessment")}>Choose your first quiz<Icon name="arrow" size={14} /></button>} />}</section>
      </div>
      <SkillAnalysisPanel analysis={analysis} state={analysisState} error={analysisError} onRetry={onRetry} onNavigate={onNavigate} progress={progress} />
    </>}
  </section>;
}

function InlineRetry({ message, onRetry }) { return <div className="inline-retry"><p>{message || "Skill results could not be loaded."}</p><button className="text-button" type="button" onClick={onRetry}>Retry<Icon name="arrow" size={14} /></button></div>; }

function GroqConnectionCard({ status, onCheck }) {
  const labels = {
    idle: "Not checked",
    checking: "Checking connection",
    connected: "Connected",
    unconfigured: "Key not configured",
    unavailable: "Connection unavailable",
    offline: "FastAPI unavailable",
  };
  const detail = status.state === "idle"
    ? "Run a small request through FastAPI to check the configured Groq model."
    : status.state === "checking"
      ? "Waiting for the backend model check..."
      : status.state === "connected"
        ? `FastAPI reached ${status.model}. No student data was sent.`
        : status.state === "unconfigured"
          ? "Add GROQ_API_KEY to the project .env file, then check again."
          : status.error || "The Groq model could not be reached.";
  return <section className={`panel groq-connection-card groq-${status.state}`} aria-live="polite">
    <div className="groq-connection-copy"><span className="eyebrow"><i /> GROQ MODEL CONNECTION</span><h2>{labels[status.state] || "Groq status"}</h2><p>{detail}</p></div>
    <button className="button button-secondary" type="button" onClick={onCheck} disabled={status.state === "checking"}>{status.state === "checking" ? "Checking..." : "Test Groq connection"}</button>
  </section>;
}

function Metric({ label,value,detail,icon,tone }) { return <article className="metric-card"><span className={`metric-icon metric-${tone}`}><Icon name={icon} size={18}/></span><div><p>{label}</p><strong>{value}</strong><small>{detail}</small></div></article>; }
function ProfileCard({student,onClick}) { return <section className="panel profile-card"><div className="profile-card-head"><span className="eyebrow">STUDENT PROFILE</span><button className="icon-button" aria-label="Set up or view profile" onClick={onClick}><Icon name="arrow" size={15}/></button></div><div className="profile-main"><span className="large-avatar">{student?.name?.[0]?.toUpperCase()||"?"}</span><div><strong>{student?.name||"Profile not set up"}</strong><small>{student?`${student.program} · Batch ${student.batch}`:"Add a profile to get started"}</small></div></div>{student&&<div className="profile-email">{student.email}</div>}</section>; }
function PanelEmpty({title,label,detail,image,alt,onClick}) { return <section className="panel empty-panel"><span className="eyebrow">{label}</span><h2>{title}</h2><p>{detail}</p>{image&&<img className="panel-feature-image" src={image} alt={alt} />}<button className="text-button" onClick={onClick}>View project status <Icon name="arrow" size={14}/></button></section>; }
function Notice({type="info",message}) { return <div className={`notice notice-${type}`} role="status"><Icon name={type==="warning"?"warning":"check"} size={16}/><span>{message}</span></div>; }

function SkillAnalysisPanel({analysis,state,error,onRetry,onNavigate,progress}) {
  if (state === "loading" || state === "idle") return <section className="panel analysis-panel" aria-labelledby="analysis-title"><span className="eyebrow">SKILL ANALYSIS</span><h2 id="analysis-title">Finding patterns in your results…</h2><p role="status">Loading saved assessment analysis.</p></section>;
  if (state === "error") return <section className="panel analysis-panel analysis-error" aria-labelledby="analysis-title"><div><span className="eyebrow">SKILL ANALYSIS</span><h2 id="analysis-title">Analysis is unavailable</h2><p>{error}</p></div><button className="button button-secondary" onClick={onRetry}>Try again</button></section>;
  const assessed = analysis.skills.filter((item) => item.attempts > 0);
  const strongest = assessed.filter((item) => item.classification === "strength").sort((a, b) => b.latest_score - a.latest_score)[0] || [...assessed].sort((a, b) => b.latest_score - a.latest_score)[0];
  const focus = assessed.filter((item) => item.classification === "needs_attention").sort((a, b) => a.latest_score - b.latest_score)[0] || assessed.filter((item) => item.classification === "developing").sort((a, b) => a.latest_score - b.latest_score)[0];
  const unassessed = analysis.skills.length - assessed.length;
  return <section className="panel analysis-panel" aria-labelledby="analysis-title">
    <div className="analysis-heading"><div><Eyebrow>UNDERSTAND YOUR BASELINE</Eyebrow><h2 id="analysis-title">Skill analysis</h2><p>Compare saved quiz results and see where another attempt can show change.</p></div><button className="text-button" onClick={() => onNavigate("recommendations")}>See suggested next steps<Icon name="arrow" size={14} /></button></div>
    <div className="analysis-summary-grid">
      <AnalysisSummary label="Skills assessed" value={`${analysis.attempted_skills} of 6`} detail={unassessed ? `${unassessed} not assessed yet` : "Every skill has a result"} />
      <AnalysisSummary label="Strongest result" value={strongest?.skill_name || "Not assessed"} detail={strongest ? `${Math.round(strongest.latest_score)}% latest score` : "Take a quiz to begin"} />
      <AnalysisSummary label="Focus next" value={focus?.skill_name || (assessed.length ? "Keep practising" : "Not assessed")} detail={focus ? `${Math.round(focus.latest_score)}% latest score` : assessed.length ? "No skill is below the attention threshold" : "Take a quiz to begin"} />
    </div>
    <div className="analysis-content-grid">
      <section className="analysis-chart-section" aria-labelledby="analysis-chart-title"><div className="section-subheading"><h3 id="analysis-chart-title">Latest score by skill</h3><span>Scale: 0–100%</span></div><SkillScoreBars skills={analysis.skills} /></section>
      <section className="analysis-detail-section" aria-labelledby="analysis-detail-title"><div className="section-subheading"><h3 id="analysis-detail-title">What your scores show</h3><span>Uses the current analysis thresholds</span></div><div className="analysis-status-list">{analysis.skills.map((item) => <AnalysisSkillRow item={item} key={item.skill_id} />)}</div></section>
    </div>
    <div className="analysis-trend"><div className="section-subheading"><div><h3>Score trends</h3><p>Changes compare attempts for the same skill.</p></div></div><ScoreTrendChart points={progress} /></div>
    <div className="analysis-next-step"><div><span className="eyebrow">A USEFUL NEXT STEP</span><strong>{focus ? `Try another ${focus.skill_name} quiz after a short practice session.` : assessed.length ? "Choose one skill to practise, then check in with another quiz." : "Take one skill quiz to create your first baseline."}</strong></div><button className="button button-secondary" onClick={() => onNavigate(focus ? "recommendations" : "assessment")}>{focus ? "Open recommendations" : "Choose a quiz"}<Icon name="arrow" size={14} /></button></div>
  </section>;
}

function AnalysisSummary({label,value,detail}) { return <div className="analysis-summary"><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>; }

function AnalysisSkillRow({item}) {
  const status = { not_assessed: "Not assessed", needs_attention: "Focus", developing: "Developing", strength: "Strong" }[item.classification];
  const evidence = item.latest_score == null ? "Take this skill quiz to add a score." : item.score_change == null ? `Latest result · ${item.attempts} attempt${item.attempts === 1 ? "" : "s"}. Complete another quiz to track change.` : `${item.score_change > 0 ? "+" : ""}${item.score_change} points since the previous attempt.`;
  return <div className="analysis-status-row"><span className={`status-marker status-${item.classification}`} aria-hidden="true" /><div><strong>{item.skill_name}</strong><small>{evidence}</small></div><span className={`status-word status-${item.classification}`}>{item.latest_score == null ? "Not assessed" : `${Math.round(item.latest_score)}% · ${status}`}</span></div>;
}

function SkillScoreBars({skills}) {
  return <div className="skill-score-bars" role="list" aria-label="Latest quiz scores for the six official skills">
    {skills.map((item) => <div className={`skill-score-row ${item.latest_score == null ? "is-unassessed" : ""}`} role="listitem" key={item.skill_id}>
      <span className="skill-score-name">{item.skill_name}</span>
      <div className="skill-score-track" role="img" aria-label={item.latest_score == null ? `${item.skill_name}: not assessed` : `${item.skill_name}: ${Math.round(item.latest_score)} percent`}><span style={{ width: item.latest_score == null ? "0%" : `${Math.max(0, Math.min(100, item.latest_score))}%` }} /></div>
      <strong>{item.latest_score == null ? "Not assessed" : `${Math.round(item.latest_score)}%`}</strong>
    </div>)}
  </div>;
}

const CHART_COLORS = ["#1e40af", "#008b45", "#5273c8", "#c27b24", "#59667a", "#167d87"];

function ScoreTrendChart({points}) {
  const groups = Object.values((points || []).reduce((map, point) => { (map[point.skill_id] ||= { name: point.skill_name, points: [] }).points.push(point); return map; }, {})).map((group) => ({ ...group, points: group.points.sort((a, b) => new Date(a.assessed_at) - new Date(b.assessed_at)) }));
  const trendGroups = groups.filter((group) => group.points.length >= 2);
  if (!trendGroups.length) return <div className="chart-empty"><span>{points?.length ? "One saved result is available for each skill shown. Take another quiz in the same skill to see a trend." : "No saved score history yet."}</span></div>;
  const dates = trendGroups.flatMap((group) => group.points.map((point) => new Date(point.assessed_at).getTime()));
  const minDate = Math.min(...dates); const maxDate = Math.max(...dates); const dateSpan = maxDate - minDate || 1;
  const x = (date) => 54 + ((new Date(date).getTime() - minDate) / dateSpan) * 660;
  const y = (score) => 18 + (100 - Number(score)) * 2.18;
  return <div className="trend-chart-wrap"><svg className="trend-chart" viewBox="0 0 740 248" role="img" aria-labelledby="trend-chart-title trend-chart-desc" preserveAspectRatio="none"><title id="trend-chart-title">Saved assessment scores over time</title><desc id="trend-chart-desc">Line chart using recorded results only. Each line represents one skill and spans only that skill's saved attempts.</desc>
    {[0, 50, 100].map((tick) => <g key={tick}><line x1="54" x2="714" y1={y(tick)} y2={y(tick)} className="chart-gridline"/><text x="43" y={y(tick) + 4} textAnchor="end" className="chart-axis-label">{tick}%</text></g>)}
    {trendGroups.map((group) => { const color = CHART_COLORS[groups.indexOf(group) % CHART_COLORS.length]; return <g key={group.name}><polyline fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" points={group.points.map((point) => `${x(point.assessed_at)},${y(point.score)}`).join(" ")} />{group.points.map((point, index) => <circle key={`${point.assessment_id}-${index}`} cx={x(point.assessed_at)} cy={y(point.score)} r="4" fill={color}><title>{`${group.name}: ${Math.round(point.score)}% on ${new Date(point.assessed_at).toLocaleDateString()}`}</title></circle>)}</g>; })}
    <text x="54" y="238" className="chart-axis-label">{new Date(minDate).toLocaleDateString()}</text><text x="714" y="238" textAnchor="end" className="chart-axis-label">{new Date(maxDate).toLocaleDateString()}</text>
  </svg><div className="chart-legend">{trendGroups.map((group) => <span key={group.name}><i style={{ background: CHART_COLORS[groups.indexOf(group) % CHART_COLORS.length] }} />{group.name}</span>)}</div></div>;
}

function RecentActivity({points}) {
  const latestByAssessment = new Map();
  points.forEach((point) => { const existing = latestByAssessment.get(point.assessment_id); if (!existing || new Date(point.assessed_at) > new Date(existing.assessed_at)) latestByAssessment.set(point.assessment_id, point); });
  return <ol className="recent-activity-list">{[...latestByAssessment.values()].slice(0, 5).map((point) => <li key={point.assessment_id}><span className="activity-icon"><Icon name="clipboard" size={16} /></span><span><strong>{point.skill_name}</strong><small>{new Date(point.assessed_at).toLocaleString()}</small></span><b>{Math.round(point.score)}%</b></li>)}</ol>;
}

function Skills({skills,skillsState,studentSkills,analysis,onNavigate}) {
  const levels=Object.fromEntries(studentSkills.map((item)=>[item.skill_id,item]));
  const analysisById=Object.fromEntries((analysis?.skills||[]).map((item)=>[item.skill_id,item]));
  return <section className="app-page" aria-labelledby="skills-title"><div className="page-heading"><Eyebrow>OFFICIAL FRAMEWORK</Eyebrow><h1 id="skills-title">Six skills. <span>One foundation.</span></h1><p>See your latest result, explore each area, and choose where to practise next.</p></div><SkillApiStatus state={skillsState}/>{skills.length?<div className="skills-page-grid">{skills.map((skill,index)=>{const score=levels[skill.id]?.latest_score;const classification=analysisById[skill.id]?.classification;const status={not_assessed:"Not assessed yet",needs_attention:"Getting started",developing:"Developing",strength:"Strong"}[classification]||(score==null?"Not assessed yet":"Assessed");const tone={not_assessed:"status-none",needs_attention:"status-focus",developing:"status-mid",strength:"status-good"}[classification]||"status-none";return <article className="panel framework-card skill-card" key={skill.id}><div className="framework-card-top"><img className={`skill-card-image tone-${index+1}`} src={SKILL_IMAGES[skill.id]} alt="" /><span className="area-index">AREA 0{index+1}</span></div><h2>{skill.name}</h2><p className="skill-card-description">{SKILL_DESCRIPTIONS[skill.id]}</p><div className="skill-card-score"><span>Latest score</span><strong>{score==null?"Not assessed yet":`${Math.round(score)}%`}</strong></div><div className="skill-card-progress" role="img" aria-label={score==null?`${skill.name}: not assessed`: `${skill.name}: ${Math.round(score)} percent`}><span style={{width:score==null?"0%":`${Math.max(0,Math.min(100,score))}%`}}/></div><div className="skill-card-footer"><span className="skill-status"><i aria-hidden="true" className={tone}/>{status}</span><button className="text-button" onClick={()=>onNavigate("assessment",skill.id)}>{score==null?"Assess skill":"Practice now"}<Icon name="arrow" size={14}/></button></div><div className="skill-topic-list" aria-label={`${skill.name} focus topics`}>{skill.focus.slice(0,3).map((item)=><span key={item}>{item}</span>)}</div></article>;})}</div>:skillsState!=="loading"&&<EmptyState icon="layers" title="No skills available" detail="FastAPI returned no official skill records."/>}</section>;
}

function Assessment({onNavigate,skills,studentId,studentSkills,assessments,onSubmit}) {
  const [status,setStatus]=useState("intro");
  const [questions,setQuestions]=useState([]);
  const [answers,setAnswers]=useState({});
  const [currentIndex,setCurrentIndex]=useState(0);
  const [result,setResult]=useState(null);
  const [error,setError]=useState("");
  const [selectedSkill,setSelectedSkill]=useState(null);
  const currentQuestion=questions[currentIndex];
  const answeredCount=Object.keys(answers).length;

  async function beginAssessment(skillId) {
    setSelectedSkill(skillId);
    setError("");
    setStatus("loading");
    try {
      const loaded=await api.assessmentQuestions(skillId);
      if (!Array.isArray(loaded)||loaded.length===0) {
        setQuestions([]);
        setStatus("empty");
        return;
      }
      setQuestions(loaded);
      setAnswers({});
      setCurrentIndex(0);
      setStatus("taking");
    } catch (requestError) {
      setError(requestError.message);
      setStatus("load-error");
    }
  }

  async function submitAnswers() {
    if (answeredCount!==questions.length) {
      setError("Answer every question before submitting.");
      return;
    }
    setError("");
    setStatus("submitting");
    try {
      const saved=await onSubmit({ skill_id:selectedSkill, answers:questions.map((question)=>({
        question_id:question.id,
        selected_option_id:answers[question.id],
      })) });
      setResult(saved);
      setStatus("result");
    } catch (requestError) {
      setError(requestError.message);
      setStatus("taking");
    }
  }

  function resetAssessment() {
    setError("");
    setResult(null);
    setQuestions([]);
    setAnswers({});
    setCurrentIndex(0);
    setSelectedSkill(null);
    setStatus("intro");
    window.history.replaceState({}, "", PAGE_PATHS.assessment);
  }

  useEffect(() => {
    const requestedSkill = new URLSearchParams(window.location.search).get("skill");
    if (requestedSkill && skills.some((skill) => skill.id === requestedSkill)) {
      window.history.replaceState({}, "", PAGE_PATHS.assessment);
      beginAssessment(requestedSkill);
    }
  }, []);

  return <section className="app-page" aria-labelledby="assessment-title">
    <div className="page-heading"><Eyebrow>ASSESSMENT</Eyebrow><h1 id="assessment-title">Know where <span>you stand.</span></h1><p>Select one of the six independent skill quizzes.</p></div>
    {status==="intro"&&<>
      <div className="assessment-banner"><div><span className="status-pill"><i/>READY WHEN YOU ARE</span><h2>One skill at a time.</h2><p>Each quiz has five questions and is scored independently. Your results are saved to your account.</p></div><img className="assessment-banner-image" src={assessmentImage} alt="Student reviewing a skill assessment dashboard" /></div>
      <div className="assessment-card-grid">{skills.map((skill,index)=>{const level=studentSkills.find((item)=>item.skill_id===skill.id);const attempts=assessments.filter((assessment)=>assessment.results?.some((resultItem)=>resultItem.skill_id===skill.id)).length;return <article className="panel assessment-skill-card" key={skill.id}><div className="assessment-skill-card-head"><img className={`skill-card-image tone-${index+1}`} src={SKILL_IMAGES[skill.id]} alt=""/><span className="area-index">QUIZ 0{index+1}</span></div><h2>{skill.name}</h2><p>5 questions · individual skill quiz</p><div className="assessment-last-result"><span>{attempts?`${attempts} attempt${attempts===1?"":"s"}`:"No quiz attempts"}</span><strong>{level?.latest_score==null?"Not assessed":`${Math.round(level.latest_score)}% latest`}</strong></div><div className="assessment-card-actions"><button className="button button-primary" type="button" disabled={!studentId} onClick={()=>beginAssessment(skill.id)}>{studentId?"Start quiz":"Profile needed"}<Icon name="arrow" size={15}/></button><button className="text-button" type="button" onClick={()=>onNavigate("progress")}>View history</button></div></article>;})}</div>
      {!studentId&&<Notice type="warning" message="Sign in with an account linked to a student profile before taking a quiz."/>}
    </>}
    {status==="loading"&&<div className="assessment-state panel" role="status"><span className="eyebrow">LOADING</span><h2>Preparing your questions</h2><p>Getting the official assessment from FastAPI…</p></div>}
    {status==="load-error"&&<div className="assessment-state panel"><Notice type="warning" message={error}/><h2>Questions could not be loaded</h2><button className="button button-secondary" type="button" onClick={()=>beginAssessment(selectedSkill)}>Try again</button></div>}
    {status==="empty"&&<EmptyState icon="clipboard" title="No assessment questions available" detail="FastAPI returned an empty question set. Try again later." action={<button className="button button-secondary" type="button" onClick={()=>beginAssessment(selectedSkill)}>Try again</button>}/>}
    {(status==="taking"||status==="submitting")&&currentQuestion&&<div className="assessment-workspace">
      <div className="assessment-progress-head"><div><span className="eyebrow">QUESTION {currentIndex+1} OF {questions.length}</span><strong>{currentQuestion.skill_name}</strong></div><span>{answeredCount} answered</span></div>
      <div className="assessment-progress-track" role="progressbar" aria-label="Assessment progress" aria-valuemin="0" aria-valuemax={questions.length} aria-valuenow={currentIndex+1}><i style={{width:`${((currentIndex+1)/questions.length)*100}%`}}/></div>
      <article className="panel assessment-question-card"><div className="assessment-question-meta"><span className="eyebrow">{currentQuestion.skill_name}</span><span className={`difficulty-tag difficulty-${currentQuestion.difficulty}`}>{currentQuestion.difficulty}</span></div><h2>{currentQuestion.text}</h2><fieldset className="assessment-options" disabled={status==="submitting"}><legend className="visually-hidden">Select one answer</legend>{currentQuestion.options.map((option,index)=><label className={`assessment-option ${answers[currentQuestion.id]===option.id?"is-selected":""}`} key={option.id}><input type="radio" name={currentQuestion.id} value={option.id} checked={answers[currentQuestion.id]===option.id} onChange={()=>setAnswers((current)=>({...current,[currentQuestion.id]:option.id}))}/><span className="option-letter">{String.fromCharCode(65+index)}</span><span>{option.text}</span></label>)}</fieldset>{!answers[currentQuestion.id]&&<p className="assessment-incomplete-hint">Choose an answer to {currentIndex===questions.length-1?"submit":"continue"}.</p>}{error&&<Notice type="warning" message={error}/>}<div className="assessment-question-footer"><button className="button button-secondary" type="button" disabled={currentIndex===0||status==="submitting"} onClick={()=>{setError("");setCurrentIndex((index)=>index-1)}}>Previous</button><span>{currentIndex+1} / {questions.length}</span>{currentIndex<questions.length-1?<button className="button button-primary" type="button" disabled={!answers[currentQuestion.id]||status==="submitting"} onClick={()=>{setError("");setCurrentIndex((index)=>index+1)}}>Continue <Icon name="arrow" size={15}/></button>:<button className="button button-primary" type="button" disabled={!answers[currentQuestion.id]||status==="submitting"} onClick={submitAnswers}>{status==="submitting"?"Saving results…":"Submit assessment"}<Icon name="arrow" size={15}/></button>}</div></article>
    </div>}
    {status==="result"&&result&&<div className="assessment-results"><div className="assessment-result-summary panel"><span className="eyebrow">ASSESSMENT SAVED</span><strong>{Number(result.overall_score).toFixed(0)}<small>%</small></strong><p>Overall score · {new Date(result.assessed_at).toLocaleString()}</p><button className="button button-primary" type="button" onClick={()=>onNavigate("dashboard")}>View dashboard <Icon name="arrow" size={15}/></button></div><div className="assessment-result-list"><div className="assessment-results-heading"><div><span className="eyebrow">YOUR RESULTS</span><h2>Scores by skill</h2></div><span>Saved assessment #{result.id}</span></div><div className="assessment-result-grid">{result.results.map((item)=><article className="panel assessment-result-card" key={item.skill_id}><span>{item.skill_name}</span><strong>{Number(item.score).toFixed(0)}%</strong><div className="assessment-score-track"><i style={{width:`${Math.max(0,Math.min(100,Number(item.score)))}%`}}/></div></article>)}</div><div className="assessment-result-actions"><button className="button button-secondary" type="button" onClick={resetAssessment}>Take another assessment</button><button className="text-button" type="button" onClick={()=>onNavigate("dashboard")}>Open dashboard <Icon name="arrow" size={14}/></button></div></div></div>}
  </section>;
}

function Recommendations({studentSkills,student,onNavigate}) {
  const [result,setResult]=useState(null);
  const [state,setState]=useState("loading");
  const [error,setError]=useState("");
  const [generating,setGenerating]=useState(false);
  async function loadRules() {
    setState("loading"); setError("");
    try { setResult(await api.recommendations()); setState("ready"); }
    catch(requestError) { setError(requestError.message); setState("error"); }
  }
  useEffect(()=>{ loadRules(); },[]);
  async function generate() {
    setGenerating(true); setError("");
    try { setResult(await api.generateRecommendations()); }
    catch(requestError) { setError(requestError.message); }
    finally { setGenerating(false); }
  }
  const recommendations=[...(result?.recommendations||[])].sort((a,b)=>({high:0,medium:1,low:2}[a.priority]-({high:0,medium:1,low:2}[b.priority])));
  const attempted=recommendations.length;
  return <section className="app-page" aria-labelledby="recommendations-title">
    <div className="page-heading"><Eyebrow>PERSONALIZED NEXT STEPS</Eyebrow><h1 id="recommendations-title">A good next step, <span>based on your results.</span></h1><p>Each suggestion is connected to a saved quiz result. Scores and priorities come from the assessment record.</p></div>
    {state==="loading"&&<div className="panel recommendation-state" role="status">Loading your saved assessment evidence…</div>}
    {state==="error"&&<div className="panel recommendation-state"><Notice type="warning" message={error}/><button className="button button-secondary" onClick={loadRules}>Retry loading</button></div>}
    {state==="ready"&&<>
      {!attempted?<div className="recommendation-empty panel"><img className="recommendation-image" src={recommendationsImage} alt="A route from current skills toward development goals"/><div><span className="eyebrow">NO ASSESSMENT EVIDENCE</span><h2>Start with one skill quiz</h2><p>{student?"Complete any one of the six quizzes to get recommendations grounded in your result.":"Connect a student profile and complete a skill quiz first."}</p></div></div>:<>
        <div className="recommendation-toolbar"><div><span className="eyebrow">{result.source==="groq"?"PERSONALIZED WORDING":"PRACTICAL GUIDANCE"}</span><p>{result.message||(result.source==="groq"?"Suggested wording is based on your saved results; the scores and priorities remain fixed.":"These steps use your saved quiz scores and the existing skill thresholds.")}</p><small>{attempted} skill{attempted===1?"":"s"} with saved results · Updated {new Date(result.generated_at).toLocaleString()}</small></div><button className="button button-secondary" type="button" onClick={generate} disabled={generating}>{generating?"Preparing…":"Refresh AI wording"}<Icon name="spark" size={15}/></button></div>
        {error&&<Notice type="warning" message={error}/>}
        <div className="recommendation-grid">{recommendations.map((item,index)=><article className={`panel recommendation-card ${index===0?"recommendation-card-featured":""}`} key={item.skill_id}><div className="recommendation-card-top"><span className="recommendation-skill-name">{item.skill_name}</span>{item.priority!=="low"&&<span className={`priority-pill priority-${item.priority}`}>{item.priority==="high"?"Focus next":"Keep building"}</span>}</div><h2>{item.title}</h2><p className="recommendation-need">{recommendationSummary(item,result.source,studentSkills)}</p><div className="recommendation-plan"><div><span>Next step</span><p>{item.action}</p></div><div><span>Try this</span><p>{item.practice_activity}</p></div></div><details className="recommendation-why"><summary>Why this suggestion?</summary><p>{item.usefulness}</p></details><div className="recommendation-evidence"><span className="eyebrow">BASED ON YOUR QUIZ</span><strong>{item.evidence}</strong>{item.priority!=="low"&&<small>{item.priority_basis}</small>}</div><button className="button button-secondary recommendation-assessment-link" type="button" onClick={()=>onNavigate("assessment",item.skill_id)}>Choose {item.skill_name} quiz<Icon name="arrow" size={14}/></button></article>)}</div>
      </>}
    </>}
  </section>;
}

function recommendationSummary(item,source,studentSkills) {
  if (source === "groq") return item.need;
  const score = studentSkills.find((skill) => skill.skill_id === item.skill_id)?.latest_score;
  if (score == null) return item.need;
  const rounded = Math.round(score);
  if (item.priority === "high") return `Your ${item.skill_name} quiz score is ${rounded}%, so this is a good area to focus on next.`;
  if (item.priority === "medium") return `Your latest ${item.skill_name} score is ${rounded}%. A little targeted practice can help you keep building.`;
  return `Your latest ${item.skill_name} quiz score is ${rounded}%, meeting the current strength threshold. Try a more challenging exercise next.`;
}

function Progress({student,progress,assessments,skills,onNavigate}) {
  const [selectedSkill,setSelectedSkill]=useState("all");
  const points=[...(progress||[])].sort((a,b)=>new Date(a.assessed_at)-new Date(b.assessed_at));
  const visiblePoints=selectedSkill==="all"?points:points.filter((point)=>point.skill_id===selectedSkill);
  const skillsWithHistory=new Set(points.map((point)=>point.skill_id)).size;
  const latest=points.at(-1);
  return <section className="app-page" aria-labelledby="progress-title"><div className="page-heading"><Eyebrow>YOUR SAVED HISTORY</Eyebrow><h1 id="progress-title">Progress you can <span>look back on.</span></h1><p>Every point here comes from a completed quiz. Compare attempts within the same skill to see how your score changes.</p></div>
    <div className="progress-metrics"><Metric label="Quiz attempts" value={assessments?.length||0} detail="Saved assessments" icon="clipboard" tone="blue"/><Metric label="Skills with history" value={`${skillsWithHistory} / 6`} detail="Official skill areas" icon="layers" tone="green"/><Metric label="Latest activity" value={latest?new Date(latest.assessed_at).toLocaleDateString():"None yet"} detail={latest?latest.skill_name:"Take a quiz to begin"} icon="chart" tone="violet"/></div>
    {!points.length?<div className="progress-empty panel"><img className="progress-empty-image" src={progressImage} alt="Illustration of checkpoints on a progress path"/><div><span className="eyebrow">NO SAVED RESULTS YET</span><h2>{student?"Your first quiz starts your history.":"Set up your student profile first."}</h2><p>After a quiz is saved, you will see its score and date here. Nothing is added until you complete an assessment.</p><button className="button button-primary" onClick={()=>onNavigate(student?"assessment":"profile")}>{student?"Choose a quiz":"Set up profile"}<Icon name="arrow" size={15}/></button></div></div>:<>
      <section className="panel progress-chart-panel"><div className="progress-section-heading"><div><Eyebrow>REAL ASSESSMENT RESULTS</Eyebrow><h2>Scores over time</h2><p>Lines connect attempts for the same skill only.</p></div><label className="skill-filter">Filter by skill<select value={selectedSkill} onChange={(event)=>setSelectedSkill(event.target.value)}><option value="all">All skills</option>{skills.map((skill)=><option value={skill.id} key={skill.id}>{skill.name}</option>)}</select></label></div><ScoreTrendChart points={visiblePoints}/></section>
      <section className="panel progress-history-panel"><div className="progress-section-heading"><div><Eyebrow>ASSESSMENT LOG</Eyebrow><h2>Saved attempts</h2><p>Scores are shown as recorded by the assessment.</p></div><span className="history-count">{visiblePoints.length} result{visiblePoints.length===1?"":"s"}</span></div><ProgressHistory points={visiblePoints}/></section>
    </>}
  </section>;
}

function ProgressHistory({points}) {
  const ordered=[...(points||[])].sort((a,b)=>new Date(b.assessed_at)-new Date(a.assessed_at));
  const attemptsByRecord={}; let countBySkill={};
  [...(points||[])].sort((a,b)=>new Date(a.assessed_at)-new Date(b.assessed_at)).forEach((point)=>{countBySkill[point.skill_id]=(countBySkill[point.skill_id]||0)+1;attemptsByRecord[`${point.assessment_id}-${point.skill_id}`]=countBySkill[point.skill_id];});
  return <div className="history-table-wrap"><table className="history-table"><thead><tr><th scope="col">Skill</th><th scope="col">Date</th><th scope="col">Attempt</th><th scope="col">Score</th></tr></thead><tbody>{ordered.map((item)=><tr key={`${item.assessment_id}-${item.skill_id}`}><th scope="row">{item.skill_name}</th><td><time dateTime={item.assessed_at}>{new Date(item.assessed_at).toLocaleDateString(undefined,{year:"numeric",month:"short",day:"numeric"})}</time></td><td>{attemptsByRecord[`${item.assessment_id}-${item.skill_id}`]}</td><td><strong>{Math.round(item.score)}%</strong></td></tr>)}</tbody></table></div>;
}

function Profile({ student, onNavigate }) { return <section className="app-page profile-page" aria-labelledby="profile-title"><div className="page-heading"><img className="profile-logo-mark" src={brandMark} alt="" /><Eyebrow>STUDENT PROFILE</Eyebrow><h1 id="profile-title">A home for <span>your progress.</span></h1><p>Your account is connected to this private student profile.</p></div>{student ? <div className="panel existing-profile"><span className="large-avatar">{student.name[0].toUpperCase()}</span><div><span className="eyebrow">CONNECTED PROFILE</span><h2>{student.name}</h2><p>{student.email} · {student.program} · Batch {student.batch}</p></div><button className="button button-primary" onClick={() => onNavigate("dashboard")}>Open dashboard <Icon name="arrow" size={15}/></button></div> : <div className="notice" role="status">Your student profile is still loading.</div>}</section>; }

export default App;
