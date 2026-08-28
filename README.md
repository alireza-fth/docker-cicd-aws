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

This project demonstrates how to build a production-style CI/CD workflow for a Dockerized Python application on AWS.

Instead of manually connecting to the EC2 instance and deploying every new version, GitHub Actions automatically performs the complete deployment process.

The pipeline performs the following steps:

1. Checkout the source code
2. Install Python dependencies
3. Run automated tests with Pytest
4. Build the Docker image
5. Authenticate with AWS using GitHub OIDC
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

The health endpoint can be used to verify that the application is running correctly after deployment.

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

The CI pipeline executes the same tests automatically before building and deploying the application.

If a test fails, the pipeline stops and the application is not deployed.

This provides a basic quality gate:

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

The pipeline is triggered by:

```yaml
on:
  push:
    branches:
      - main

  pull_request:
    branches:
      - main
```

### Pipeline Stages

#### 1. Test

GitHub Actions creates an Ubuntu runner and:

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

Using the commit SHA provides a unique and immutable image version.

#### 3. Push to Amazon ECR

GitHub Actions authenticates to AWS using:

```text
GitHub OIDC
        ↓
AWS IAM Role
        ↓
Amazon ECR
```

The image is then pushed to:

```text
675962431653.dkr.ecr.eu-central-1.amazonaws.com/docker-cicd-aws
```

### Immutable Image Tags

The ECR repository uses immutable image tags.

Instead of using:

```text
latest
```

the pipeline uses the Git commit SHA:

```text
0562c8305d05e24b7afd2e7b0ddd805a3bea0f7c
```

This prevents an existing image tag from being overwritten and provides a unique version for every deployment.

## AWS IAM OIDC

GitHub Actions does not use long-term AWS Access Keys.

Instead, the workflow uses GitHub's OpenID Connect integration.

The GitHub repository is trusted through an AWS IAM OIDC Identity Provider:

```text
token.actions.githubusercontent.com
```

The GitHub Actions workflow assumes:

```text
GitHubActionsDockerCICD
```

Role.

The trust policy restricts access to:

```text
repo:alireza-fth/docker-cicd-aws:ref:refs/heads/main
```

This means the AWS role is restricted to the specific repository and `main` branch.

## IAM Roles

### GitHub Actions Role

```text
GitHubActionsDockerCICD
```

The role provides permissions required to:

* Authenticate with Amazon ECR
* Push Docker images to ECR
* Send deployment commands through SSM

Policies include:

```text
GitHubActionsECRPush
GitHubActionsSSMDeploy
```

### EC2 Role

```text
DockerCICDEC2Role
```

The EC2 instance uses this IAM role instead of storing AWS Access Keys.

Attached AWS managed policies:

```text
AmazonEC2ContainerRegistryReadOnly
AmazonSSMManagedInstanceCore
```

This allows EC2 to:

* Pull Docker images from ECR
* Communicate with AWS Systems Manager

## AWS Systems Manager

The deployment process uses AWS Systems Manager instead of storing an SSH private key in GitHub.

GitHub Actions sends an SSM command to the EC2 instance:

```text
GitHub Actions
      ↓
AWS IAM OIDC
      ↓
SSM SendCommand
      ↓
EC2
```

The EC2 instance then executes the deployment commands.

## Deployment Process

During deployment, SSM executes commands similar to:

```bash
aws ecr get-login-password --region eu-central-1 | \
sudo docker login \
--username AWS \
--password-stdin \
675962431653.dkr.ecr.eu-central-1.amazonaws.com
```

Pull the new image:

```bash
sudo docker pull \
675962431653.dkr.ecr.eu-central-1.amazonaws.com/docker-cicd-aws:<GITHUB_SHA>
```

Stop the previous container:

```bash
sudo docker stop docker-cicd-app || true
```

Remove the previous container:

```bash
sudo docker rm docker-cicd-app || true
```

Start the new container:

```bash
sudo docker run -d \
  --name docker-cicd-app \
  -p 80:5000 \
  675962431653.dkr.ecr.eu-central-1.amazonaws.com/docker-cicd-aws:<GITHUB_SHA>
```

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

## Security Group

Inbound traffic:

| Protocol | Port | Source    | Purpose            |
| -------- | ---: | --------- | ------------------ |
| TCP      |   22 | My IP     | SSH administration |
| TCP      |   80 | 0.0.0.0/0 | HTTP application   |

SSH access is restricted to the administrator's IP address.

The application is publicly accessible through HTTP.

## Verification

After deployment, the application can be tested from the local machine.

Home endpoint:

```powershell
curl.exe http://<EC2_PUBLIC_IP>/
```

Example response:

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

The first test intentionally failed because the application response changed while the test still expected the previous value.

GitHub Actions correctly stopped the pipeline:

```text
pytest
 ↓
FAILED
 ↓
Build skipped
 ↓
Deployment skipped
```

After updating the test to match the new application version, the pipeline completed successfully:

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

This confirmed that the CI/CD pipeline works from source-code change through production deployment.

## Local Development

Clone the repository:

```powershell
git clone https://github.com/alireza-fth/docker-cicd-aws.git
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

For future changes, the deployment process is simply:

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
* Infrastructure security
* Cloud troubleshooting

## Future Improvements

Possible improvements include:

* Add HTTPS with an Application Load Balancer
* Add domain name and Route 53
* Add Amazon CloudWatch monitoring
* Add automated rollback
* Add blue/green deployments
* Add Docker image vulnerability scanning
* Add deployment health checks
* Add ECS/Fargate deployment
* Add Terraform infrastructure provisioning
* Add GitHub Actions deployment environments
* Add staging and production environments
* Add Docker Compose for local development

## Repository

GitHub:

```text
https://github.com/alireza-fth/docker-cicd-aws
```

## Author

**Alireza Fathihafshejani**

Master's Student in Software Engineering

Germany

## License

This project is intended for educational and portfolio purposes.

```
```
