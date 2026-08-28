# Docker CI/CD AWS

A complete CI/CD pipeline for deploying a containerized Flask application to Amazon EC2 using Docker, Amazon ECR, GitHub Actions, AWS IAM OIDC, and AWS Systems Manager.

The project demonstrates an automated deployment workflow where every push to the `main` branch is tested, containerized, pushed to Amazon ECR, and deployed automatically to an EC2 instance.

## Architecture

```text
                         GitHub
                            │
                            │ git push
                            ▼
                    GitHub Actions
                            │
                     ┌──────┴──────┐
                     │             │
                  Pytest       Docker Build
                     │             │
                     └──────┬──────┘
                            │
                            ▼
                    Amazon ECR
                            │
                     Docker Image
                            │
                            ▼
                  AWS Systems Manager
                         (SSM)
                            │
                            ▼
                         EC2
                            │
                         Docker
                            │
                            ▼
                     Flask App
                         :5000
                            │
                         Port 80
                            │
                            ▼
                       Internet
```

## Project Overview

This project demonstrates how to build an automated CI/CD pipeline for a Dockerized Python application on AWS.

Instead of manually connecting to the EC2 instance and deploying every new version, GitHub Actions automatically performs the complete deployment process.

The pipeline performs the following steps:

1. Checkout the source code
2. Install Python dependencies
3. Run automated tests with Pytest
4. Build the Docker image
5. Authenticate to AWS using GitHub OIDC
6. Authenticate with Amazon ECR
7. Push the Docker image to ECR
8. Send a deployment command to EC2 using AWS Systems Manager
9. Pull the new Docker image on EC2
10. Stop and remove the previous container
11. Start the new container
12. Complete the deployment automatically

## Technologies

* **Python**
* **Flask**
* **Docker**
* **Amazon EC2**
* **Amazon ECR**
* **AWS Systems Manager (SSM)**
* **AWS IAM**
* **GitHub Actions**
* **GitHub OIDC**
* **Pytest**
* **AWS CLI**
* **Git & GitHub**

## AWS Region

The infrastructure is deployed in:

```text
eu-central-1
```

AWS Region:

```text
Frankfurt
```

## Application

The application is a simple Flask web service.

### Home Endpoint

```text
GET /
```

Response:

```text
Docker CI/CD AWS Pipeline V2 is working!
```

### Health Endpoint

```text
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

The health endpoint provides a simple way to verify that the application is running correctly after deployment.

## Application Structure

```text
docker-cicd-aws/
│
├── app/
│   └── app.py
│
├── .github/
│   └── workflows/
│       └── ci.yaml
│
├── Dockerfile
├── requirements.txt
├── test_app.py
├── .dockerignore
├── .gitignore
└── README.md
```

## Flask Application

The application runs on:

```text
0.0.0.0:5000
```

Example:

```python
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Docker CI/CD AWS Pipeline V2 is working!"


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

## Docker

The application is packaged into a Docker image.

Build locally:

```powershell
docker build -t docker-cicd-aws .
```

Run locally:

```powershell
docker run -d `
  --name docker-cicd-app `
  -p 5000:5000 `
  docker-cicd-aws
```

Test locally:

```powershell
curl.exe http://localhost:5000
```

Health check:

```powershell
curl.exe http://localhost:5000/health
```

## Automated Testing

The project uses Pytest.

Run tests locally:

```powershell
pytest
```

GitHub Actions executes the tests automatically before building and deploying the application.

If a test fails, the pipeline stops and the application is not deployed.

```text
Code
 ↓
Tests
 ↓
Docker Build
 ↓
ECR
 ↓
Deployment
```

## GitHub Actions CI/CD

The workflow is located at:

```text
.github/workflows/ci.yaml
```

The pipeline is triggered by pushes and pull requests targeting the `main` branch.

### Pipeline Stages

#### 1. Test

GitHub Actions:

* Checks out the repository
* Installs Python 3.12
* Installs dependencies
* Runs Pytest

```text
pytest
```

#### 2. Docker Build

After successful tests, the Docker image is built.

The image is tagged using the Git commit SHA:

```text
docker-cicd-aws:<GITHUB_SHA>
```

Using the commit SHA provides a unique and immutable version for each deployment.

#### 3. Push to Amazon ECR

GitHub Actions authenticates to AWS using GitHub OIDC:

```text
GitHub OIDC
     ↓
AWS IAM Role
     ↓
Amazon ECR
```

The image is pushed to the project's ECR repository.

Example format:

```text
<AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/docker-cicd-aws
```

## Immutable Image Tags

The ECR repository uses immutable image tags.

Instead of using:

```text
latest
```

the pipeline uses the Git commit SHA:

```text
<GITHUB_SHA>
```

For example:

```text
0562c8305d05e24b7afd2e7b0ddd805a3bea0f7c
```

This prevents an existing image tag from being overwritten and provides a unique version for every deployment.

## GitHub OIDC Authentication

GitHub Actions does not use long-term AWS access keys.

Instead, the workflow uses GitHub OpenID Connect (OIDC) to obtain temporary AWS credentials.

The AWS IAM OIDC provider is:

```text
token.actions.githubusercontent.com
```

The GitHub Actions workflow assumes an AWS IAM role.

The trust policy restricts access to the specific repository and `main` branch:

```text
repo:<GITHUB_USERNAME>/docker-cicd-aws:ref:refs/heads/main
```

This prevents unrelated repositories from assuming the deployment role.

## IAM Permissions

The GitHub Actions IAM role provides permissions required to:

* Authenticate with Amazon ECR
* Push Docker images to ECR
* Send deployment commands through AWS Systems Manager

The EC2 IAM role provides permissions required to:

* Pull images from Amazon ECR
* Communicate with AWS Systems Manager

No AWS access keys are stored inside the GitHub repository.

## AWS Systems Manager

The deployment process uses AWS Systems Manager instead of storing an SSH private key in GitHub.

The deployment flow is:

```text
GitHub Actions
      ↓
AWS IAM OIDC
      ↓
SSM SendCommand
      ↓
EC2
```

The EC2 instance receives and executes the deployment commands through SSM.

## EC2 Configuration

The application runs on:

```text
Amazon Linux 2023
```

Instance type:

```text
t3.micro
```

Docker runs the Flask application inside the EC2 instance.

Container port:

```text
5000
```

EC2 HTTP port:

```text
80
```

Port mapping:

```text
EC2 :80 → Container :5000
```

## ECR Repository

The Docker image is stored in an Amazon ECR repository:

```text
docker-cicd-aws
```

The registry URI follows this format:

```text
<AWS_ACCOUNT_ID>.dkr.ecr.eu-central-1.amazonaws.com/docker-cicd-aws
```

Actual AWS account and infrastructure identifiers are intentionally not included in this public documentation.

## Security Group

Inbound traffic is configured as follows:

| Protocol | Port | Source           | Purpose            |
| -------- | ---: | ---------------- | ------------------ |
| TCP      |   22 | Administrator IP | SSH administration |
| TCP      |   80 | 0.0.0.0/0        | HTTP application   |

SSH access should be restricted to trusted IP addresses.

The application is publicly accessible through HTTP.

## Deployment Process

During deployment, SSM executes commands to:

1. Authenticate Docker with Amazon ECR
2. Pull the new image
3. Stop the existing container
4. Remove the existing container
5. Start the new container

Conceptually:

```bash
aws ecr get-login-password --region eu-central-1
```

```bash
docker pull <ECR_IMAGE>:<GITHUB_SHA>
```

```bash
docker stop docker-cicd-app || true
```

```bash
docker rm docker-cicd-app || true
```

```bash
docker run -d \
  --name docker-cicd-app \
  -p 80:5000 \
  <ECR_IMAGE>:<GITHUB_SHA>
```

## Verification

After deployment, the application can be tested using the EC2 public IP:

```powershell
curl.exe http://<EC2_PUBLIC_IP>/
```

Expected response:

```text
Docker CI/CD AWS Pipeline V2 is working!
```

Health endpoint:

```powershell
curl.exe http://<EC2_PUBLIC_IP>/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## CI/CD Validation

The pipeline was tested by modifying the Flask application's response.

Initially, the application response was changed while the automated test still expected the previous response.

As a result, GitHub Actions correctly stopped the pipeline:

```text
pytest
 ↓
FAILED
 ↓
Build stopped
 ↓
Deployment stopped
```

After updating the test to match the new application response, the pipeline completed successfully:

```text
Tests              ✅
Docker Build       ✅
ECR Push            ✅
AWS OIDC            ✅
SSM Deployment     ✅
EC2 Deployment     ✅
Container Running  ✅
HTTP Response      ✅
```

This confirmed the complete CI/CD workflow from source-code change to EC2 deployment.

## Local Development

Clone the repository:

```powershell
git clone https://github.com/<GITHUB_USERNAME>/docker-cicd-aws.git
```

Navigate to the project:

```powershell
cd docker-cicd-aws
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Run tests:

```powershell
pytest
```

Run the Flask application:

```powershell
python app/app.py
```

Or run the application with Docker:

```powershell
docker build -t docker-cicd-aws .
```

```powershell
docker run -d `
  --name docker-cicd-app `
  -p 5000:5000 `
  docker-cicd-aws
```

## Deployment Workflow

For future changes:

```powershell
git add .
git commit -m "Update application"
git push
```

GitHub Actions automatically performs:

```text
Git Push
   ↓
Run Tests
   ↓
Build Docker Image
   ↓
Push Image to ECR
   ↓
Send SSM Command
   ↓
Pull Image on EC2
   ↓
Replace Container
   ↓
Application Updated
```

No manual SSH deployment is required.

## Security Considerations

This repository is intended for educational and portfolio purposes.

The following sensitive information should never be committed to GitHub:

```text
AWS Access Keys
AWS Secret Access Keys
AWS Session Tokens
SSH Private Keys
.pem files
.env files containing secrets
GitHub Personal Access Tokens
API Keys
Passwords
```

The project uses GitHub OIDC instead of storing long-term AWS credentials in GitHub.

Infrastructure-specific identifiers such as AWS Account IDs, EC2 Instance IDs, public IP addresses, and private infrastructure details are intentionally omitted from this public README.

## Project Highlights

This project demonstrates practical experience with:

* CI/CD automation
* GitHub Actions
* Docker containerization
* Amazon ECR
* Amazon EC2
* AWS Systems Manager
* AWS IAM
* GitHub OIDC
* Temporary AWS credentials
* Immutable container image versioning
* Automated testing
* Linux server administration
* AWS networking
* Container deployment
* Health checks
* Cloud troubleshooting
* Secure credential management

## Future Improvements

Possible improvements include:

* Add HTTPS with an Application Load Balancer
* Add a custom domain using Route 53
* Add CloudWatch monitoring
* Add automated rollback
* Add blue/green deployments
* Add Docker image vulnerability scanning
* Add automated deployment health checks
* Add ECS/Fargate deployment
* Add Terraform infrastructure provisioning
* Add GitHub Actions deployment environments
* Add staging and production environments
* Add Docker Compose for local development

## Repository

GitHub repository:

```text
https://github.com/<GITHUB_USERNAME>/docker-cicd-aws
```

## Author

**Alireza Fathihafshejani**

Master's Student in Software Engineering

Germany

## License

This project is intended for educational and portfolio purposes.

```
```
