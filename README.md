# Morelli Scan Bot

Telegram bot for intelligent door handle selection using AI-powered image analysis.

## Important: Development Workflow

**🚨 ALL DEVELOPMENT MUST BE DONE ON THE SERVER 🚨**

This project is deployed and runs on Beget server. Local folder contains only documentation.

## Quick Start

### Connect to Server
```bash
ssh -i ~/.ssh/beget_key root@212.8.226.218
```

Or use alias:
```bash
ssh beget
```

### Navigate to Project
```bash
cd /root/morelli-bot
```

### Activate Virtual Environment
```bash
source venv/bin/activate
```

## Documentation

- **SSH Connection Guide**: `SSH_CONNECTION.md`
- **Project Memory**: `PROJECT_MEMORY.md`

## Bot Status

Check bot status:
```bash
ssh beget 'systemctl status morelli-bot'
```

View logs:
```bash
ssh beget 'journalctl -u morelli-bot -f'
```

## SSH Authentication

### SSH Key Location
- **Public Key**: `beget_key.pub` (stored in project root)
- **Private Key**: `~/.ssh/beget_key` (on local machine)

The public key is saved locally in the project folder for reference and backup purposes.

## Server Details
- **IP**: 212.8.226.218
- **User**: root
- **Project Path**: /root/morelli-bot/
- **Service**: morelli-bot.service
