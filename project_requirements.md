# Morelli Bot - Technical Requirements (TZ)

## Project Goal
Create a Telegram bot that analyzes photos of doors sent by users and recommends suitable Morelli door handles based on visual characteristics (color, style, material) using AI-powered image analysis and embeddings-based matching.

## Functional Requirements

### Core Features

#### 1. Photo Reception & Processing
- **Input**: User sends photo of door via Telegram
- **Processing**:
  - Accept photo in any resolution
  - Compress if needed to optimize processing
  - Extract visual features: dominant colors, style elements, material texture
- **Output**: Acknowledgment message to user

#### 2. Image Analysis
- **Color Detection**:
  - Extract 2-3 dominant colors from door
  - Convert to standard color names or hex codes
  - Weight by area coverage
- **Style Recognition**:
  - Classic/traditional
  - Modern/contemporary
  - Minimalist
  - Ornate/decorative
- **Material Detection**:
  - Wood grain patterns
  - Metal/glass elements
  - Surface finish (matte/glossy)

#### 3. Product Matching
- **Database**: SQLite with Morelli handle products
- **Matching Logic**:
  - Convert image features to embedding vector
  - Compare with pre-generated product embeddings
  - Calculate cosine similarity scores
  - Rank products by match score
- **Threshold**: Minimum similarity score for recommendations

#### 4. Recommendation Output
- **Format**: Top 3-5 handle suggestions
- **Details for Each Product**:
  - Product name and article number
  - Color/finish match explanation
  - Style compatibility note
  - Price (if available)
  - Product page link (morelli.ru)
  - Product photo
- **Fallback**: "No close matches found" if scores too low

### User Interaction Flow
1. User: `/start` → Bot: Welcome message + instructions
2. User: sends photo → Bot: "Processing your image..."
3. Bot: Analyzes photo (2-5 seconds)
4. Bot: Returns 3-5 recommendations with details
5. User: Can send another photo or ask for more details

### Bot Commands
- `/start` - Welcome message and instructions
- `/help` - Usage guide and examples
- (Optional) `/reset` - Clear conversation history

## Technical Requirements

### Infrastructure
- **Server**: Beget hosting (212.8.226.218)
- **OS**: Linux (Ubuntu/Debian)
- **Runtime**: Python 3.12.3
- **Service**: systemd for 24/7 operation
- **Database**: SQLite 3.x

### Performance
- **Response Time**: < 10 seconds per photo analysis
- **Uptime**: 99.5% availability (4h downtime/month allowed)
- **Concurrent Users**: Support up to 50 simultaneous requests
- **Database Queries**: < 500ms per similarity search

### Scalability
- Handle up to 1000 requests/day initially
- Database size: ~500-1000 products
- Image storage: Not required (process in memory)

### Security
- **Bot Token**: Stored in .env file (not in code)
- **SSH Access**: Public key authentication only
- **API Limits**: Respect Telegram API rate limits
- **Data Privacy**: Don't store user photos after processing

### Dependencies
- python-telegram-bot >= 20.0 (async/await support)
- PyTorch >= 2.0.0 (ML inference)
- transformers >= 4.30.0 (CLIP or similar models)
- Pillow >= 10.0.0 (image processing)
- sqlite3 (built-in)
- numpy, scikit-learn (similarity calculations)

## Data Requirements

### Product Database Schema
```sql
CREATE TABLE handles (
    id INTEGER PRIMARY KEY,
    article TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT,
    finish TEXT,
    style TEXT,
    price REAL,
    url TEXT,
    image_url TEXT,
    embedding BLOB  -- Serialized numpy array
);
```

### Product Data Sources
- products_complete.json (existing catalog)
- Morelli website scraping (if needed)
- Manual data entry for missing fields

### Embedding Generation
- Pre-generate embeddings for all products
- Store in `embedding` column as binary blob
- Regenerate when products updated
- Script: `generate_embeddings.py`

## Non-Functional Requirements

### Maintainability
- Code must be documented (docstrings)
- Configuration via environment variables
- Logging all errors and warnings
- Structured logs for monitoring

### Monitoring
- systemd service status
- journalctl logs for debugging
- Error alerting (future: Telegram channel)

### Backup & Recovery
- Daily database backups (to be implemented)
- Bot token backup in secure location
- Code versioned in Git (documentation repo)

## Out of Scope (Current Phase)
- Web interface
- Mobile app
- Multi-language support
- User accounts/authentication
- Payment processing
- Inventory management
- Admin panel
- Analytics dashboard

## Success Metrics
- **Accuracy**: 70%+ user satisfaction with recommendations
- **Speed**: 90% of requests processed in < 10s
- **Reliability**: < 5 crashes per week
- **Engagement**: Users send average 2+ photos per session
