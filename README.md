# Cloud-Native Notes Management System

A simple Flask notes app that I built mainly to learn and practice **DevOps basics** — Docker, GitHub Actions, and CI/CD. The notes app (login, add/edit/delete notes, etc.) is just the project I used to practice setting up an actual deployment pipeline. The real focus here is the **CI/CD workflow**.

## What I was trying to learn

How code goes from "written on my laptop" to "live on the internet" automatically:

1. I push my code to GitHub (`main` branch)
2. GitHub Actions picks it up automatically and runs a pipeline (install dependencies, build a Docker image)
3. If that pipeline succeeds, it triggers a deploy on Render
4. Render pulls the latest code from GitHub and redeploys the app

So basically: push code → it goes live, with no manual steps in between. This is the core idea of CI/CD and was the whole point of this project for me.

## The CI/CD pipeline

This is my workflow file at `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ "main" ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Build Docker Image
      run: docker build -t my-notes-api .

    - name: Deploy to Render
      uses: johnbeynon/render-deploy-action@v0.0.8
      with:
        service-id: ${{ secrets.RENDER_SERVICE_ID }}
        api-key: ${{ secrets.RENDER_API_KEY }}
```

**What each step does:**
- `checkout` — grabs my latest code from the repo
- `setup-python` — sets up Python 3.9 to run things in
- `Install dependencies` — installs everything from `requirements.txt`
- `Build Docker Image` — builds the app into a Docker image, just to confirm it builds cleanly
- `Deploy to Render` — calls Render's API to tell it to redeploy

**Secrets needed** (added under repo Settings → Secrets and variables → Actions):
- `RENDER_SERVICE_ID`
- `RENDER_API_KEY`

**How Render fits in:** Render is set to auto-deploy whenever it sees a new commit on `main` (Git-based deploy). The Actions workflow above builds/checks everything first, then pings Render to actually do the redeploy.

```
push to main
   → GitHub Actions runs (checkout, setup python, install deps, build docker image)
   → triggers Render deploy action
   → Render pulls latest code and redeploys
   → app is live
```

## Tech used

- **Backend:** Flask
- **Database:** SQLite + Flask-SQLAlchemy
- **Auth:** Flask-Login + Werkzeug (password hashing)
- **Containers:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **Hosting:** Render

## Project structure

```
.
├── .github/workflows/ci.yml   # the CI/CD pipeline
├── app.py                     # Flask app — routes, models, templates
├── dockerfile
├── docker_compose.yaml
├── requirements.txt
└── notes.db                   # created automatically when app runs
```

## Running it locally

**With Docker:**
```bash
docker compose -f docker_compose.yaml up --build
```

**Without Docker:**
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

App runs at `http://localhost:5000`.

## About the notes app itself

Since I needed a real working app to deploy, I built a basic notes manager with:
- Login/register (passwords are hashed, not stored in plain text)
- Add, edit, delete, and pin notes
- Categories (General, Work, Personal, Ideas, Important)
- Search and filter on the dashboard
- A `/health` route Render can use to check the app is alive

## Things I want to add next

Mostly pipeline-related, since that's what I'm focused on learning:
- Add a test step in the pipeline before it builds/deploys (so broken code never gets deployed)
- Actually push the built Docker image somewhere (right now it just builds locally in CI and doesn't get used by the deploy step)
- Maybe a staging branch before main, so I can test changes before they go live
- Switch the Dockerfile to run with Gunicorn instead of the Flask dev server

## Note on secrets

The `SECRET_KEY` in `app.py` has a placeholder default — I should set a real one as an environment variable on Render instead of relying on that.

---

Built by **Suseendar Akash L** while learning DevOps fundamentals — Docker, GitHub Actions, and CI/CD with Render.
