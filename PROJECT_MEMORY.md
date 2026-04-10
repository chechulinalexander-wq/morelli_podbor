# Morelli Scan Bot - Project Memory

## Project Overview
Telegram bot for Morelli door handle selection using image embeddings and AI-powered recommendations.

## Current Status
- **Environment**: Production on Beget server
- **Status**: Deployed and running
- **Bot Token**: 8372353929:AAGmSDUrdxJpnB3qpIrQr_aBlLmnZMBvots
- **Server IP**: 212.8.226.218

## Architecture

### Tech Stack
- **Language**: Python 3.12.3
- **Bot Framework**: python-telegram-bot >= 20.0
- **ML/AI**:
  - PyTorch >= 2.0.0
  - Transformers >= 4.30.0
- **Image Processing**: Pillow >= 10.0.0
- **Data**:
  - SQLite database (handles.db)
  - JSON product catalog (products_complete.json)

### Project Structure
```
/root/morelli-bot/
├── bot.py                      # Main bot logic
├── generate_embeddings.py      # Embedding generation for products
├── requirements.txt            # Dependencies
├── .env                        # Environment configuration
├── handles.db                  # Handle database
├── products_complete.json      # Complete product catalog
└── venv/                       # Virtual environment
```

## Bot Functionality

### Current Features
1. **Start Command** (`/start`)
   - Welcomes users
   - Explains bot capabilities
   - Provides usage instructions

2. **Photo Handler**
   - Receives door photos
   - Sends acknowledgment message
   - TODO: Add image analysis and recommendation logic

3. **Text Handler**
   - Handles non-command text messages
   - Prompts user to send a photo

### Planned Features
- Image analysis using computer vision
- Product recommendation based on:
  - Door color
  - Door style
  - Design preferences
- Handle similarity matching using embeddings
- Product details with links to website

## Development History

### 2025-11-09: Initial Deployment
- Created basic bot structure
- Set up environment variables (.env)
- Deployed to Beget server
- Configured systemd service
- Bot running in production

### Key Decisions
1. **Server-side Development**: All development happens directly on Beget server
2. **Environment Variables**: Sensitive data in .env file
3. **Systemd Service**: Auto-restart on failure, runs on boot
4. **Python Virtual Environment**: Isolated dependencies

## Database Schema

### handles.db (SQLite)
- Contains door handle product information
- Fields: TBD (needs inspection)

### products_complete.json
- Complete product catalog in JSON format
- Used for embeddings and recommendations

## API Keys & Credentials
- **Telegram Bot Token**: Stored in .env
- **Server Access**: SSH key authentication

## Deployment Process
1. Connect to server via SSH
2. Navigate to `/root/morelli-bot/`
3. Activate venv: `source venv/bin/activate`
4. Make changes to code
5. Test changes
6. Restart service: `systemctl restart morelli-bot`
7. Check logs: `journalctl -u morelli-bot -f`

## Known Issues
- None currently

## TODO / Roadmap
1. Implement image analysis
   - Upload and process door photos
   - Extract color, style, design features

2. Build recommendation engine
   - Generate embeddings for products
   - Similarity matching algorithm
   - Ranking and filtering

3. Product display
   - Format product information
   - Include images
   - Add website links

4. Database optimization
   - Index frequently queried fields
   - Optimize embedding storage

5. Testing
   - Unit tests for core functions
   - Integration tests for bot handlers
   - Performance testing

## Notes
- Development is done exclusively on the server
- Local `dev/` folder contains only documentation
- Old development files archived in `dev/OLD/`
- Bot automatically restarts on failure (10 sec delay)

## Resources
- Telegram Bot API: https://core.telegram.org/bots/api
- python-telegram-bot docs: https://docs.python-telegram-bot.org/
- PyTorch docs: https://pytorch.org/docs/
- Transformers docs: https://huggingface.co/docs/transformers/
