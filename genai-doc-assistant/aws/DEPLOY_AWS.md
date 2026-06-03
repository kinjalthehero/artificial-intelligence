# Deploy GenAI Document Assistant on AWS EC2

A step-by-step guide to deploying on AWS. Each step explains the AWS concept so you learn while you deploy.

## Prerequisites

- AWS account ([Create free tier account](https://aws.amazon.com/free/))
- Your `GOOGLE_API_KEY` from Google AI Studio or Google Cloud Console

## Cost

- **EC2 t3.micro**: FREE for 12 months (750 hours/month)
- **Storage (8 GB)**: FREE for 12 months
- **Data transfer**: FREE (100 GB/month outbound)
- **After 12 months**: ~$8-10/month. **Set a reminder to terminate before June 2027.**

---

## Step 1: Create an AWS Account

1. Go to https://aws.amazon.com/free/
2. Sign up with your email
3. Add a payment method (required but won't be charged for free tier)
4. Select the "Basic Support - Free" plan

**What you're learning:** AWS requires a payment method even for free tier as a fraud prevention measure. You won't be charged as long as you stay within free tier limits.

---

## Step 2: Set Up a Budget Alert

Do this FIRST to protect against unexpected charges.

1. Go to **AWS Console** > search **"Budgets"** > **Create a budget**
2. Choose **"Monthly cost budget"**
3. Budget amount: **$1**
4. Alert threshold: **80%** ($0.80)
5. Add your email for notifications

**What you're learning:** AWS Budgets monitors your spending and sends email alerts. It doesn't auto-stop services, but it warns you early. A $1 budget catches any accidental charges immediately.

---

## Step 3: Launch an EC2 Instance

**What is EC2?** Elastic Compute Cloud — virtual servers in the cloud. You're renting a computer from Amazon that runs 24/7 in their data center.

1. Go to **AWS Console** > search **"EC2"** > click **"Launch Instance"**

2. **Name**: `genai-doc-assistant`

3. **AMI (Amazon Machine Image)**: Select **Amazon Linux 2023** (free tier eligible)
   - *What is an AMI?* A pre-configured OS image — like a Docker image but for entire virtual machines.

4. **Instance type**: Select **t3.micro** (free tier eligible)
   - 1 vCPU, 1 GB RAM — sufficient for our Docker container
   - *What is an instance type?* The hardware spec of your virtual server. `t3.micro` is the smallest free option.

5. **Key pair**: Click **"Create new key pair"**
   - Name: `genai-doc-assistant-key`
   - Type: RSA
   - Format: `.pem`
   - Download and save it somewhere safe (e.g., `~/.ssh/`)
   - *What is a key pair?* SSH uses public/private key cryptography. AWS keeps the public key; you keep the private `.pem` file to prove your identity when connecting.

6. **Network settings**: Click **"Edit"** and configure the Security Group:
   - Security group name: `genai-doc-assistant-sg`
   - **Rule 1**: Type: SSH, Port: 22, Source: My IP
   - **Rule 2**: Type: HTTP, Port: 80, Source: Anywhere (0.0.0.0/0)
   - *What is a Security Group?* A virtual firewall. It controls which traffic can reach your instance. We allow SSH (for you to manage it) and HTTP (for users to access the app).

7. **Storage**: 8 GB gp3 (default, free tier eligible)

8. Click **"Launch Instance"**

9. Wait ~1 minute for the instance to start. Note the **Public IPv4 address** from the instance details.

---

## Step 4: Connect via SSH

**What is SSH?** Secure Shell — a protocol for securely connecting to remote computers over the internet. Like remote desktop, but command-line only.

```bash
# First, set correct permissions on your key file
chmod 400 ~/.ssh/genai-doc-assistant-key.pem

# Connect to your instance (replace with your public IP)
ssh -i ~/.ssh/genai-doc-assistant-key.pem ec2-user@<YOUR_PUBLIC_IP>
```

If using Amazon Linux, the username is `ec2-user`. For Ubuntu, use `ubuntu`.

You should see a terminal prompt on your EC2 instance.

---

## Step 5: Install Docker and Deploy

**What is Docker on EC2?** The same Docker you use locally. The container runs identically whether it's on your MacBook or on an AWS server — that's the whole point of containers.

Run the automated setup script:

```bash
# Download and run the setup script
curl -O https://raw.githubusercontent.com/kinjalthehero/artificial-intelligence/main/genai-doc-assistant/aws/setup-ec2.sh
bash setup-ec2.sh
```

This installs Docker, clones the repo, and prepares the environment.

After it completes:

```bash
# 1. Add your API key
cd artificial-intelligence/genai-doc-assistant
nano .env
# Add: GOOGLE_API_KEY=your-key-here
# Save: Ctrl+X, Y, Enter

# 2. Log out and back in (needed for Docker group permissions)
exit
ssh -i ~/.ssh/genai-doc-assistant-key.pem ec2-user@<YOUR_PUBLIC_IP>

# 3. Start the application
cd artificial-intelligence/genai-doc-assistant
docker compose up -d --build

# 4. Watch the build (takes ~3-5 minutes first time)
docker compose logs -f

# 5. Check it's running
docker compose ps
```

---

## Step 6: Access Your App

Open a browser and go to:

```
http://<YOUR_EC2_PUBLIC_IP>
```

You should see the GenAI Document Assistant UI. Upload a document and try asking a question.

**Tip:** Bookmark this URL. The IP won't change unless you stop/start (not reboot) the instance.

---

## Step 7: Updating the App

When you push new code to GitHub:

```bash
ssh -i ~/.ssh/genai-doc-assistant-key.pem ec2-user@<YOUR_PUBLIC_IP>
cd artificial-intelligence/genai-doc-assistant
bash aws/update.sh
```

---

## Cancel Before You're Charged

**AWS free tier expires 12 months after account creation (~June 2027).**

To avoid charges after the free tier ends:

1. Go to **EC2 Console** > **Instances**
2. Select your instance > **Instance state** > **Terminate instance**
3. This permanently deletes the instance and stops all charges

To just pause (stop billing but keep data):
- **Stop instance** (no compute charges, small storage charge)
- **Start instance** when you need it again (IP will change)

---

## What You've Learned

| AWS Concept | What It Is |
|-------------|-----------|
| **EC2** | Virtual servers in the cloud |
| **AMI** | Pre-configured OS image for VMs |
| **Instance Type** | Hardware spec (CPU, RAM) |
| **Key Pair** | SSH authentication (public/private keys) |
| **Security Group** | Virtual firewall (inbound/outbound rules) |
| **SSH** | Secure remote terminal access |
| **Budgets** | Spending alerts and monitoring |

## What to Learn Next

| Topic | What It Does | When You Need It |
|-------|-------------|-----------------|
| **Elastic IP** | Fixed public IP that persists across stop/start | When you want a permanent URL |
| **Route 53** | AWS DNS service — map a domain name to your IP | When you want `myapp.com` instead of an IP |
| **ALB (Application Load Balancer)** | Distributes traffic across multiple instances | When you need high availability |
| **Auto Scaling Group** | Automatically adds/removes instances based on traffic | When traffic is unpredictable |
| **RDS** | Managed database (PostgreSQL, MySQL) | When SQLite isn't enough |
| **S3** | Object storage for files | When you need durable file storage |
| **ECR** | Docker image registry | When you want to store Docker images on AWS |
| **ECS/Fargate** | Managed container service (no servers) | When you want serverless containers |
| **EKS (Kubernetes)** | Managed Kubernetes | When you have many microservices (costs $72+/month for the control plane — overkill for a single app) |

## When Does Kubernetes Make Sense?

Kubernetes (K8s) is designed for orchestrating **many containers across many servers**. It's powerful but complex and expensive on AWS (EKS: $72+/month just for the control plane).

**Use Kubernetes when:**
- You have 5+ microservices that need to communicate
- You need auto-scaling, self-healing, and rolling deployments
- Your team has dedicated DevOps engineers
- Your budget supports $100+/month infrastructure

**Don't use Kubernetes when:**
- You have a single application (like this project)
- You're on a budget under $50/month
- Docker Compose on a single server handles your traffic
- You're learning and want to keep things simple

For this project, **Docker Compose on EC2** is the right choice. It's production-ready for the traffic level we expect, costs $0 for a year, and teaches you the foundational AWS concepts that Kubernetes builds on.
