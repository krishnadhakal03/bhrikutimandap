# CI/CD Flow (Local Dev → Git Push → VPS Deploy)

This document describes the current CI/CD pipeline for this repo, using Docker on a Hostinger VPS and GitHub Actions for automated tests + deployment.

## What You Have (Architecture)

- **Source of truth**: GitHub `main` branch
- **CI/CD runner**: GitHub Actions workflow at `.github/workflows/ci-cd.yml`
- **Production host**: VPS
  - App directory: `/opt/bhrikutimandap`
  - Runs via Docker Compose: `compose.prod.yml`
  - Environment file: `/opt/bhrikutimandap/.env.prod`
  - Database: PostgreSQL container (`db` service)
  - Django: Gunicorn in `web` container
  - Nginx: runs on the VPS host and reverse-proxies to `127.0.0.1:8000`

Important: **the VPS does not “pull” by itself**. GitHub Actions SSH-es into the VPS and runs `git pull` + Docker commands.

---

## 1) Local Development Workflow

### 1.1 Run locally
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

### 1.2 Before pushing
Run checks and tests:
```bash
python manage.py check
python manage.py test
```

### 1.3 Commit + push
```bash
git add -A
git commit -m "Describe change"
git push origin main
```

What happens next:
- GitHub Actions starts a workflow run.
- If tests pass and deployment succeeds, production gets updated.

---

## 2) GitHub Actions Workflow (What Runs)

Workflow file: `.github/workflows/ci-cd.yml`

### Job: `test`
Runs on every `push`, `pull_request`, and manual `workflow_dispatch`.
- Checks out code
- Installs Python dependencies
- Runs:
  - `python manage.py check`
  - `python manage.py test`

### Job: `build-and-push` (optional)
Runs on `push` events only.
- Builds a Docker image
- Pushes it to GHCR (`ghcr.io/...`)

Note: Your deployment job builds on the VPS, so GHCR is not required for production. If `build-and-push` fails but deploy is fine, the workflow run still appears red. You can remove/disable it if you don’t need registry images.

### Job: `deploy`
Runs on:
- `push` to `main`
- manual `workflow_dispatch`

Deploy steps (high-level):
1. SSH to VPS (using GitHub Secrets)
2. Ensure `/opt/bhrikutimandap` exists and repo is cloned
3. `git pull origin main`
4. Require `.env.prod` to exist
5. `docker build -t bhrikutimandap:deploy .`
6. `docker compose --env-file .env.prod -f compose.prod.yml up -d`
7. Run Django migrations + collectstatic
8. Health check `curl http://127.0.0.1:8000/`

---

## 3) Required GitHub Secrets

In GitHub repo → **Settings → Secrets and variables → Actions**:

- `VPS_HOST` – VPS IP or hostname (example: `72.62.198.204`)
- `VPS_USER` – SSH user (often `root`)
- `VPS_SSH_KEY` – private key used by GitHub Actions to SSH into the VPS

Security note:
- If an SSH private key was ever exposed, **rotate it immediately** (generate a new keypair, update VPS `authorized_keys`, update `VPS_SSH_KEY`, and stop using the old key).

---

## 4) VPS Production Setup Requirements

On the VPS:
- Docker Engine installed
- Docker Compose plugin installed (`docker compose version` works)
- Repo exists at `/opt/bhrikutimandap` (the deploy job can clone it)

The file `/opt/bhrikutimandap/.env.prod` must exist.

Typical `.env.prod` values (example):
```bash
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=False
ALLOWED_HOSTS=bhrikutimandap.com,www.bhrikutimandap.com

DATABASE_ENGINE=postgresql
DATABASE_NAME=bhrikuti_db
DATABASE_USER=bhrikuti_user
DATABASE_PASSWORD=...
DATABASE_HOST=db
DATABASE_PORT=5432

SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 5) Manual Deploy (Workflow Dispatch)

If you want to deploy without pushing a new commit:
1. GitHub → **Actions** → select **CI/CD**
2. Click **Run workflow**
3. Choose branch `main`

This triggers `test` then `deploy`.

---

## 6) Verifying a Deploy on the VPS

Check current code version:
```bash
cd /opt/bhrikutimandap
git rev-parse HEAD
```

Check containers:
```bash
cd /opt/bhrikutimandap
docker compose --env-file .env.prod -f compose.prod.yml ps
```

Check app health from the VPS:
```bash
curl -I http://127.0.0.1:8000/
```

---

## 7) Common Failures + Fixes

### A) Workflow is red but tests are OK
Likely `build-and-push` failed.
- If you don’t need GHCR images, remove/disable that job.

### B) Deploy SSH fails
Common causes:
- Wrong `VPS_HOST` / `VPS_USER`
- `VPS_SSH_KEY` secret has formatting issues (missing newlines)
- VPS does not have the matching public key in `~/.ssh/authorized_keys`

### C) Deploy fails: `.env.prod missing`
Create it at:
- `/opt/bhrikutimandap/.env.prod`

### D) Deploy fails: permissions in `/opt/bhrikutimandap`
If using `root`, permissions are simplest.
If using a non-root user, ensure it can run Docker and write to the folder.

---

## 8) Admin Access (Production)

If you forgot admin login credentials, create a new superuser on the VPS:
```bash
cd /opt/bhrikutimandap
docker compose --env-file .env.prod -f compose.prod.yml exec web python manage.py createsuperuser
```

---

## 9) Backup & Restore (Production)

### 9.1 Admin DB Tools
- `/admin/db-tools/` provides:
  - JSON dump/load (fixtures)
  - Media ZIP download
  - Server backups stored in `/opt/bhrikutimandap/backups/`

### 9.2 VPS scheduled backups
See `tools/backup_prod.sh` and systemd timer files in `tools/`.

---

## 10) Recommended Next Improvement (Optional)

To reduce “red builds”, consider removing the `build-and-push` job if you are not using GHCR.
The production deploy already builds on the VPS.
