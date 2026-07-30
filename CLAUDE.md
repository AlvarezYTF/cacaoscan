# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Screenshots

Cuando el usuario mencione una captura de pantalla (sin dar ruta), búscala en `C:\Users\jefer\OneDrive\Pictures\Screenshots` — toma la más reciente por defecto.

## Project Overview

CacaoScan is a full-stack platform that measures dimensions and weight of cacao beans using computer vision and ML. It pairs a Django REST API (PyTorch + YOLOv8 + scikit-learn) with a Vue 3 SPA. The backend serves the API and admin; the frontend is the user-facing UI.

## Common Commands

### Top-level (Docker / Make)
- `make up` / `docker compose up -d --build` — full stack (backend, frontend, postgres, redis)
- `make down`, `make logs`, `make clean` (clean removes volumes — destroys DB)
- `make test` — runs backend pytest + frontend vitest
- `make deploy` / `make k8s-status` / `make k8s-logs` — Kubernetes via `k8s/`
- AWS deploy: push a `main` dispara CI/CD automático (ver `Doc/AWS_DEPLOYMENT.md`); infra en `infra/terraform/`
- `bash scripts/sync_models_from_s3.sh` — descarga modelos ML desde S3 al entorno local
- `bash scripts/upload_model_to_s3.sh` — sube modelos entrenados a S3

### Backend (`cd backend`, requires Python 3.12 exactly)
- Create venv: `py -3.12 -m venv venv && venv\Scripts\activate` (Windows) or `source venv/bin/activate`
- Install: `pip install -r requirements.txt`
- Run: `python manage.py runserver` → http://127.0.0.1:8000
- Migrations: `python manage.py makemigrations && python manage.py migrate`
- Seeders (required after fresh DB): `python manage.py init_catalogos` then `python manage.py seed_colombia`
- Tests: `pytest` (config in `backend/pytest.ini`, uses `--reuse-db --nomigrations`)
- Single test: `pytest api/tests/test_foo.py::TestClass::test_method`
- Parallel: `pytest -n auto` (pytest-xdist installed)
- Coverage: `pytest --cov`
- Inside Docker: `docker compose exec backend python manage.py <cmd>`

### Frontend (`cd frontend`, requires Node `^20.19.0 || >=22.12.0`, prefer pnpm)
- Install: `pnpm install`
- Dev: `pnpm dev` → http://127.0.0.1:5173
- Build / preview: `pnpm build` / `pnpm preview`
- Tests: `pnpm test` (vitest watch), `pnpm test:unit` (single run + coverage)
- Lint / format: `pnpm lint`, `pnpm format`

### ML Pipeline (run inside backend container, in order)
1. `python manage.py train_unet_background --epochs 20 --batch-size 16` — produces `ml/segmentation/cacao_unet.pth`
2. `python manage.py calibrate_dataset_pixels --segmentation-backend auto` — produces crops + `media/datasets/pixel_calibration.json`
3. `python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50 --batch-size 32` — produces `ml/artifacts/regressors/hybrid.pt`

GPU is auto-detected; lower batch sizes (4–8) when on CPU. Source data goes in `backend/media/cacao_images/raw/` and `backend/media/datasets/`.

## Architecture

### Backend layout (`backend/`)
Django project is `cacaoscan/` (settings, urls, asgi/wsgi). Apps are mounted under `/api/v1/` from `cacaoscan/urls.py`:
- `api/` — primary REST surface; contains `views/`, `serializers/`, `services/`, `tasks/`, plus realtime infra (`consumers.py`, `routing.py`, `realtime_service.py`, `realtime_middleware.py`, `cache_config.py`). Most cross-cutting endpoints live here.
- `auth_app/` — JWT auth (SimpleJWT) and login endpoints.
- `personas/` — user/agricultor/técnico profiles. Mounted *before* `api.urls` to avoid prefix conflicts.
- `fincas_app/` — fincas (farms) and lotes (lots).
- `images_app/` — image upload/storage and dataset ingestion (S3-capable via django-storages).
- `catalogos/` — reference data (countries, regions, cacao varieties); seeded by management commands.
- `reports/` — Excel/PDF report generation (openpyxl, XlsxWriter, reportlab).
- `notifications/`, `audit/` — notification delivery and audit log.
- `legal/` — terms and privacy endpoints.
- `training/` — ML training orchestration (management commands and services for the pipeline above).
- `ml/` — model code organized by stage: `segmentation/`, `classification/`, `regression/`, `prediction/`, `measurement/`, `pipeline/`, plus `artifacts/` for trained weights.
- `core/`, `users/` — shared models and primitives.

URL loading is defensive: each app's URLconf is wrapped in try/except so a broken app doesn't take down the whole API. When adding routes, follow the *specific-before-general* ordering already in `cacaoscan/urls.py`.

Realtime: `channels` + `channels_redis` provide WebSockets via `api/routing.py` and `api/consumers.py`. Async tasks use Celery (worker + beat services in `docker-compose.yml`); broker/cache is Redis. Celery only starts in containers when `USE_CELERY_REDIS` is enabled and `CELERY_BROKER_URL` is set (see `docker-entrypoint.sh`).

Settings (`cacaoscan/settings.py`) auto-generates a dev `.env` if missing (only when `APP_ENV != production`) and force-sanitizes `.env` bytes (BOM/latin-1) before loading. Production requires `.env` to exist or it raises. `env.example` is the reference.

### Frontend layout (`frontend/src/`)
Standard Vue 3 SPA: `views/` (route pages), `components/` (reusable), `stores/` (Pinia), `router/`, `services/` (axios API clients), `composables/`, `utils/`, `assets/`, `styles/`. Tailwind v4 via `@tailwindcss/vite`. API base URL comes from `VITE_API_BASE_URL`. Tests live in `__tests__/` and `src/test/` and run under vitest + jsdom.

### Deployment
- `docker-compose.yml` (root) wires backend, frontend (nginx), db (postgres 15), redis, celery worker, celery beat.
- `render.yaml` + `RENDER_ENVIRONMENT_VARIABLES.md` define Render deployment; `Doc/` has guides for AWS S3 and CSRF troubleshooting.
- `k8s/` contains Kustomize manifests; namespace defaults to `app-namespace` (override with `K8S_NS=...`).
- Sonar config in `sonar-project.properties`; `run_sonar_full.bat` runs full analysis.

## Repo-Specific Gotchas

- **Python 3.12 only.** 3.11 and 3.13 break (the settings file even shims `SecurityWarning` for 3.12).
- **`pytest.ini` ignores many test files** that currently fail due to schema/factory drift. Don't assume an `--ignore`d test is supposed to pass; check before "fixing" by un-ignoring.
- **Comment hygiene (from global CLAUDE.md):** when editing any file, audit existing comments — delete obvious/stale ones, fix wrong ones. Keep comments sparse, accurate, and useful.
- **Two `docker-compose.yml` files** exist (root and `backend/`). The root one is the source of truth for full-stack dev; the backend-local one is for backend-only workflows.
- **URL prefixes:** all v1 routes go under `/api/v1/`. `personas/` is mounted before `api/` deliberately — preserve that order when adding apps.
- **Spanish-language project.** Code identifiers, commit messages, docs, and user-facing strings are in Spanish. Match this when writing new code or docs.

## Estilo de Respuesta (Cavernícola) — regla dura

- Responde en español salvo que el usuario escriba en otro idioma.
- Sin preámbulos. Sin despedidas. Sin frases de relleno.
- Nunca narres lo que vas a hacer: acción primero.
- Explica solo si se te pregunta.
- **Brevedad dura**: el mínimo de palabras posible. Por defecto 1–3 líneas; máximo ~6 salvo que el usuario pida detalle. Nada de resúmenes de lo hecho, listas de archivos tocados ni recuentos de cambios: solo el resultado.
- No repitas lo que ya se ve en el diff o en el output de las herramientas.
- Si la respuesta es un dato o un "listo", di eso y nada más.
- **Al grano, siempre**: primero el hallazgo o la conclusión; el sustento solo si se pide. Nada de recorridos por el código, tablas de opciones ni diagramas ASCII salvo petición explícita.
- **Ninguna skill ni slash command anula esta brevedad.** Si un modo (`explore`, `brainstorming`, `plan`, etc.) invita a extenderse, ignóralo: esta regla gana. Explorar = investigar a fondo y **reportar corto**.
- Máximo **una** pregunta por turno, y solo si el trabajo no puede seguir sin ella.

## Proposal vs cambio directo (regla dura)

- Por defecto, **aplica los cambios directamente**, sin generar proposal/spec y sin preguntar.
- Genera proposal (OpenSpec o similar) **solo** cuando el cambio es pesado: toca varios módulos/flujos, rediseña arquitectura o esquema, o el alcance es demasiado grande/denso para un solo pase.
- **Nunca preguntes** "¿genero proposal o aplico directo?": decide con este criterio y ejecuta.

## Cierre de tarea: commit + push SIEMPRE

Al terminar una tarea de código —verificada y sin nada pendiente— **haz commit y push sin preguntar**. No es un extra opcional ni requiere confirmación: es parte de terminar.

- Commitea en la rama de trabajo y pushea a `origin`.
- Verifica **antes** de commitear (tests/typecheck/lint/build según el proyecto). Si algo falla o queda a medias, **no** commitees: arregla o reporta.
- Mensaje honesto sobre lo que entra. Nunca `--no-verify` ni saltarse hooks.

### Solo lo tuyo: el trabajo ajeno no se toca (regla dura)

Puede haber otras sesiones de Claude trabajando en paralelo en el mismo árbol. Todo lo que no escribiste **en esta sesión** es ajeno.

- **Commitea solo los archivos que tú tocaste en esta sesión**, con `git add <ruta>` explícito por archivo. Nunca `git add -A`, `git add .`, ni `git commit -a`.
- Si encuentras cambios ajenos en el árbol o ya staged: **déjalos como están**. No los commitees, no los descartes, no los reformatees, no los "arregles". No hagas `git reset`, `git stash`, `git checkout --`, ni `git restore` sobre ellos.
- Si tu archivo trae además cambios ajenos entremezclados, commitea el archivo completo y **dilo en el mensaje** — no inventes una separación falsa, pero tampoco te apropies de lo ajeno.
- Antes de commitear, compara `git status` contra tu propia lista de archivos editados. Lo que no esté en tu lista no entra.
