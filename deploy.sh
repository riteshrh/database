#!/bin/bash

echo "🚀 GradToHired Database Automation - Deployment Script"
echo "======================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your configuration first."
    exit 1
fi

# Load environment variables
source .env

echo "✅ Environment variables loaded"
echo ""

# Function to deploy to Streamlit Cloud
deploy_streamlit_cloud() {
    echo "🌐 Deploying to Streamlit Cloud..."
    echo "1. Push your code to GitHub"
    echo "2. Go to https://share.streamlit.io"
    echo "3. Connect your GitHub repository"
    echo "4. Deploy automatically"
    echo ""
    echo "Your app will be available at: https://your-app-name.streamlit.app"
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "🦸 Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install it first:"
        echo "   https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Create Heroku app if it doesn't exist
    if [ -z "$HEROKU_APP_NAME" ]; then
        echo "Please set HEROKU_APP_NAME in your .env file"
        exit 1
    fi
    
    # Set environment variables on Heroku
    heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY"
    heroku config:set SNOWFLAKE_USER="$SNOWFLAKE_USER"
    heroku config:set SNOWFLAKE_PASSWORD="$SNOWFLAKE_PASSWORD"
    heroku config:set SNOWFLAKE_ACCOUNT="$SNOWFLAKE_ACCOUNT"
    heroku config:set SNOWFLAKE_WAREHOUSE="$SNOWFLAKE_WAREHOUSE"
    heroku config:set SNOWFLAKE_DATABASE="$SNOWFLAKE_DATABASE"
    heroku config:set SNOWFLAKE_SCHEMA="$SNOWFLAKE_SCHEMA"
    
    # Deploy
    git add .
    git commit -m "Deploy to Heroku"
    git push heroku main
    
    echo "✅ Deployed to Heroku!"
    echo "Your app is available at: https://$HEROKU_APP_NAME.herokuapp.com"
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Deploying with Docker..."
    
    # Build and run with docker-compose
    docker-compose up --build -d
    
    echo "✅ Deployed with Docker!"
    echo "Your app is available at: http://localhost:8501"
}

# Function to deploy to AWS
deploy_aws() {
    echo "☁️ Deploying to AWS..."
    echo "This requires AWS CLI and additional setup."
    echo "Consider using AWS App Runner or ECS for easy deployment."
    echo ""
    echo "For AWS App Runner:"
    echo "1. Push to GitHub"
    echo "2. Connect to AWS App Runner"
    echo "3. Deploy automatically"
}

# Main deployment menu
echo "Choose deployment option:"
echo "1. Streamlit Cloud (Recommended - Easiest)"
echo "2. Heroku"
echo "3. Docker (Local/Any Cloud)"
echo "4. AWS"
echo "5. Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_streamlit_cloud
        ;;
    2)
        deploy_heroku
        ;;
    3)
        deploy_docker
        ;;
    4)
        deploy_aws
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please try again."
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment completed!"
echo "Check the output above for your app's URL." 