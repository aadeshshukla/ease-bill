# EaseBill

EaseBill converts bank statement PDFs to Tally-compatible XML.

## Live testing links

Update these values after your first deployment:

- Frontend: `https://ease-bill.vercel.app`
- API docs: `https://ease-bill-api.onrender.com/docs`
- Health check: `https://ease-bill-api.onrender.com/health`

## Production deployment setup

- Frontend deployment config: `frontend/vercel.json`
- Backend production env template: `backend/.env.production.example`
- Deployment guide: `docs/deployment/render-railway-vercel.md`
- Auto deploy workflow: `.github/workflows/cloud-deploy.yml`

## Local run (docker compose)

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

## Health check

```bash
curl http://localhost:8000/health
```
