# Morelli Bot - Technology Stack

## Overview
This document describes all technologies, libraries, and tools used in the Morelli Telegram bot project.

---

## Infrastructure

### Hosting
- **Provider**: Beget
- **Server IP**: 212.8.226.218
- **OS**: Linux (Ubuntu/Debian based)
- **Access**: SSH with public key authentication
- **SSH Key**: `~/.ssh/beget_key`
- **User**: root

### Runtime Environment
- **Python Version**: 3.12.3
- **Virtual Environment**: venv (located at `/root/morelli-bot/venv/`)
- **Process Manager**: systemd
- **Service Name**: morelli-bot.service

### File Structure
```
/root/morelli-bot/
├── bot.py                      # Main application
├── generate_embeddings.py      # ML preprocessing
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── handles.db                  # SQLite database
├── products_complete.json      # Product catalog
└── venv/                       # Virtual environment
```

---

## Core Technologies

### Bot Framework
**python-telegram-bot >= 20.0**
- Modern async/await API
- Built-in handlers for commands, messages, photos
- Webhook and long-polling support
- Used for: All Telegram interactions

### Database
**SQLite 3.x**
- File-based database (handles.db)
- Built into Python standard library
- No server required
- Used for: Product catalog storage, embeddings

---

## Machine Learning & AI

### Deep Learning Framework
**PyTorch >= 2.0.0**
- GPU/CPU support
- Model inference for embeddings
- Used for: Running pre-trained vision models

### NLP & Vision Models
**transformers >= 4.30.0** (Hugging Face)
- Pre-trained models (CLIP, ViT, BERT)
- Easy model loading and inference
- Used for: Image-to-text/embedding conversion

### Computer Vision
**Pillow >= 10.0.0** (PIL Fork)
- Image loading and preprocessing
- Color extraction
- Image resizing and format conversion
- Used for: Photo processing before ML inference

### Numerical Computing
**NumPy**
- Array operations
- Vector calculations
- Used for: Embedding manipulation, similarity calculations

**scikit-learn**
- Cosine similarity
- Normalization functions
- Used for: Product matching algorithm

---

## Development Tools

### Version Control
**Git**
- Documentation repo (local folder)
- Server code managed manually
- Future: Proper version control on server

### Code Editor
**Cursor / VS Code**
- Local development environment
- SSH remote editing (when needed)

### SSH Client
**OpenSSH**
- Connection: `ssh -i ~/.ssh/beget_key root@212.8.226.218`
- Alias: `ssh beget`

---

## Configuration & Environment

### Environment Variables
**python-dotenv**
- Loads variables from `.env` file
- Variables:
  - `BOT_TOKEN`: Telegram bot API token
  - (Future: `MODEL_PATH`, `DB_PATH`, etc.)

### Configuration Files
- `.env` - Secrets and tokens
- `requirements.txt` - Python dependencies
- `/etc/systemd/system/morelli-bot.service` - systemd service config

---

## Monitoring & Logging

### System Logs
**journalctl**
- View logs: `journalctl -u morelli-bot -f`
- Log rotation: Managed by systemd
- Used for: Error tracking, debugging

### Application Logging
**Python logging module**
- Log levels: DEBUG, INFO, WARNING, ERROR
- Output: stdout (captured by systemd)
- Used for: Application events, errors

### Service Management
**systemctl**
- Commands: start, stop, restart, status, enable
- Auto-restart on failure (10s delay)
- Used for: Bot lifecycle management

---

## External APIs

### Telegram Bot API
- **Version**: Bot API 7.x+
- **Endpoint**: https://api.telegram.org/bot<TOKEN>/
- **Features Used**:
  - sendMessage
  - sendPhoto
  - getFile (for photo download)
- **Rate Limits**: 30 messages/second

### Morelli Website (Future)
- **URL**: https://morelli.ru
- **Usage**: Product images, descriptions (if needed)
- **Method**: Web scraping or API (TBD)

---

## Data Formats

### JSON
- Product catalog: `products_complete.json`
- Configuration files (future)

### SQLite Binary
- Database: `handles.db`
- Embeddings stored as BLOB

### Image Formats
- Input: JPEG, PNG (from Telegram)
- Processing: RGB arrays (NumPy/PIL)

---

## Security

### Authentication
- SSH: Public key only (no password)
- Telegram: Bot token (stored in .env)

### Secrets Management
- `.env` file (not in Git)
- File permissions: 600 (read/write owner only)

---

## Dependencies Summary

### Python Packages (requirements.txt)
```
python-telegram-bot>=20.0
torch>=2.0.0
transformers>=4.30.0
Pillow>=10.0.0
numpy
scikit-learn
python-dotenv
```

### System Packages
- Python 3.12.3
- sqlite3
- systemd
- ssh

---

## Deployment Architecture

```
User (Telegram)
    ↓
Telegram Bot API
    ↓
Beget Server (212.8.226.218)
    ↓
systemd service (morelli-bot)
    ↓
bot.py (Python 3.12.3)
    ↓
├── PyTorch + Transformers (ML inference)
├── Pillow (image processing)
└── SQLite (handles.db)
    ↓
Response to user
```

---

## Performance Considerations

### Model Optimization
- Use CPU-optimized models (no GPU on server)
- Batch processing if multiple users
- Cache frequently used embeddings in memory

### Database
- Index on article, color, style columns
- Limit embedding dimension (512-768)
- Preload embeddings on bot startup

### Image Processing
- Resize to max 512px before processing
- Convert to RGB (no alpha channel)
- Compress if file size > 5MB

---

## Future Technologies (Planned)

### Potential Additions
- **Redis**: Caching layer for embeddings
- **PostgreSQL**: If SQLite becomes limiting
- **FastAPI**: REST API for web interface
- **Docker**: Containerized deployment
- **Prometheus + Grafana**: Advanced monitoring
- **Sentry**: Error tracking
- **GitHub Actions**: CI/CD pipeline

---

## Resource Requirements

### Compute
- **CPU**: 2+ cores (for ML inference)
- **RAM**: 2GB minimum (model loading)
- **Storage**: 1GB (models + database)

### Network
- **Bandwidth**: ~1GB/month (assuming 1000 requests)
- **Latency**: <100ms to Telegram servers

### Telegram API Limits
- 30 messages/second
- 20MB max file size
- No limit on received messages
