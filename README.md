# AWS Telegram Bot Infrastructure (DevOps Lab)

This project demonstrates a production-ready CI/CD pipeline for deploying Telegram bots to AWS using Infrastructure as Code (IaC). It features a secure, passwordless deployment process and a split-server architecture for high availability.

## 🏗 Architecture

- **Cloud Provider:** AWS (EC2, RDS, VPC, IAM).
- **IaC:** Terraform (Infrastructure provisioning).
- **Configuration Management:** Ansible (Server configuration & App deployment).
- **CI/CD:** GitHub Actions (OIDC authentication, Dynamic Inventory).
- **Containerization:** Docker (Isolated bot environments).
- **Database:** PostgreSQL (RDS) for user data and state persistence.

## 🚀 Key Features

- **Security First:** Uses OpenID Connect (OIDC) for AWS authentication — no long-lived access keys stored in GitHub Secrets.
- **Dynamic Inventory:** Ansible hosts are discovered automatically via AWS Tags, eliminating hardcoded IPs.
- **Zero-Downtime Deployment:** Docker containers are rebuilt and replaced on the fly.
- **Network Hardening:** SSH ports are opened strictly for the GitHub Runner IP only during deployment.

## 📂 Repository Structure
```
├── .github/workflows/ # CI/CD pipelines (Deploy, Audit)
├── ansible/           # Playbooks for server provisioning
├── terraform/         # IaC definitions (EC2, SG, RDS, IAM)
├── motivator/         # Source code for the Motivation Bot
└── memer/             # Source code for the Meme Bot
```

## 🛠 Usage
1. Infrastructure: Run Terraform to provision AWS resources.
```
cd terraform
terraform init && terraform apply
```
2. Deployment: Push changes to the `main` branch. GitHub Actions will automatically:
- Authenticate via OIDC.
- Whitelist the runner's IP.
- Run Ansible playbooks to update the bots.

## 📝 Future Improvements
- Implement monitoring with Prometheus/Grafana.
- Add unit tests for bot logic.