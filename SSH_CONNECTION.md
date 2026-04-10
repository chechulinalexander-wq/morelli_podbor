# SSH Connection to Beget Server

## Server Details
- **IP Address**: 212.8.226.218
- **User**: root
- **Authentication**: SSH Key (passwordless)
- **Password** (for emergency): 1gnGQwHE&zcq

## SSH Connection Command
```bash
ssh -i ~/.ssh/beget_key root@212.8.226.218
```

Or use the configured host alias:
```bash
ssh beget
```

## Project Location on Server
```
/root/morelli-bot/
```

## Important: Development Workflow

**ALL DEVELOPMENT MUST BE DONE DIRECTLY ON THE SERVER!**

### Working on the Server
1. Connect to server via SSH
2. Navigate to project directory:
   ```bash
   cd /root/morelli-bot
   ```
3. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Make your changes directly on the server
5. Test changes
6. Restart the bot service if needed:
   ```bash
   systemctl restart morelli-bot
   ```

## Bot Management Commands

### Check bot status
```bash
systemctl status morelli-bot
```

### View bot logs (live)
```bash
journalctl -u morelli-bot -f
```

### View last 50 log lines
```bash
journalctl -u morelli-bot -n 50
```

### Restart bot
```bash
systemctl restart morelli-bot
```

### Stop bot
```bash
systemctl stop morelli-bot
```

### Start bot
```bash
systemctl start morelli-bot
```

### Enable bot to start on system boot
```bash
systemctl enable morelli-bot
```

## Files on Server
```
/root/morelli-bot/
├── bot.py                      # Main bot script
├── generate_embeddings.py      # Embedding generation script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (BOT_TOKEN)
├── handles.db                  # SQLite database
├── products_complete.json      # Product data
├── venv/                       # Python virtual environment
└── data/                       # Data directory
```

## Environment Variables
The `.env` file contains:
```
BOT_TOKEN=8372353929:AAGmSDUrdxJpnB3qpIrQr_aBlLmnZMBvots
```

## Python Dependencies
All dependencies are installed in the virtual environment (`venv/`):
- torch >= 2.0.0
- transformers >= 4.30.0
- Pillow >= 10.0.0
- requests >= 2.31.0
- numpy >= 1.24.0
- python-telegram-bot >= 20.0
- python-dotenv >= 1.0.0

## Service Configuration
The bot runs as a systemd service located at:
```
/etc/systemd/system/morelli-bot.service
```

Service configuration:
- **Type**: Simple
- **Auto-restart**: Yes (on failure)
- **Restart delay**: 10 seconds
- **User**: root
- **Working Directory**: /root/morelli-bot

## Notes
- The local `dev/` folder now contains only documentation
- All project files have been moved to `dev/OLD/` for archival
- Use SSH to access and modify files on the server
- Changes made on the server are immediately effective
- Remember to restart the service after code changes
