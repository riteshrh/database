# 🚀 GradToHired Database Automation - Deployment Guide

This guide covers multiple deployment options for your Streamlit application, from the easiest (Streamlit Cloud) to more advanced options (AWS, Docker).

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Environment Variables**: A `.env` file with all required credentials
2. **GitHub Repository**: Your code pushed to a GitHub repository
3. **API Keys**: Valid OpenAI and Snowflake credentials

## 🌐 Option 1: Streamlit Cloud (Recommended - Easiest)

**Best for**: Quick deployment, no server management, free hosting

### Steps:
1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `main_app.py`
   - Click "Deploy"

3. **Set Environment Variables**:
   - In your Streamlit Cloud dashboard
   - Go to "Settings" → "Secrets"
   - Add your `.env` file contents

**✅ Pros**: Free, automatic deployments, no server management
**❌ Cons**: Limited customization, potential cold starts

---

## 🦸 Option 2: Heroku

**Best for**: Production use, easy scaling, good free tier

### Prerequisites:
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login
```

### Steps:
1. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**:
   ```bash
   heroku config:set OPENAI_API_KEY="your_key"
   heroku config:set SNOWFLAKE_USER="your_user"
   # ... set all other variables
   ```

3. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

4. **Open App**:
   ```bash
   heroku open
   ```

**✅ Pros**: Good free tier, easy scaling, production-ready
**❌ Cons**: Free tier limitations, requires credit card

---

## 🐳 Option 3: Docker (Local/Any Cloud)

**Best for**: Consistent environments, any cloud platform, full control

### Local Testing:
```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8501
```

### Deploy to Any Cloud:
1. **Build Image**:
   ```bash
   docker build -t gradtohired-app .
   ```

2. **Push to Registry**:
   ```bash
   # For Docker Hub
   docker tag gradtohired-app yourusername/gradtohired-app
   docker push yourusername/gradtohired-app
   
   # For AWS ECR, GCP Container Registry, etc.
   # Follow platform-specific instructions
   ```

3. **Deploy on Platform**:
   - **AWS ECS**: Use the ECS console or CLI
   - **GCP Cloud Run**: Use the Cloud Run console
   - **Azure Container Instances**: Use Azure CLI

**✅ Pros**: Portable, consistent, works anywhere
**❌ Cons**: More complex setup, requires Docker knowledge

---

## ☁️ Option 4: AWS (Advanced)

**Best for**: Enterprise use, full control, high scalability

### AWS App Runner (Easiest):
1. **Push to GitHub**
2. **Connect to AWS App Runner**
3. **Deploy automatically**

### AWS ECS (More Control):
1. **Create ECS Cluster**
2. **Define Task Definition**
3. **Deploy Service**

### AWS Lambda + API Gateway:
1. **Convert to API endpoints**
2. **Deploy as serverless functions**

**✅ Pros**: Highly scalable, enterprise features, full control
**❌ Cons**: Complex setup, requires AWS knowledge, costs

---

## 🔧 Environment Variables

All deployment methods require these environment variables:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Snowflake Database Configuration
SNOWFLAKE_USER=your_snowflake_username
SNOWFLAKE_PASSWORD=your_snowflake_password
SNOWFLAKE_ACCOUNT=your_snowflake_account_identifier
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=userprofiles
SNOWFLAKE_SCHEMA=public

# Optional: Heroku App Name
HEROKU_APP_NAME=your-app-name
```

## 🚀 Quick Deployment Script

Use the included `deploy.sh` script for automated deployment:

```bash
# Make executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## 📊 Deployment Comparison

| Platform | Difficulty | Cost | Scalability | Maintenance |
|----------|------------|------|-------------|-------------|
| Streamlit Cloud | ⭐ | Free | Low | None |
| Heroku | ⭐⭐ | Low | Medium | Low |
| Docker | ⭐⭐⭐ | Medium | High | Medium |
| AWS | ⭐⭐⭐⭐ | High | Very High | High |

## 🎯 Recommendation

- **Start with**: Streamlit Cloud (easiest, free)
- **Scale to**: Heroku (good balance)
- **Enterprise**: Docker + Cloud Platform (full control)

## 🆘 Troubleshooting

### Common Issues:
1. **Environment Variables**: Ensure all required variables are set
2. **Port Configuration**: Check if port 8501 is available
3. **Dependencies**: Verify all packages are in requirements.txt
4. **Database Access**: Ensure Snowflake allows external connections

### Getting Help:
- Check the deployment logs
- Verify environment variables
- Test locally first
- Check platform-specific documentation

---

**Happy Deploying! 🚀✨** 