# Render Deployment Guide for Network Monitoring Dashboard

## Prerequisites
1. GitHub account with your project repository
2. Render account (free signup at https://render.com)

## Deployment Steps

### 1. Prepare Your Repository
Make sure your project has these files:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Tells Render how to run your app
- ✅ `.env` - Environment variables (optional for local testing)

### 2. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 3. Create Render Web Service

1. **Sign in to Render**: Go to https://render.com and sign in/up
2. **Connect GitHub**: Connect your GitHub account
3. **Create New Web Service**: 
   - Click "New +" → "Web Service"
   - Select your GitHub repository: `Network-Monitoring`
   - Click "Connect"

### 4. Configure Deployment Settings

Fill in these settings on Render:
- **Name**: `network-monitoring-dashboard` (or your preferred name)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - main:app`

### 5. Set Environment Variables

In the Render dashboard, go to "Environment" and add:
- `SECRET_KEY`: Generate a secure random key
- `FLASK_DEBUG`: `False`
- `FLASK_HOST`: `0.0.0.0`
- `DATABASE_PATH`: `data/network_dashboard.db`

Optional (for DevNet integration):
- `CATALYST_CENTER_HOST`: Your Catalyst Center host
- `CATALYST_CENTER_USERNAME`: Your username
- `CATALYST_CENTER_PASSWORD`: Your password

### 6. Deploy

Click "Create Web Service" and wait for deployment to complete.

## Expected Results

✅ Your app will be available at: `https://your-service-name.onrender.com`
✅ Automatic deployments on every push to main branch
✅ Free SSL certificate included
✅ Auto-scaling based on traffic

## Troubleshooting

### Common Issues:
1. **Build fails**: Check requirements.txt for incompatible versions
2. **App crashes**: Check logs in Render dashboard
3. **Database issues**: Render's free tier has ephemeral storage

### View Logs:
- Go to your service in Render dashboard
- Click "Logs" tab to see real-time application logs

## Portfolio Enhancement Tips

Add these to your resume/portfolio:
- 🎯 **Cloud Deployment**: "Deployed full-stack network monitoring application to cloud platform"
- 🚀 **DevOps**: "Implemented CI/CD pipeline with automatic deployments"
- 🔧 **Production Ready**: "Configured production environment with gunicorn WSGI server"
- 🌐 **Network Automation**: "Integrated with Cisco DevNet APIs for real device management"

## Next Steps

Consider upgrading to paid Render plan for:
- Persistent storage
- Custom domains
- Better performance
- Background workers

## Demo URL
Once deployed, your live demo will be at:
`https://your-service-name.onrender.com`

Add this URL to your resume and LinkedIn profile!
