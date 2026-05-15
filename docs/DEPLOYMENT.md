# Streamlit Cloud Deployment Guide

This guide provides step-by-step instructions for deploying the RAG Document Assistant to Streamlit Cloud.

## Prerequisites

- GitHub account
- Streamlit Cloud account (free at https://share.streamlit.io/)
- Groq API key or OpenAI API key

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)

```bash
cd RAG
git init
git add .
git commit -m "Initial commit: RAG Document Assistant"
```

### 1.2 Create .gitignore

Create a `.gitignore` file in your project root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment variables
.env

# Data directories
data/pdf_cache/*
!data/pdf_cache/.gitkeep
data/vector_store/*
!data/vector_store/.gitkeep

# Logs
logs/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### 1.3 Create .gitkeep files for empty directories

```bash
touch data/pdf_cache/.gitkeep
touch data/vector_store/.gitkeep
touch logs/.gitkeep
```

### 1.4 Commit and push to GitHub

```bash
git add .
git commit -m "Add gitignore and gitkeep files"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 2: Configure Streamlit Cloud

### 2.1 Create Streamlit Cloud Account

1. Go to https://share.streamlit.io/
2. Click "Sign up" or "Sign in with GitHub"
3. Authorize Streamlit to access your GitHub account

### 2.2 Create New App

1. Click "New app" button
2. Select your repository from the dropdown
3. Select the main branch
4. Set the main file path to `app.py`
5. Click "Deploy"

## Step 3: Configure Environment Variables

### 3.1 Add Environment Variables

1. After deployment, click on your app
2. Go to "Settings" → "Secrets"
3. Add the following secrets:

```
GROQ_API_KEY=your_actual_groq_api_key
# OR
OPENAI_API_KEY=your_actual_openai_api_key

LLM_PROVIDER=groq
LLM_MODEL=llama3-70b-8192
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### 3.2 Save and Redeploy

1. Click "Save"
2. The app will automatically redeploy with the new environment variables

## Step 4: Verify Deployment

### 4.1 Check App Status

- Go to your app dashboard
- Wait for the deployment to complete (usually 1-2 minutes)
- Check the logs for any errors

### 4.2 Test the Application

1. Open your app URL
2. Enter your API key in the sidebar
3. Upload a test PDF
4. Ask a question to verify functionality

## Step 5: Advanced Configuration

### 5.1 Custom Domain (Optional)

Streamlit Cloud allows custom domains for paid plans:

1. Go to "Settings" → "Custom domain"
2. Add your domain
3. Configure DNS settings as instructed

### 5.2 Resource Limits

Free tier limits:
- 30 days of app uptime per month
- 1GB RAM
- Shared CPU

Paid tier options:
- More uptime
- More RAM
- Dedicated CPU
- Custom domains

### 5.3 Monitoring

View app metrics:
- Go to your app dashboard
- Check "Usage" tab for:
  - CPU usage
  - Memory usage
  - Number of visitors
  - Response times

## Troubleshooting

### Common Issues

#### 1. Deployment Fails

**Problem**: App fails to deploy

**Solutions**:
- Check GitHub repository is public
- Verify `app.py` exists in the root
- Check requirements.txt is valid
- Review deployment logs for specific errors

#### 2. API Key Not Working

**Problem**: API key errors in the app

**Solutions**:
- Verify API key is correct
- Check environment variable name matches exactly
- Ensure API key has necessary permissions
- Try regenerating the API key

#### 3. PDF Upload Fails

**Problem**: Cannot upload PDF files

**Solutions**:
- Check file size limits (Streamlit: 200MB default)
- Verify PDF is not corrupted
- Check browser console for errors
- Ensure sufficient disk space

#### 4. Slow Performance

**Problem**: App is slow to respond

**Solutions**:
- Reduce chunk size for faster processing
- Use smaller embedding model
- Enable persistent vector store
- Consider upgrading to paid tier for more resources

#### 5. Memory Errors

**Problem**: Out of memory errors

**Solutions**:
- Process fewer documents at once
- Use smaller chunk sizes
- Clear conversation history regularly
- Upgrade to paid tier for more RAM

## Alternative Deployment Options

### Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t rag-assistant .
docker run -p 8501:8501 -e GROQ_API_KEY=your_key rag-assistant
```

### AWS/Azure/GCP Deployment

#### AWS EC2

1. Launch EC2 instance
2. Install Docker
3. Deploy using Docker
4. Configure security groups for port 8501

#### Azure Container Instances

1. Create Azure Container Registry
2. Push Docker image
3. Deploy to Azure Container Instances

#### Google Cloud Run

1. Containerize application
2. Push to Google Container Registry
3. Deploy to Cloud Run

## Security Best Practices

1. **Never commit API keys** to Git
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** in production
4. **Implement rate limiting** for API calls
5. **Regularly rotate** API keys
6. **Monitor logs** for suspicious activity
7. **Keep dependencies** updated

## Performance Optimization

### 1. Caching

- Enable persistent vector store
- Cache processed documents
- Use Redis for session caching

### 2. Load Balancing

- Use multiple app instances
- Configure load balancer
- Implement horizontal scaling

### 3. Database Optimization

- Use PostgreSQL for metadata
- Implement connection pooling
- Add database indexes

## Cost Estimation

### Streamlit Cloud Free Tier

- **Cost**: $0/month
- **Limitations**: 30 days uptime, 1GB RAM
- **Suitable for**: Development, small projects

### Streamlit Cloud Pro

- **Cost**: ~$20/month
- **Benefits**: Unlimited uptime, more RAM, custom domains
- **Suitable for**: Production applications

### Self-Hosted (AWS/Azure/GCP)

- **Cost**: Varies by provider and usage
- **Typical**: $20-100/month for small deployment
- **Suitable for**: Large-scale applications, full control

## Maintenance

### Regular Tasks

1. **Monitor logs** for errors
2. **Update dependencies** regularly
3. **Backup vector indexes**
4. **Rotate API keys** periodically
5. **Review usage metrics**
6. **Test functionality** after updates

### Backup Strategy

```bash
# Backup vector store
tar -czf vector_backup.tar.gz data/vector_store/

# Backup to cloud storage
aws s3 cp vector_backup.tar.gz s3://your-bucket/backups/
```

## Support

- Streamlit Cloud Documentation: https://docs.streamlit.io/streamlit-cloud
- GitHub Issues: Report issues in your repository
- Community Forum: https://discuss.streamlit.io/

---

For additional help, refer to the main README.md or open an issue on GitHub.
