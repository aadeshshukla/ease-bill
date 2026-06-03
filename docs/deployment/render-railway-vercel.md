# EaseBill cloud deployment (Render/Railway + Vercel)

## 1) Backend on Render (recommended free tier path)

1. Create a **PostgreSQL** instance in Render.
2. Create a new **Web Service** from this repository, root directory: `backend`.
3. Set build/start commands:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `backend/.env.production.example`.

Required values:

- `DATABASE_URL` = Render PostgreSQL Internal Database URL
- `CORS_ORIGINS` = your Vercel frontend URL (for example `https://ease-bill.vercel.app`)
- `SECRET_KEY` = long random string

Verify after deploy:

```bash
curl https://<your-render-backend>/health
curl https://<your-render-backend>/docs
```

## 2) Backend on Railway (alternative)

```bash
# Requires Railway CLI and logged-in account
npm i -g @railway/cli
railway login
railway init
railway add -d postgres
railway up
```

Then set variables in Railway service settings using `backend/.env.production.example`.

## 3) Frontend on Vercel

1. Import this repository in Vercel.
2. Set **Root Directory** to `frontend`.
3. Add env var:
   - `VITE_API_BASE_URL=https://<your-backend-domain>`
4. Deploy.

## 4) Auto deploy from GitHub main branch

Add repository secrets:

- `VERCEL_DEPLOY_HOOK_URL` (Vercel project deploy hook)
- `RENDER_DEPLOY_HOOK_URL` (Render service deploy hook, optional if using Render)

Workflow: `.github/workflows/cloud-deploy.yml`

On every push to `main`, deploy hooks are triggered automatically.
