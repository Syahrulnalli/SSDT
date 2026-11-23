# SSDT Complete Project Documentation

**Project:** Student Skill Development Tracker (SSDT)
**Project type:** BCA capstone
**Updated:** 23 November 2026
**Repository baseline:** branch main, commit dc1245b before this change set

## 1. Executive summary

SSDT is a student-facing web application for taking separate quizzes in six technical skill areas, saving results, reviewing attempts, and receiving learning suggestions based on those results. Its stack is React/Vite, FastAPI/Uvicorn, SQLAlchemy, and PostgreSQL in normal mode. Optional demo mode uses an isolated in-memory SQLite database so authentication and quiz workflows can run without PostgreSQL. FastAPI serves the React build and API from one origin. Groq can optionally generate alternative recommendation wording when explicitly requested.

The repository also retains an older server-rendered Jinja preview that uses illustrative data from demo_data.py. When SERVE_FRONTEND is true, FastAPI serves React on web page routes; otherwise it renders the Jinja preview. React is the account-based UI connected to authenticated student APIs. In DEMO_MODE, a visible notice states that result data is temporary and reset at server restart.

Skill analysis is deterministic threshold and trend logic. Groq is optional language generation, not a trained predictive model. There is no model training pipeline or evaluation evidence in this repository. The ML extension module defines a future predictor interface but leaves the predictor unset.

## 2. Purpose, scope, and project roles

The application lets an individual student review the official skills, take a five-question quiz for one selected skill, save the result, compare attempts, review progress, and get next-step suggestions linked to their saved results.

Implemented scope includes account registration and login, a linked student profile, six fixed quizzes, assessment history, deterministic analysis, rule-based recommendations, and optional Groq wording. There is no trained ML prediction, administrator console, student directory, persisted recommendation history, or versioned database migration framework.

The role assignments below came from the project brief and do not assert contribution history:

| Member | Assigned responsibility |
| --- | --- |
| Syahrul Nalli | Backend |
| Sai Dhrasahn | Frontend |
| Salla Stalin | Database |

## 3. Technology stack and repository layout

| Area | Technology | Main location |
| --- | --- | --- |
| Frontend | React 19, JavaScript, Vite 8, CSS | frontend/src |
| API | Python, FastAPI, Uvicorn | backend/app, app.py |
| ORM | SQLAlchemy 2 | backend/app/models and services |
| Database | PostgreSQL through psycopg 3 in normal mode; in-memory SQLite in demo mode | DATABASE_URL and DEMO_MODE settings |
| Authentication | pwdlib Argon2, PyJWT, HttpOnly cookie | auth_service.py, core/security.py |
| Optional text generation | Groq SDK | groq_service.py, recommendation_service.py |
| Shared skill catalog | JSON and Python loader | skill_catalog.json, skill_catalog.py |
| Legacy UI | Jinja, static CSS/JS | templates, static, demo_data.py |
| Deployment prep | Docker multi-stage build, Render Blueprint | Dockerfile, render.yaml, DEPLOYMENT.md |

Key source modules:

- app.py exports the ASGI app for Uvicorn.
- backend/app/main.py builds FastAPI, middleware, exception handling, static mounts, and the React/Jinja serving choice.
- backend/app/api/router.py includes API route groups.
- backend/app/api/routes contains health, auth, students, skills, assessments, and insights.
- backend/app/core/config.py reads environment settings and validates production requirements.
- backend/app/core/database.py builds a PostgreSQL engine in normal mode, or an isolated SQLite in-memory engine in demo mode, and exposes the session dependency.
- backend/app/models defines User, Student, Skill, Assessment, and AssessmentResult.
- backend/app/schemas defines validated input and output structures.
- backend/app/services contains account, scoring, history, analysis, recommendation, Groq, and skill-catalog logic.
- backend/app/init_db.py contains explicit table initialization and idempotent skill seeding; it was not run during this documentation task.
- frontend/src/main.jsx mounts React. frontend/src/pages/App.jsx owns routes, state, and views; frontend/src/components/ui.jsx contains shared UI helpers; frontend/src/services/api.js centralizes requests; frontend/src/styles/styles.css contains application styles.
- frontend/src/assets contains logos, skill illustrations, and feature illustrations.
- tests contains API workflow, insight, and deployment configuration tests.
- README.md and DEPLOYMENT.md describe setup and deployment.
- .env.example contains placeholders. Real environment values are not included in this document.

## 4. Architecture and data flow

### Runtime architecture

    Browser: React application
       | same-origin /api requests with cookie credentials
       v
    FastAPI routes and validated schemas
       | session identity and ownership checks
       v
    Domain services
       | SQLAlchemy session
       v
    PostgreSQL: users, students, skills, assessments, results
       |
       +---- optional Groq call for explicitly requested wording

In local development, Vite normally runs at 127.0.0.1:5173 and FastAPI at 127.0.0.1:8000. The API client defaults to the FastAPI URL in Vite development unless VITE_API_BASE_URL or VITE_API_URL is set. Production builds default to relative /api paths. Docker builds Vite and copies its output into the Python runtime, where FastAPI serves the React app and API from one origin.

### Assessment submission

1. A signed-in student selects a skill.
2. React requests that skill's questions from GET /api/assessments/questions.
3. The response includes answer choices but excludes the correct-option IDs.
4. React posts the skill ID, five question IDs, and selected option IDs to POST /api/assessments.
5. FastAPI resolves the student from the logged-in account, checks the exact question set/options, then scores using the server-side answer key.
6. The service stores an assessment snapshot and one result for that skill.
7. React reloads the student's profile, skill summary, attempts, progress points, and analysis.

Scores are calculated on the server, not trusted from the browser. Five questions per skill means each correct answer contributes 20 percentage points, for a 0â€“100 result.

### Analysis and recommendation flow

Analysis joins result rows to their assessment dates and filters by the current account's linked student. It produces six catalog entries; an unassessed skill has null score rather than zero.

The recommendations page loads a deterministic endpoint by default. A separate action posts to the Groq generation endpoint. Generated JSON is validated and must include exactly the assessed skill IDs expected by the server. The server retains score evidence and priorities. If Groq or validation fails, deterministic suggestions are returned with an unavailable status.

## 5. React pages and reusable components

React navigation uses browser history and page mappings in App.jsx. On startup, the app requests /api/auth/me. Private pages redirect anonymous visitors to sign-in. The API client includes cookies in requests.

| Page | Purpose and data |
| --- | --- |
| Home (/) | Introduces SSDT and the six skills. Skill rows load from FastAPI; the canonical catalog is shown as a marked reference if the request fails. |
| Sign in (/login) | Accepts username or email and password and calls the login API. |
| Create account (/register) | Registers the account and linked student profile. |
| Dashboard (/dashboard) | Loads current profile, scores, assessment history, activity, and deterministic analysis. |
| Skills (/skills) | Lists the six official areas, catalog focus topics, current latest scores, and quiz links. |
| Assessment (/assessment) | Loads and runs one selected skill quiz, submits answers, and displays saved results. |
| Skill Analysis | Shown as a dashboard panel from /api/insights/analysis; it is not a separate route. |
| Progress (/progress) | Shows attempt totals, skills with history, latest activity, filtered score trends, and assessment log. |
| Recommendations (/recommendations) | Shows rule-generated advice by default; the user may request Groq wording. Includes loading, empty, error, priority, and evidence states. |
| Profile (/profile) | Displays the student profile associated with the signed-in account. |
| Unknown path | Current page lookup resolves unknown paths to the home view. |

Shared components/helpers include Icon, Eyebrow, SectionTitle, EmptyState, SkillApiStatus, Metric, ProfileCard, Notice, analysis panels and rows, ScoreTrendChart, RecentActivity, and ProgressHistory. Responsive styles are in styles.css. Illustrations are visual assets, not score or assessment data.

Network errors are converted to readable API messages. HTTP 401 triggers client-side session cleanup and return to sign-in. Loading, retry, empty, and error states are implemented where relevant. The catalog can provide a labeled fallback for skill presentation; private student data depends on the API.

## 6. Skills and assessment bank

The catalog in skill_catalog.json is shared by React and the backend. The six official IDs and names are:

| ID | Skill |
| --- | --- |
| python | Python |
| machine-learning | Machine Learning |
| artificial-intelligence | Artificial Intelligence |
| sql-databases | SQL & Databases |
| web-development | Web Development |
| problem-solving-algorithms | Problem Solving & Algorithms |

The catalog also has display symbols and focus topics. backend/app/services/assessment_question_bank.py contains five fixed questions per skill, 30 total. Correct answers remain server-side. The API schema requires exactly five unique question IDs and rejects unexpected fields such as a submitted score. The service rejects unknown skills, questions from another skill, missing questions, duplicate IDs, or invalid answer options.

Interactive attempts currently store one skill result per assessment. The database schema allows multiple results in one assessment, which is used by the imported historical records. An assessment response calculates its overall score as the average of the result rows it contains.

## 7. Analysis and recommendation rules

### Deterministic analysis

Default thresholds in backend/app/core/config.py:

- Below 60: needs_attention.
- 60 through less than 80: developing.
- 80 and above: strength.

SKILL_GAP_THRESHOLD and SKILL_STRENGTH_THRESHOLD can override these values, with required ordering 0 <= gap < strength <= 100. They classify a quiz score, not general mastery.

Per skill, analysis computes latest and previous scores, attempt count, score change, latest assessment time, trend, classification, strengths, and areas to improve. Attempts are ordered by timestamp and assessment ID. A single attempt has insufficient_history. A skill without attempts has null scores and not_assessed status.

### Rule-based suggestions

A low score yields high priority, a developing score medium priority, and a strength-range quiz result low priority. Advice contains the skill, need, action, practice activity, priority basis, evidence, and usefulness. Unassessed skills receive no recommendation. Responses are generated per request and are not persisted.

### Groq generation

Only POST /api/insights/recommendations/generate asks Groq to write recommendation text. The configured default model is openai/gpt-oss-20b and GROQ_MODEL can override it. The request is server-side and uses assessed skill IDs/names, scores, classifications, recent score/date pairs, and thresholds; it does not include names, email addresses, passwords, cookies, or API credentials.

Groq is asked for JSON and Pydantic validates the response. The returned skill IDs must match the expected assessed skills exactly. The server attaches score evidence and priorities from its deterministic suggestions. Provider calls use a ten-second timeout and no retries. Provider, timeout, rate-limit, and malformed-output failures preserve deterministic recommendations.

### What kind of AI/ML exists

| Capability | Present | Evidence |
| --- | --- | --- |
| Rule-based analysis | Yes | Threshold classification and comparison of recent attempts |
| Rule-based recommendations | Yes | Recommendations grounded in saved assessment results |
| Generative language | Optional | Explicit Groq recommendation action |
| Trained and evaluated ML model | No | No training or evaluation; ml_extension.py defines a protocol and sets predictor to None |

The app has analysis rules and optional language generation. It should not be described as containing a trained ML predictor.

## 8. API reference

All paths below are prefixed with /api.

| Method and endpoint | Access | Purpose |
| --- | --- | --- |
| GET /health | Public | Reports process status, PostgreSQL URL configuration, DEMO_MODE, and storage mode. |
| GET /health/database | Public | Executes SELECT 1; reports sqlite-demo in demo mode and does not present SQLite as PostgreSQL. |
| GET /health/groq | Public | Checks optional Groq configuration/connectivity; not a generation test. |
| POST /auth/register | Public, origin checked | Creates user and profile, sets session cookie. |
| POST /auth/login | Public, origin checked | Authenticates username/email and sets cookie. |
| GET /auth/me | Session cookie | Returns current user and linked student. |
| POST /auth/logout | Origin checked | Clears session cookie. |
| GET /skills | Public | Lists persisted official skills in catalog order. |
| GET /skills/{skill_id} | Public | Reads one official skill or returns 404. |
| GET /assessments/questions?skill_id=... | Public | Returns selected quiz questions without answer keys. |
| POST /students | Session cookie, origin checked | Creates a profile with account-matching email. |
| GET /students/{student_id} | Session and ownership | Reads only the caller's profile. |
| GET /students/{student_id}/skills | Session and ownership | Returns six current skill summaries. |
| GET /students/{student_id}/assessments | Session and ownership | Lists saved assessment snapshots. |
| GET /students/{student_id}/progress | Session and ownership | Returns chronological result history. |
| POST /assessments | Session, origin checked | Validates, scores, and saves an attempt. |
| GET /insights/analysis | Session cookie | Analyzes current user's student; accepts no student ID. |
| GET /insights/recommendations | Session cookie | Returns deterministic recommendations. |
| POST /insights/recommendations/generate | Session, origin checked | Requests Groq wording or deterministic fallback. |

Interactive Swagger/ReDoc docs are enabled outside production and disabled by production config. SQLAlchemy errors return a generic service-unavailable response without SQL parameters or connection details.

## 9. PostgreSQL schema and inspection

### Read-only findings

The configured local DATABASE_URL connected through SQLAlchemy during the database inspection on 19 November 2026. That schema/count inspection used a PostgreSQL read-only transaction. The later demo-mode tests used isolated in-memory SQLite and did not write to the configured PostgreSQL database.

| Table | Rows | Role |
| --- | ---: | --- |
| users | 2 | Login accounts |
| students | 103 | Linked and unlinked student profiles |
| skills | 6 | Official skill records |
| assessments | 105 | Assessment snapshots |
| assessment_results | 615 | Skill scores |
| student_import | 100 | Source/import student table |
| assessment_import | 600 | Source/import assessment rows |

All 100 source import profiles matched a students row with user_id NULL. Each of those 100 student profiles had exactly six result records across assessment history, representing six distinct skills. All six database skill names matched the canonical names above. The import rows were not attached to login accounts, and no public student directory endpoint exists.

These are counts from the locally configured database at inspection time, not confirmation of the production database.

### ORM comparison

The five application-managed tables were compared to SQLAlchemy model metadata. Column names, nullability, primary keys, foreign keys, indexes, unique constraints, score check constraint, and timestamp timezone declarations matched.

| Table | Structure |
| --- | --- |
| users | id INTEGER PK; username VARCHAR(32) unique/indexed; email VARCHAR(255) unique/indexed; password_hash VARCHAR(255); created_at timezone-aware timestamp. |
| students | id INTEGER PK; nullable user_id FK to users.id with ON DELETE SET NULL and unique index; name VARCHAR(120); email VARCHAR(255) unique/indexed; program VARCHAR(100); batch VARCHAR(20); created_at timezone-aware timestamp. |
| skills | id VARCHAR(64) PK; name VARCHAR(120) unique; description TEXT. |
| assessments | id INTEGER PK; student_id FK to students.id with ON DELETE CASCADE and index; assessed_at timezone-aware timestamp with server default and index. |
| assessment_results | id INTEGER PK; assessment_id FK to assessments.id with ON DELETE CASCADE and index; skill_id FK to skills.id with ON DELETE RESTRICT and index; score NUMERIC(5,2); unique assessment_id + skill_id; check score between 0 and 100. |

The source import tables are present in PostgreSQL but are not ORM-mapped.

Relationships:

    users 1 --- 0..1 students
    students 1 --- many assessments
    assessments 1 --- many assessment_results
    skills 1 --- many assessment_results

## 10. Authentication, privacy, and integrity

- pwdlib's recommended Argon2 configuration hashes passwords.
- JWT tokens use HS256 with issuer, audience, issue time, and expiry claims; the token is stored in an HttpOnly cookie.
- AUTH_COOKIE_SECURE controls Secure; production requires it true. SameSite is Lax.
- Production checks require PostgreSQL when DEMO_MODE=false. Demo production requires configured demo credentials. Both modes require a JWT key of at least 32 bytes, secure cookies, React serving, and AUTO_CREATE_TABLES=false.
- Write endpoints enforce allowed/same-site request origin.
- Profile and history queries check that student.user_id belongs to the current user. Analysis and recommendations derive the student identity from the session.
- Imported profiles have NULL user_id and are not login accounts; they remain inaccessible through owner-specific private routes.
- Scores are computed by the backend. Database constraints restrict scores to 0â€“100 and prevent duplicate skill rows in one assessment.
- Secrets are not included here. The Docker image does not copy local .env files.

In DEMO_MODE, the backend compares login input against DEMO_USERNAME and DEMO_PASSWORD from server environment settings. It creates one temporary demo profile in the isolated in-memory SQLite store, disables normal account registration, and uses the existing authenticated cookie and student-ownership routes. The demo account is not written to PostgreSQL. The React application shows a persistent-on-page demo notice; results disappear when the application process restarts.

## 11. Tests and checks actually run

Run date: 23 November 2026 for the deployment-preparation changes. Earlier database inspection results are dated 19 November 2026; current aggregate counts were rechecked read-only on 23 November 2026.

| Command or check | Result |
| --- | --- |
| .\.venv\Scripts\python.exe -m pytest -q | Passed: 43 tests; one Starlette deprecation warning for TestClient/httpx. |
| .\.venv\Scripts\python.exe -m compileall -q backend app.py skill_catalog.py | Passed with no syntax errors. |
| SQLAlchemy schema/count inspection in a read-only transaction | Passed: connection, table counts (103 students, 105 assessments, 615 results), imported-profile aggregate, six results per imported profile, official skill names. |
| SQLAlchemy metadata comparison | Passed for five ORM tables, including constraints/indexes. |
| Demo-mode subprocess integration (FastAPI + React serving + auth + quiz + analysis + progress + recommendations + logout) | Passed against isolated in-memory SQLite; supplied unreachable PostgreSQL URL was not used. Registration disabled; invalid login rejected; valid demo login worked. |
| Demo-mode process restart check | Passed: in-memory assessment history was reset after process restart. |
| Local configured PostgreSQL smoke check | Passed: health/database reported PostgreSQL, React login page and built asset returned HTTP 200, invalid test login returned 401. No database writes were made. |
| Staged frontend npm ci and npm run build, Node 24.21.0 | Passed; Vite 8.3.5 transformed 35 modules. |
| Browser visual/console check | Not performed. |
| Live Groq recommendation generation | Not performed; automated provider tests use mocks. |
| Public Render deployment/hosted DB | Not verified; no provider runtime check was made. |

The Vite build ran from an isolated dependency staging directory after the frontend structure changes. Demo-mode tests and subprocess checks used isolated in-memory SQLite; the configured PostgreSQL database was inspected read-only and its records were preserved.

Current tests cover empty, one-skill, multiple-skill data; latest/previous scores; improving, declining, unchanged trends; thresholds and recommendation evidence; student isolation; authentication/ownership; assessment submission and client score rejection; Groq missing configuration, timeout, rate limit, malformed/wrong-skill output, deterministic fallback, and recommendation non-persistence. See tests/test_skill_insights.py and tests/test_api_workflows.py.

## 12. Local setup and use

Prerequisites: Python 3.11+, Node.js 22.12+ or 20.19+, and npm. PostgreSQL 14+ (project brief specifies PostgreSQL 18) and DATABASE_URL are required only when DEMO_MODE=false.

Windows PowerShell commands from the repository root:

    Copy-Item .env.example .env
    notepad .env
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -m backend.app.init_db

For normal PostgreSQL mode, the initializer creates missing application tables, performs additive setup for students.user_id/index, and idempotently seeds skills. It is not a versioned migration system. Review it and the target database before running. For demo mode, set DEMO_MODE=true and configure DEMO_USERNAME and DEMO_PASSWORD in the backend environment. The app creates an isolated in-memory SQLite schema and seeds the official skills at startup. Demo results are temporary and never written to PostgreSQL.

Start FastAPI:

    uvicorn app:app --reload

Open http://127.0.0.1:8000. Development API docs are at http://127.0.0.1:8000/docs.

For separate Vite development, use another terminal:

    Set-Location frontend
    npm install
    npm run dev

Open http://127.0.0.1:5173. In development the API defaults to 127.0.0.1:8000 unless a VITE_API_BASE_URL or VITE_API_URL override is set. FRONTEND_ORIGINS must permit the local frontend for credentialed cross-origin writes.

Local checks:

    .\.venv\Scripts\python.exe -m pytest -q
    .\.venv\Scripts\python.exe -m compileall -q backend app.py skill_catalog.py
    Push-Location frontend
    npm ci
    npm run build
    Pop-Location

If using the bundled Node runtime, add its directory to PATH in that PowerShell session before npm commands. Tests use isolated test databases.

## 13. Deployment preparation and status

render.yaml prepares a single Render Docker web service:

- GitHub repository Syahrulnalli/SSDT, branch main.
- Root directory, Docker context, and Dockerfile location are the repository root and ./Dockerfile.
- Docker builds the React assets using npm ci and npm run build.
- FastAPI serves the built React app and API from one origin.
- Uvicorn uses Render's PORT, with 10000 as image default.
- Health check path is /api/health/database; in the prepared Blueprint this reports the temporary SQLite demo store.
- No first-deploy database hook or PostgreSQL resource is needed for demo mode. The app initializes only its ephemeral SQLite store at startup.
- DEMO_USERNAME and DEMO_PASSWORD are required provider-side values; JWT_SECRET_KEY is generated by the Blueprint. GROQ_API_KEY is optional and backend-only.
- Persistent PostgreSQL mode requires DEMO_MODE=false and a separately configured DATABASE_URL.

Git inspection showed main at dc1245b tracking origin/main for https://github.com/Syahrulnalli/SSDT. Git status also showed an untracked supabase.txt. Its contents were not inspected, staged, or changed.

Repository configuration is not proof of a live service. The local PostgreSQL connection does not verify the host database. Deployment should be verified by comparing Render's commit to GitHub main, reviewing deployment logs, and testing the public HTTPS website and API. DEPLOYMENT.md contains the provider checklist and synthetic-account smoke procedure.

## 14. Strengths, limitations, future work

### Strengths

- One canonical skill catalog shared across UI and backend.
- Independent quizzes with server-side answer keys and scoring.
- Analysis and suggestions based on saved results.
- Student ownership checks on private records.
- Unassessed skills remain null instead of fabricated zero scores.
- Groq is optional and has schema validation plus deterministic fallback.
- Same-origin production architecture is prepared.
- Tests cover important account, assessment, analysis, and provider-failure behavior.

### Limitations

- Five fixed quiz items per skill do not establish a validated assessment.
- Thresholds are rules, not validated predictors.
- No trained/evaluated ML model exists.
- Recommendation history is not persisted; Groq wording requires an explicit action.
- Import tables are not ORM models or an admin directory.
- Imported profiles with NULL user_id cannot log in.
- Jinja demo pages remain and are served when React mode is disabled.
- No versioned migration framework is present.
- Browser console, live Groq generation, and public Render deployment were not tested in this task.

### Suggested next work

1. Introduce reviewed, versioned migrations before future schema changes.
2. Expand and validate assessment items before using scores for high-stakes decisions.
3. If prediction is required, define a target/time window, consent and data governance, collect adequate longitudinal data, and evaluate against a baseline with leakage-safe splits before claiming ML.
4. If a student directory is required, make it admin-only with field minimization, role checks, auditability, and privacy tests.
5. Perform browser and public Render checks using synthetic accounts.
6. Decide whether recommendation history or feedback is a product requirement.

## 15. Verification summary

The optional Render demo mode was implemented and verified end to end with the existing FastAPI/SQLAlchemy routes against a real in-memory SQLite test store. It does not use PostgreSQL: configured demo credentials authenticate one temporary student, registration is disabled, and quiz, analysis, progress, and deterministic recommendations work until the server process restarts. Normal PostgreSQL mode remains in place. The read-only PostgreSQL check confirmed 103 students, 105 assessments, 615 results, and the imported sample records remain unlinked with six results each; no records were modified.

The backend suite passed 43 tests, Python compilation passed, the Vite production build passed, and the local PostgreSQL-mode API/React smoke checks passed. The deployment configuration, React/API structure, backend demo support, tests, README, deployment guide, and this documentation file were changed. Live Groq recommendation generation, browser console inspection, and public Render deployment remain untested.
