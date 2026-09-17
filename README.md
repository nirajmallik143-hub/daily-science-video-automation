# Daily Science Video Automation 🚀

Automated daily video generation and posting about **Science, Math, Quantum Physics, Quantum Computing & Newton's Laws** to YouTube, Instagram Reels, and TikTok.

## Features

✅ **AI-Powered Content Generation**
- Automatically generates scripts on science/math/quantum topics
- Text-to-speech narration
- Stock footage integration
- Automatic captions & subtitles
- Thumbnail generation

✅ **Multi-Platform Posting**
- YouTube & YouTube Shorts
- Instagram Reels
- TikTok

✅ **Automated Daily Scheduling**
- GitHub Actions runs at specified time daily
- No manual intervention needed

## Project Structure

```
daily-science-video-automation/
├── .github/workflows/
│   └── daily-post.yml              # GitHub Actions daily scheduler
├── scripts/
│   ├── generate_script.py           # AI script generation
│   ├── generate_video.py            # Video assembly
│   ├── upload_youtube.py            # YouTube uploader
│   ├── upload_instagram.py          # Instagram Reels uploader
│   ├── upload_tiktok.py             # TikTok uploader
│   └── main.py                      # Main orchestrator
├── config/
│   ├── topics.json                  # Topic database
│   └── config.json                  # Configuration
├── assets/
│   ├── stock_footage/               # Stock video clips
│   └── music/                       # Background music
├── output/
│   └── videos/                      # Generated videos (temp)
├── requirements.txt                 # Python dependencies
└── README.md
```

## Setup Guide

### Prerequisites

- Python 3.8+
- GitHub account
- Google Cloud account with YouTube API enabled
- Meta Business account (for Instagram)
- TikTok Business API access
- FFmpeg installed

### 1. Clone & Install Dependencies

```bash
git clone https://github.com/nirajmallik143-hub/daily-science-video-automation.git
cd daily-science-video-automation
pip install -r requirements.txt
```

### 2. Google Cloud Setup (YouTube)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the `credentials.json` file
6. Place it in the repo root directory

### 3. Meta/Instagram Setup

1. Go to [Meta Developers](https://developers.facebook.com)
2. Create an app (Instagram Graph API)
3. Get your **Page Access Token** & **Page ID**
4. Add as GitHub Secret: `META_ACCESS_TOKEN`, `INSTAGRAM_PAGE_ID`

### 4. TikTok Setup

1. Apply for [TikTok API Access](https://developers.tiktok.com)
2. Get your **Client ID**, **Client Secret**, **Access Token**
3. Add as GitHub Secrets: `TIKTOK_CLIENT_ID`, `TIKTOK_CLIENT_SECRET`, `TIKTOK_ACCESS_TOKEN`

### 5. GitHub Secrets Configuration

Go to **Settings → Secrets and variables → Actions** and add:

```
GOOGLE_CREDENTIALS_JSON    # Content of credentials.json (as JSON string)
META_ACCESS_TOKEN          # Instagram Page Access Token
INSTAGRAM_PAGE_ID          # Instagram Page ID
TIKTOK_CLIENT_ID           # TikTok API Client ID
TIKTOK_CLIENT_SECRET       # TikTok API Client Secret
TIKTOK_ACCESS_TOKEN        # TikTok API Access Token
OPENAI_API_KEY             # For AI script generation
```

### 6. Enable GitHub Actions

1. Go to your repo → **Actions**
2. Enable workflows
3. The workflow runs daily at **09:00 UTC** (configurable in `.github/workflows/daily-post.yml`)

## How It Works

1. **Script Generation** → AI creates a script on a random science topic
2. **Video Assembly** → Combines voiceover + stock footage + captions
3. **Thumbnail Creation** → Auto-generates eye-catching thumbnail
4. **Multi-Platform Upload** → Posts to YouTube, Instagram Reels & TikTok simultaneously
5. **Logging** → Tracks all uploads and errors

## Configuration

Edit `config/config.json` to customize:

```json
{
  "video": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "duration": 60
  },
  "upload_schedule": "0 9 * * *",
  "topics": ["quantum_physics", "quantum_computing", "newton_laws", "math", "science"]
}
```

## Topics Covered

- 🔬 **Quantum Physics** - Superposition, entanglement, wave-particle duality
- 💻 **Quantum Computing** - Qubits, quantum algorithms, quantum advantage
- 📐 **Newton's Laws** - Motion, force, gravitation
- 🧮 **Math** - Calculus, algebra, geometry, physics equations
- 🌌 **Science** - Astrophysics, relativity, thermodynamics

## Troubleshooting

### Videos Not Uploading?
- Check GitHub Actions logs: **Actions → daily-post → latest run**
- Verify API credentials in GitHub Secrets
- Ensure YouTube/Meta/TikTok APIs are enabled

### Quality Issues?
- Adjust stock footage sources in `config/config.json`
- Modify script length in `generate_script.py`
- Change video resolution in config

### Rate Limits?
- YouTube: 10,000 quota units/day (each upload ≈ 1,500 units)
- Instagram: Rate-limited per hour
- TikTok: Check API rate limits

## Future Enhancements

- [ ] Multi-language support
- [ ] Analytics dashboard (views, likes, shares)
- [ ] AI thumbnail A/B testing
- [ ] Trend-based topic selection
- [ ] Comment automation
- [ ] Monetization tracking

## License

MIT License - feel free to fork and modify!

## Support

For issues or questions, create a GitHub Issue in this repo.

---

**Built with ❤️ for science education automation**
