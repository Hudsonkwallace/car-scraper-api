# Deployment Guide

This guide covers deploying your car scraper API to cloud platforms so n8n can access it from anywhere.

## 🎯 Recommended Deployment Options

### Option 1: Railway (Easiest - Free Tier Available) ⭐

**Best for:** Quick deployment, no Docker knowledge needed

1. **Prepare your code:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Push to GitHub:**
   - Create a new repository on GitHub
   - Push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/car-scraper-api.git
   git push -u origin main
   ```

3. **Deploy to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python and deploy

4. **Configure (if needed):**
   - Railway usually auto-detects settings
   - If not, set:
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Get your URL:**
   - Railway provides a URL like: `https://your-app.railway.app`
   - Use this in n8n: `https://your-app.railway.app/scrape`

**Cost:** Free tier includes 500 hours/month (enough for development)

---

### Option 2: Render (Free Tier, More Control)

**Best for:** Long-running services, persistent deployments

1. **Push to GitHub** (same as Railway above)

2. **Deploy to Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Configure:
     - **Name:** car-scraper-api
     - **Environment:** Python 3
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
     - **Plan:** Free

3. **Wait for deployment** (5-10 minutes)

4. **Get your URL:**
   - Render provides: `https://car-scraper-api.onrender.com`
   - Use in n8n: `https://car-scraper-api.onrender.com/scrape`

**Notes:**
- Free tier spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Good for periodic n8n workflows

**Cost:** Completely free

---

### Option 3: Docker + Cloud Platform

**Best for:** Full control, production deployments

#### Build and Test Locally:

1. **Install Docker Desktop** (if not installed)
   - Download from [docker.com](https://www.docker.com/products/docker-desktop)

2. **Build the Docker image:**
   ```bash
   docker build -t car-scraper-api .
   ```

3. **Run locally:**
   ```bash
   docker run -p 8000:8000 car-scraper-api
   ```

4. **Test:**
   ```bash
   curl http://localhost:8000/scrape
   ```

#### Deploy with Docker Compose:

```bash
docker-compose up -d
```

#### Deploy to Cloud with Docker:

**A. Fly.io** (Recommended for Docker)

1. Install Fly CLI:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. Create `fly.toml`:
   ```toml
   app = "car-scraper-api"

   [build]
     dockerfile = "Dockerfile"

   [[services]]
     http_checks = []
     internal_port = 8000
     processes = ["app"]
     protocol = "tcp"

     [[services.ports]]
       port = 80
       handlers = ["http"]

     [[services.ports]]
       port = 443
       handlers = ["tls", "http"]
   ```

3. Deploy:
   ```bash
   fly launch
   fly deploy
   ```

4. Get URL:
   ```bash
   fly status
   ```

**B. Google Cloud Run**

1. Install gcloud CLI
2. Build and push:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/car-scraper-api
   ```
3. Deploy:
   ```bash
   gcloud run deploy car-scraper-api \
     --image gcr.io/YOUR_PROJECT_ID/car-scraper-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

---

### Option 4: DigitalOcean App Platform

**Best for:** Scalable production apps

1. **Push to GitHub**

2. **Create App:**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - "Create App" → Connect GitHub repo
   - Select Dockerfile deployment
   - Choose $5/month plan (or free trial)

3. **Configure:**
   - Port: 8000
   - HTTP Routes: /

4. **Deploy and get URL**

---

## 🔧 Environment Variables

If you need to configure the API, set these environment variables in your deployment platform:

- `PORT` - The port to run on (usually set by platform)
- `LOG_LEVEL` - Set to `INFO` or `DEBUG`

---

## 🧪 Testing Your Deployment

Once deployed, test with:

```bash
# Basic health check
curl https://your-app-url.com/health

# Test scraping
curl "https://your-app-url.com/scrape?url=https://www.usautosofdallas.com/"
```

---

## 🔗 Integrating with n8n

1. In your n8n workflow, add an **HTTP Request** node

2. Configure:
   - **Method:** GET
   - **URL:** `https://your-deployed-url.com/scrape`
   - **Query Parameters:**
     - Name: `url`, Value: `https://www.usautosofdallas.com/`
     - Name: `llm_format`, Value: `true`

3. Add a **Code** or **AI** node to process the response

4. Example workflow:
   ```
   [Schedule Trigger]
   → [HTTP Request: Scrape Cars]
   → [Claude AI: Analyze Inventory]
   → [Send Email with Report]
   ```

---

## 📊 Monitoring

### Railway
- Built-in logs and metrics dashboard
- View at: Project → Deployments → Logs

### Render
- Logs tab shows all output
- Metrics show request counts

### Docker Logs
```bash
docker logs -f container_name
```

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid (Basic) | Best For |
|----------|-----------|--------------|----------|
| **Railway** | 500 hrs/month | $5/month | Quick start |
| **Render** | Unlimited (spins down) | $7/month | Development |
| **Fly.io** | 3 VMs free | $1.94/month | Docker apps |
| **DigitalOcean** | Trial credits | $5/month | Production |
| **Google Cloud Run** | 2M requests/month | Pay per use | High scale |

---

## 🚀 Quick Start (Recommended Path)

For getting started quickly with n8n:

1. **Use Railway** (easiest):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   # Push to GitHub
   # Deploy via Railway dashboard
   ```

2. **Get your URL** from Railway

3. **Use in n8n:**
   - URL: `https://your-app.railway.app/scrape`
   - The API will be always available (free tier)

---

## 🔒 Security Considerations

1. **Rate Limiting:** Consider adding rate limiting for production
2. **Authentication:** Add API key authentication if needed
3. **CORS:** Already configured for all origins (restrict in production)
4. **Secrets:** Never commit API keys or secrets

---

## ⚠️ Troubleshooting

### Chrome Not Found in Docker
- The Dockerfile includes Chrome installation
- If issues persist, check Chrome version compatibility

### Slow Scraping
- First request may be slow (Chrome initialization)
- Consider keeping the service "warm" with periodic pings

### Memory Issues
- Selenium uses ~500MB RAM
- Ensure your deployment has at least 512MB RAM

### Timeout Errors
- Increase timeout in n8n HTTP Request node
- Set to 60-90 seconds for scraping operations

---

## 📚 Next Steps

After deployment:

1. ✅ Test the `/scrape` endpoint
2. ✅ Configure n8n workflow
3. ✅ Set up monitoring/alerts
4. ✅ Consider adding authentication
5. ✅ Implement caching for repeated scrapes

Need help? Check the [README.md](README.md) for API documentation.
