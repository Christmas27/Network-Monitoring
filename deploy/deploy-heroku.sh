#!/bin/bash
# Heroku Deployment Script

echo "🚀 Deploying Network Dashboard to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first."
    echo "Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "Please log in to Heroku first:"
    heroku login
fi

# App name (change this to your desired app name)
APP_NAME="network-dashboard-$(whoami)"

echo "Creating Heroku app: $APP_NAME"

# Create Heroku app
heroku create $APP_NAME --region us

# Set environment variables
echo "Setting environment variables..."
heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set SECRET_KEY=$(openssl rand -base64 32) --app $APP_NAME
heroku config:set PORT=5000 --app $APP_NAME

# Set stack to container (for Docker deployment)
heroku stack:set container --app $APP_NAME

# Deploy
echo "Deploying application..."
git add .
git commit -m "Deploy to Heroku" || echo "No changes to commit"
git push heroku main

# Open the app
echo "✅ Deployment complete!"
echo "Opening your app..."
heroku open --app $APP_NAME

echo "🔍 To view logs: heroku logs --tail --app $APP_NAME"
echo "⚙️  To manage app: https://dashboard.heroku.com/apps/$APP_NAME"
