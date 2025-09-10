# 🌿 Git Sparse Checkout Guide
## For Clean Oracle Cloud Deployment

If you prefer to use Git directly on Oracle Cloud instead of uploading archives:

### 1. **Clone with Sparse Checkout:**
```bash
# Clone repository without downloading all files
git clone --filter=blob:none https://github.com/Christmas27/Network-Monitoring.git
cd Network-Monitoring

# Initialize sparse checkout
git sparse-checkout init --cone

# Set directories to include
git sparse-checkout set app_pages components utils modules config database docs deploy

# Checkout specific files manually
git checkout local-testing -- streamlit_app.py requirements.txt Dockerfile docker-compose.yml .dockerignore config.json .env.example README.md
```

### 2. **Verify Clean Structure:**
```bash
ls -la
# Should only show essential deployment files
```

### 3. **Deploy:**
```bash
docker-compose up -d
```

### 🎯 Benefits:
- ✅ Version controlled deployment
- ✅ Easy updates with `git pull`
- ✅ No manual file management
- ✅ Automatic exclusion of dev files

### ⚠️ Requirements:
- Git must be installed on Oracle Cloud VM
- Internet access for clone operation
- Sparse checkout knowledge for maintenance

---
**Use this method if you're comfortable with Git and want version-controlled deployment.**
