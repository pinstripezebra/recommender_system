# Docker Hub CI/CD Setup

This repository includes GitHub Actions workflows that automatically build and push Docker images to Docker Hub when you commit to the main branch.

## Setup Instructions

### 1. Docker Hub Account Setup
- Make sure you have a Docker Hub account
- Your Docker Hub username should be: `seelucas`
- Your repository will be: `seelucas/fastapi_tutorial`

### 2. GitHub Secrets Configuration
You need to add the following secrets to your GitHub repository:

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** and add:

**Required Secrets:**
- **Name:** `DOCKER_USERNAME`
  - **Value:** `seelucas` (your Docker Hub username)
  
- **Name:** `DOCKER_PASSWORD`
  - **Value:** Your Docker Hub password or access token (recommended)

### 3. Docker Hub Access Token (Recommended)
Instead of using your password, create an access token:

1. Log in to Docker Hub
2. Go to **Account Settings** → **Security**
3. Click **New Access Token**
4. Give it a name (e.g., "GitHub Actions")
5. Copy the token and use it as your `DOCKER_PASSWORD` secret

### 4. Workflow Files
Two workflow files have been created:

#### `simple-docker-build.yml` (Recommended)
- Runs your exact commands
- Builds and pushes on every commit to main
- Simple and straightforward

#### `docker-build-push.yml` (Advanced)
- More features like multi-platform builds
- Better caching
- Metadata extraction
- Runs on both pushes and pull requests

### 5. How it Works
When you commit to the main branch:

1. GitHub Actions automatically triggers
2. Checks out your code
3. Logs in to Docker Hub using your secrets
4. Runs these commands:
   ```bash
   docker build -t recommendersystem .
   docker tag recommendersystem seelucas/fastapi_tutorial:fastapi_on_render
   docker push seelucas/fastapi_tutorial:fastapi_on_render
   ```

### 6. Monitoring
- Check the **Actions** tab in your GitHub repository to see build status
- Each commit will show a green checkmark ✅ if successful
- Click on any workflow run to see detailed logs

### 7. Usage
After setup, simply:
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

The Docker image will be automatically built and pushed to Docker Hub!

## Troubleshooting

### Common Issues:
1. **Authentication Failed**: Check your Docker Hub credentials in GitHub secrets
2. **Repository Not Found**: Ensure the Docker Hub repository exists or will be created
3. **Build Failed**: Check the Actions tab for detailed error logs

### Verification:
- Check Docker Hub at: https://hub.docker.com/r/seelucas/fastapi_tutorial
- Your image should appear with the tag `fastapi_on_render`
