# Student Skill Development Tracker

A BCA capstone project for assessing six official student skills, identifying areas for growth, and tracking progress. The React dashboard uses saved PostgreSQL assessment results for deterministic skill analysis and can request Groq-generated learning guidance.

## Stack and current status

- Python, FastAPI, Uvicorn, SQLAlchemy, PostgreSQL, psycopg 3, and the Groq Python SDK.
- The existing HTML/Jinja pages remain served by FastAPI. The separate React/Vite frontend MVP is in `frontend/`; it communicates with FastAPI, while Groq requests stay in the backend.
- PostgreSQL is the source of truth for students, skills, assessments, and assessment results. Skill display metadata comes from the canonical catalog.
- The preserved server-rendered Jinja preview pages still use illustrative data from `demo_data.py`. The React application uses authenticated FastAPI endpoints and saved PostgreSQL results for student analysis and recommendations.
- The six official skills are Python, Machine Learning, Artificial Intelligence, SQL & Databases, Web Development, and Problem Solving & Algorithms.

## Requirements

- Python 3.11 or newer
- PostgreSQL 14 or newer
- Node.js 22.12+ (or 20.19+) and npm for the React/Vite frontend.

## Public deployment

The production option prepared for this repository is a single Docker-based Render web service. It builds React/Vite into static files served by FastAPI, so the browser uses one HTTPS origin for the UI and API. PostgreSQL and Groq remain server-side services. The deployment blueprint does not create a database or transfer local records.

See [DEPLOYMENT.md](DEPLOYMENT.md) for the ordered GitHub/Render setup, required provider-side secrets, one-time schema initialization, public smoke checks, and current free-tier limitations. Production startup requires PostgreSQL, a private JWT key, HTTPS cookies, the built React app, and `AUTO_CREATE_TABLES=false`; it fails closed when those requirements are missing.

## PostgreSQL setup on Windows

Install PostgreSQL using the official Windows installer linked from [postgresql.org](https://www.postgresql.org/download/windows/). During setup, remember the password you assign to the `postgres` database user and keep the default port `5432` unless you choose another one.

The project database is named `student_skill_tracker`. If it has not already been created, create it from PowerShell (you will be prompted for the `postgres` password):

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -h localhost -p 5432 -c "CREATE DATABASE student_skill_tracker;"
```

If your PostgreSQL installation is in another versioned folder, change `18` in the executable path. Skip the command if the database already exists.

## Configure and initialize

From the project root:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set `DATABASE_URL` in `.env` to your own local username and password. The `.env.example` value is only a placeholder; do not commit real credentials. Keep `FRONTEND_ORIGINS` restricted to the actual local frontend origin. The default entries support common React/Vite development ports.

Create and activate a virtual environment, then install dependencies and initialize the schema:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m backend.app.init_db
```

The initialization command creates the `students`, `skills`, `assessments`, and `assessment_results` tables, then idempotently seeds the six official skills. The development server also runs this initializer on startup while `AUTO_CREATE_TABLES=true`. Set that variable to `false` when a migration workflow is introduced.

## Start the application

```powershell
uvicorn app:app --reload
```

Open the existing site at `http://127.0.0.1:8000`. FastAPI's interactive documentation is at `http://127.0.0.1:8000/docs`; ReDoc is at `http://127.0.0.1:8000/redoc`.

## API overview

- `GET /api/health` — API process status and whether a database URL is configured.
- `GET /api/health/groq` — safe Groq configuration and model connectivity check.
- `GET /api/health/database` — PostgreSQL connectivity check.
- `GET /api/skills` and `GET /api/skills/{skill_id}` — read the seeded official skill rows.
- `POST /api/students` and `GET /api/students/{student_id}` — create and retrieve profiles.
- `GET /api/students/{student_id}/skills` — latest recorded score for each official skill.
- `POST /api/assessments` and `GET /api/students/{student_id}/assessments` — save and list assessment snapshots.
- `GET /api/students/{student_id}/progress` — historical assessment results.
- `GET /api/insights/analysis` — six-skill analysis for the authenticated student; identity comes from the session cookie.
- `GET /api/insights/recommendations` — deterministic learning suggestions based on the current student's saved results.
- `POST /api/insights/recommendations/generate` — explicitly ask Groq to personalize recommendation text for the current student; scores, evidence, and priority remain server-calculated.

Assessment scores use the existing 0–100 percentage convention. Analysis and recommendation endpoints require the existing authenticated session. They do not accept a student ID from the browser.

## Groq integration foundation

The official `groq` Python SDK is a backend dependency. Groq credentials and requests stay inside FastAPI; the React app does not receive the API key or call Groq from the browser.

Create or edit the root `.env` file and set:

```dotenv
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-20b
```

Put the real key only in `.env`. The repository `.gitignore` excludes that file; never commit the key or place it in frontend variables, source files, logs, or API responses. `GROQ_MODEL` can be changed locally without editing code. If `.env` already exists, add these values to it instead of replacing the file.

To check the configuration and make one minimal request to the configured model, start FastAPI and run:

```powershell
curl.exe http://127.0.0.1:8000/api/health/groq
```

The endpoint returns only whether a key is configured, the model name, connection status, and a safe error message. It does not submit student data. Missing `GROQ_API_KEY` does not prevent the application from starting.

Groq is called only by the authenticated recommendation-generation endpoint. It receives a compact summary of attempted skill IDs/names, latest and previous scores, trend classifications, and at most three recent score/date pairs per attempted skill. Names, email addresses, passwords, cookies, database credentials, and API keys are not sent. The model returns JSON text validated against Pydantic schemas; invalid output or provider failures produce clearly labeled rule-based suggestions instead of claiming AI succeeded. The configured model is used, and keys remain server-side.

## Skill analysis and recommendations

The React student area now reads saved assessment results from PostgreSQL through FastAPI. The deterministic analysis always returns the six canonical skills. A skill with no attempts has `latest_score: null`, no trend, and no gap classification. Each attempted skill shows its latest and previous result, the score-point change when two comparable attempts exist, attempt count, most recent date, trend status, and score-based strengths or improvement notes. Because the current quizzes each contain five questions and scores use the same percentage scale, two attempts for the same skill can be compared. A single attempt is never labeled an improvement or decline.

Gap rules are configurable in the backend `.env`:

```dotenv
SKILL_GAP_THRESHOLD=60
SKILL_STRENGTH_THRESHOLD=80
```

A latest score below the attention threshold is classified `needs_attention`; a score from that threshold up to (but not including) the strength threshold is `developing`; a score at or above the strength threshold is a current `strength`. Configuration must satisfy `0 <= gap < strength <= 100`. These rules classify quiz results; they do not claim broad mastery.

`GET /api/insights/recommendations` returns deterministic, evidence-backed suggestions without contacting Groq. The recommendations page offers an explicit **Generate AI guidance** action to call Groq. The model may personalize titles and suggested actions, but the server attaches the saved score evidence and threshold-based priority. Unattempted skills receive no recommendations. Recommendations are not persisted in this MVP: each GET recomputes the current rule-based response, and generation is an explicit request. No recommendation table or database migration was needed, and dashboard refreshes do not create records or duplicate provider calls.

Threshold analysis and Groq text are not trained machine learning. There is no predictive model trained or evaluated in this phase. `backend/app/services/ml_extension.py` defines a small injectable predictor protocol as a future extension point, with no configured predictor. A defensible model would need an appropriately consented, sufficiently large longitudinal dataset, a clearly defined prediction target and time window, leakage-safe train/validation/test splits, a baseline, and evaluation metrics appropriate to that target. The current records are not enough evidence to claim predictive validity.

To run the backend tests and frontend production build:

```powershell
python -m pytest -q
Set-Location frontend
npm run build
```

The test suite uses a temporary in-memory test database and does not modify the configured PostgreSQL database or existing student data.

## React integration status

The local React MVP preview is separate from the existing Jinja pages. To start it from the project root:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. This is a local preview only. The React UI imports the same root `skill_catalog.json` as FastAPI and calls the backend for student, assessment, progress, analysis, and recommendation APIs. It never calls Groq directly. The six independent quizzes use fixed server-side answer keys and server-calculated scores.
