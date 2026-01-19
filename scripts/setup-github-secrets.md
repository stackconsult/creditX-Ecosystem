# GitHub Secrets Setup Guide

> **When Hyperlift team responds**, follow these steps to configure GitHub secrets.

## Prerequisites

- [ ] Hyperlift dashboard access confirmed
- [ ] Managed PostgreSQL provisioned (get `DATABASE_URL`)
- [ ] Managed Dragonfly provisioned (get `CACHE_HOST`)

## Step 1: Generate JWT Secret

Run this command locally:

```bash
openssl rand -base64 32
```

Save the output - you'll need it below.

## Step 2: Navigate to GitHub Secrets

1. Go to: https://github.com/stackconsult/creditX-Ecosystem/settings/secrets/actions
2. Click **"New repository secret"** for each secret below

## Step 3: Add Required Secrets

| Secret Name | Value Source | Example Format |
|-------------|--------------|----------------|
| `OPENAI_API_KEY` | `.env` line 147 | `sk-proj-...` |
| `COPILOTKIT_API_KEY` | `.env` line 148 | `ck_pub_...` |
| `NEXT_PUBLIC_COPILOTKIT_API_KEY` | `.env` line 148 (same) | `ck_pub_...` |
| `DATABASE_URL` | From Spaceship | `postgresql://user:pass@host:5432/db` |
| `CACHE_HOST` | From Spaceship | `dragonfly-xxxx.internal` |
| `CACHE_PORT` | Standard | `6379` |
| `JWT_SECRET` | Generated above | `aBcD1234...` (32+ chars) |

## Step 4: Trigger Deployment

After all secrets are set:

```bash
# Option A: Push any change to main
git commit --allow-empty -m "chore: trigger deployment"
git push origin main

# Option B: Manual workflow trigger (if configured)
# Go to Actions tab → Select workflow → Run workflow
```

## Step 5: Verify Deployment

Run the verification script:

```bash
./scripts/verify-deployment.sh https://creditx.credit
```

## Troubleshooting

### Build fails with missing env var
- Check all 7 secrets are set in GitHub
- Verify secret names match exactly (case-sensitive)

### Health check fails
- Check Hyperlift logs in dashboard
- Verify DATABASE_URL is accessible
- Verify CACHE_HOST is accessible

### 500 errors on API
- Check JWT_SECRET is set
- Verify OPENAI_API_KEY is valid

## Checklist

- [ ] `OPENAI_API_KEY` added
- [ ] `COPILOTKIT_API_KEY` added
- [ ] `NEXT_PUBLIC_COPILOTKIT_API_KEY` added
- [ ] `DATABASE_URL` added (from Spaceship)
- [ ] `CACHE_HOST` added (from Spaceship)
- [ ] `CACHE_PORT` added (`6379`)
- [ ] `JWT_SECRET` added (generated)
- [ ] Push triggered
- [ ] Deployment verified at https://creditx.credit

---

*Created: January 19, 2026*
