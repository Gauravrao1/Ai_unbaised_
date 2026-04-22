# BiasLens AI - Unbiased AI Decision-Making Dashboard 

BiasLens AI is a full-stack fairness intelligence product that detects, visualizes, explains, and mitigates bias in ML systems. It is designed for hackathons, but the structure and workflows are production-oriented: clear API boundaries, persisted uploads, explainability with Gemini, fairness metrics with Fairlearn and AIF360, and a dashboard that surfaces tradeoffs instead of hiding them.

## What it does

- Upload a CSV dataset and optionally a trained model.
- Auto-detect likely sensitive attributes such as gender, caste, age, and income.
- Compute core fairness metrics:
  - Demographic parity difference
  - Equal opportunity difference
  - Disparate impact
  - Statistical parity difference
- Render a modern dashboard with scorecards, charts, protected-group comparison, and before/after mitigation.
- Convert fairness metrics into plain-English explanations with Gemini.
- Suggest mitigations such as reweighing, data balancing, threshold adjustment, and fairness constraints.
- Include an India-specific hiring dataset that highlights gender and caste bias.

## Project structure

```text
biaslens-ai/
  backend/
    app/
      core/
      data/
      models/
      routes/
      services/
      main.py
    requirements.txt
    .env.example
    uploads/
  frontend/
    src/
      components/
      lib/
      pages/
      App.jsx
      main.jsx
    Dockerfile
    package.json
    tailwind.config.js
    vercel.json
  README.md
  docker-compose.yml
  pitch-deck.md
  .github/workflows/ci.yml
  render.yaml
  demo-script.md
```

## Clean architecture

- `routes/` handles HTTP endpoints.
- `services/` contains the fairness engine, mitigation logic, explanation layer, and file persistence.
- `models/` defines request and response schemas.
- `core/` contains runtime configuration.
- `frontend/` contains the dashboard UI and API integration.

## Backend setup

Requirements: Python 3.10+.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Backend endpoints:

- `POST /upload`
- `POST /analyze-bias`
- `POST /mitigate`
- `POST /explain`
- `GET /health`

## Frontend setup

Requirements: Node.js 18+.

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Set `VITE_API_URL` to your backend URL if you are not running locally.

## Demo data

Use the included India-specific sample file:

- `backend/app/data/hiring_bias_sample.csv`
- `backend/app/data/hiring_bias_validation.csv`

`hiring_bias_sample.csv` simulates a hiring dataset with stronger bias signals for the live demo.

`hiring_bias_validation.csv` is a more balanced validation dataset you can use to check that the pipeline, charts, and explanation layer still work on a cleaner fairness test case.

## AI explanation layer

To enable Gemini explanations, set `GEMINI_API_KEY` in `backend/.env`. If the key is missing, the backend falls back to a deterministic human-readable explanation so the product still works during a live demo.

## Deployment steps

### Backend on Render

1. Create a new Web Service on Render.
2. Connect the repo.
3. Set the root directory to `backend`.
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables from `backend/.env.example`.
7. Deploy and copy the backend URL.

### Frontend on Vercel

1. Create a new Vercel project.
2. Set the root directory to `frontend`.
3. Set `VITE_API_URL` to the Render backend URL.
4. Build command: `npm run build`
5. Output directory: `dist`
6. Deploy.

### Local Docker setup

```bash
docker compose up --build
```

This starts the FastAPI backend on port `8000` and the built frontend on port `5173`.

## CI

A GitHub Actions workflow in `.github/workflows/ci.yml` builds and validates both services on push and pull request.

## Why this scores well in a hackathon

### Technical

- Uses a real fairness stack: FastAPI, Fairlearn, AIF360, scikit-learn, pandas.
- Includes a persisted upload flow and a mitigation pipeline.
- Separates analysis, explanation, and UI concerns cleanly.

### Innovation

- Turns fairness numbers into a conversational AI explanation.
- Adds a bias risk score and a mitigation comparison.
- Makes bias visible to non-technical stakeholders.

### Impact

- Strong fit for UN SDG 10 because it highlights inequality in hiring, lending, and public-sector decisions.
- India-specific caste and gender lens increases relevance and narrative strength.

### UX

- Dashboard-first product instead of a notebook-style demo.
- Card-based metrics, charts, and clear callouts.
- AI insight panel keeps the story understandable during a live pitch.

## Fairness metric interpretation

- Demographic parity difference close to 0 is better.
- Equal opportunity difference close to 0 is better.
- Disparate impact between 0.8 and 1.25 is generally safer.
- Statistical parity difference close to 0 is better.

## Downloadable report

The frontend can export the current analysis, mitigation output, and explanation as JSON for sharing with judges or stakeholders.

## Example pitch positioning

BiasLens AI is not just an analytics dashboard. It is a decision support layer for organizations that want to deploy ML responsibly while reducing inequality across protected groups.

## Notes

- If a trained model upload fails to load, the backend falls back to a baseline logistic regression so the demo still works.
- The included sample dataset is synthetic but structured to mimic India-focused hiring bias patterns.
