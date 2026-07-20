# BusinessPilotAI: Deployment & Build Guide

This document details the configuration and deployment procedures for **BusinessPilotAI** across different environments: Local Development, Docker Containerization, Streamlit Community Cloud, and Production Virtual Private Servers (VPS).

---

## 1. Local Development Environment Setup

### Prerequisites
- **Python**: Version 3.9, 3.10, or 3.11.
- **SQLite3**: Pre-installed on Windows/macOS.

### Step-by-Step Installation
1. **Navigate to the Project Directory**:
   ```bash
   cd C:\Users\risha\.gemini\antigravity\scratch\business_pilot_ai
   ```
2. **Initialize a Virtual Environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate the Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\activate
     ```
   - **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```
4. **Install Required Packages**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Execute SQLite Seeding**:
   ```bash
   python database/seed_data.py
   ```
6. **Launch Streamlit Web Server**:
   ```bash
   streamlit run frontend/app.py
   ```
   Open your browser to `http://localhost:8501`.

---

## 2. Docker Containerization (Local & Cloud)

### Build the Image
To build the Docker image locally, run the following command from the project root:
```bash
docker build -t business_pilot_ai:latest .
```

### Launch via Docker Run
To run the container, exposing the default port `8501` and mounting volumes for database and reports persistence:
```bash
docker run -d -p 8501:8501 \
  -v "$(pwd)/database:/app/database" \
  -v "$(pwd)/reports:/app/reports" \
  -v "$(pwd)/datasets:/app/datasets" \
  --name business_pilot_ai_app \
  business_pilot_ai:latest
```

### Launch via Docker Compose
To run using Docker Compose (which mounts the volumes and binds the host port automatically):
```bash
# Build and run containers in detached mode
docker-compose up --build -d
```
Stop the container stack with:
```bash
docker-compose down
```

---

## 3. Deployment to Streamlit Community Cloud

Streamlit Community Cloud provides a free hosting environment directly connected to your GitHub repository.

### Steps to Deploy
1. **Prepare the Repository**: Push your code to a public GitHub repository. Ensure `.streamlit/config.toml` and `requirements.txt` are at the correct paths.
2. **Log In to Streamlit**: Go to [share.streamlit.io](https://share.streamlit.io/) and log in using your GitHub account.
3. **Configure the App**:
   - **Repository**: Select `business_pilot_ai`.
   - **Branch**: Select `main` (or active development branch).
   - **Main file path**: Set to `frontend/app.py`.
4. **Define Secrets**: In the Streamlit app settings menu, configure the environment secrets in TOML format:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
5. **Deploy**: Click **Deploy**. Streamlit will automatically build the container, install packages, and launch the web server.

---

## 4. Production Deployment on VPS (AWS / GCP / DigitalOcean)

For a production setup with custom domain names and SSL encryption, deploy on a Linux VPS behind an Nginx reverse proxy.

### A. Setup Host Directories & Code
Clone the repository onto the server:
```bash
git clone https://github.com/your-org/business_pilot_ai.git /var/www/business_pilot_ai
cd /var/www/business_pilot_ai
```

### B. Systemd Daemon Service Setup
Create a systemd configuration file to keep Streamlit running in the background:
```bash
sudo nano /etc/systemd/system/business_pilot.service
```

Add the following configuration:
```ini
[Unit]
Description=BusinessPilotAI Streamlit Web Daemon
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/business_pilot_ai
ExecStart=/var/www/business_pilot_ai/venv/bin/streamlit run frontend/app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
Environment=OPENAI_API_KEY=sk-...

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable business_pilot.service
sudo systemctl start business_pilot.service
```

Check the service status:
```bash
sudo systemctl status business_pilot.service
```

### C. Nginx Reverse Proxy Setup
Install Nginx and configure it to reverse proxy requests from port 80 to Streamlit on port 8501:
```bash
sudo apt update
sudo apt install nginx -y
sudo nano /etc/nginx/sites-available/business_pilot
```

Add the following server block:
```nginx
server {
    listen 80;
    server_name businesspilot.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the configuration and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/business_pilot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### D. SSL Configuration via Certbot (Let's Encrypt)
Secure your domain with SSL:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d businesspilot.yourdomain.com
```
Certbot will obtain the SSL certificate and automatically update the Nginx configuration to redirect all HTTP traffic to HTTPS.
