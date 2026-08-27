# Production Deployment Guide

This guide covers deploying **CRYPTO_ALPHA_SNIPER** on a Linux Virtual Private Server (VPS) for 24/7 autonomous monitoring.

---

## 🖥️ Server Provisioning Guidelines

* **Recommended Cloud Providers**: DigitalOcean, Hetzner, AWS EC2, Linode, Vultr.
* **OS**: Ubuntu 22.04 LTS or Debian 12.
* **Specs**: 1 vCPU, 1 GB - 2 GB RAM, 20 GB SSD.

---

## 🚀 Method 1: Systemd Service Deployment (Native Python)

Running via Systemd ensures automatic restart on crashes and server reboots.

### 1. Create System User and Directory
```bash
sudo useradd -r -s /bin/false sniper
sudo mkdir -p /opt/crypto_alpha_sniper
sudo chown -R sniper:sniper /opt/crypto_alpha_sniper
```

### 2. Clone Code & Install Virtualenv
```bash
sudo git clone https://github.com/nuexn0x-9/CRYPTO_ALPHA_SNIPER.git /opt/crypto_alpha_sniper
cd /opt/crypto_alpha_sniper

sudo python3 -m venv .venv
sudo /opt/crypto_alpha_sniper/.venv/bin/pip install --upgrade pip
sudo /opt/crypto_alpha_sniper/.venv/bin/pip install -r requirements.txt

sudo cp .env.example .env
# Edit .env with your credentials:
sudo nano .env

sudo chown -R sniper:sniper /opt/crypto_alpha_sniper
```

### 3. Create Systemd Service File
Create `/etc/systemd/system/crypto-alpha-sniper.service`:

```ini
[Unit]
Description=CRYPTO_ALPHA_SNIPER Intelligence Scanner
After=network.target

[Service]
Type=simple
User=sniper
Group=sniper
WorkingDirectory=/opt/crypto_alpha_sniper
ExecStart=/opt/crypto_alpha_sniper/.venv/bin/python -m src.main
Restart=always
RestartSec=10
EnvironmentFile=/opt/crypto_alpha_sniper/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable crypto-alpha-sniper
sudo systemctl start crypto-alpha-sniper
```

### 5. Monitor Service Status & Logs
```bash
# Check status
sudo systemctl status crypto-alpha-sniper

# View live stream logs
sudo journalctl -u crypto-alpha-sniper -f
```

---

## 🐳 Method 2: Docker Compose Deployment

Refer to the complete [Docker Guide](docker-guide.md) for running via Docker Compose in detached mode with persistent volume mounting.

---

## 🔒 Server Hardening & Security Best Practices

1. **Firewall (UFW)**: The scanner only makes outbound HTTPS queries; no inbound ports need to be opened except SSH (Port 22).
   ```bash
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```
2. **File Permissions**: Ensure `.env` and database files have restrictive permissions (`chmod 600 .env`).
3. **Database Backups**: Set up a daily cron job to back up `data/crypto_alpha_sniper.db` to a secure off-site location.
