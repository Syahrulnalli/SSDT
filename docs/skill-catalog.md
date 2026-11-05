# Official Skill Framework

**Status:** Official initial framework

The Student Skill Development Tracker will assess exactly these six core skills. The names and ordering below are the canonical labels to use across the app, assessments, data, analysis, recommendations, visualizations, and reports.

| ID | Official skill | Assessment focus |
| --- | --- | --- |
| `python` | Python | Fundamentals; writing programs; functions, loops, conditions, and data structures; libraries; practical solutions. |
| `machine-learning` | Machine Learning | Fundamental concepts; supervised and unsupervised learning; common algorithms; training and evaluating models; performance and predictions. |
| `artificial-intelligence` | Artificial Intelligence | Fundamental concepts; intelligent systems; AI-based problem solving; techniques and applications; practical use. |
| `sql-databases` | SQL & Databases | Relational databases; SQL queries; creating and managing structures; retrieving and manipulating data; entity relationships. |
| `web-development` | Web Development | Frontend fundamentals; HTML, CSS, and JavaScript; backend and web application concepts; FastAPI in this project. |
| `problem-solving-algorithms` | Problem Solving & Algorithms | Logical thinking; decomposing problems; algorithm design; algorithms and data structures; efficient computational solutions. |

## Framework rules

- Track exactly these six top-level categories.
- Do not add Data Science as a skill.
- Keep technologies such as HTML, CSS, JavaScript, and FastAPI within Web Development; they are not separate top-level skills.
- Keep Python libraries within Python; they are not separate top-level skills.
- Use the exact official skill names consistently.

## Decisions still open

- The assessment questions and scoring methodology.
- How scores map to skill gaps and development priorities.
- The ML approach and its role in producing personalized recommendations.
- The learning-resource catalog.

The initial PostgreSQL schema stores student profiles, the six official skills, assessment snapshots, and per-skill assessment results. Progress history is queried from those dated results.
