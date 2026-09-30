# FitBuddy — AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite application based on the supplied FitBuddy project documentation.

## Included
- FastAPI backend and Jinja2 templates
- SQLAlchemy + SQLite persistence
- Current Google GenAI Python SDK (`google-genai`)
- Structured Gemini JSON output validated by Pydantic
- 7-day workout generation
- Nutrition/recovery guidance
- Feedback-based plan revisions
- Local user/admin dashboard
- Responsive frontend
- Mock AI mode for testing without a Gemini key
- Pytest coverage for the main flow
- VS Code debug configuration

## Model update
The source document used the older `google-generativeai` SDK and Gemini 1.5 model names. This project uses the current Google GenAI SDK and configurable model names:
- `GEMINI_WORKOUT_MODEL=gemini-3.1-pro-preview`
- `GEMINI_FAST_MODEL=gemini-3.8-flash`

If a model is unavailable to your API account, change those environment variables.

## Run in VS Code / Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs.

For a no-key test, keep `MOCK_AI=true`. For Gemini, set `GEMINI_API_KEY` and `MOCK_AI=false`.

## Tests
```powershell
pytest -q
```

## Routes
- `GET /` — home
- `POST /generate-workout` — create/update user and generate plan
- `POST /submit-feedback` — revise plan
- `GET /view-all-users` — local admin view
- `POST /delete-user/{user_id}` — delete user
- `GET /health` — health check
- `GET /docs` — Swagger UI

## Safety
This is general wellness software, not medical advice. Review AI-generated guidance and seek qualified professional advice where appropriate. The local admin page has no authentication and should not be exposed publicly without adding access control.

## Verification performed
The packaged project was syntax-compiled and its offline/mock automated test suite passed (`4 passed`). Live Gemini calls were not executed in this environment because outbound package/network access is unavailable here; the Gemini integration follows Google's current GenAI SDK and structured-output API documented for the configured models.
