# TSU Discord Class Manager

A web-based admin panel for TradeSmart University that automates Discord class setup and student onboarding.

## Overview

This system allows TSU staff to quickly create Discord classes and generate join links for students. It automates the entire setup process including category creation, channel creation, role assignment, and permission configuration.

## Features

### 🆕 Create New Class
- **Automated Discord Setup**: Creates a Discord category, text channel, and role in one click
- **Permission Management**: Automatically configures permissions so only students with the assigned role can access the class
- **Join Link Generation**: Generates an OAuth2 authorization link that students can click to join and automatically receive the role
- **Google Sheets Logging**: Logs all created resources to a Google Sheet for tracking and management

### 🔗 Existing Role Link
- **Role Selection**: Browse all existing Discord roles with a visual dropdown (shows role colors like Discord)
- **Quick Link Generation**: Generate OAuth2 join links for any existing class role
- **One-Click Copy**: Easy copy button to share links with students

## How It Works

### For Admins

1. **Access the Admin Panel**: Navigate to the deployed frontend URL
2. **Authenticate**: Enter the password when prompted (credentials provided separately)
3. **Choose an Option**:
   - **Create New Class**: Enter a class name, click "Create Discord Channel"
   - **Existing Role Link**: Select a role from the dropdown, click "Generate Join Link"
4. **Share the Link**: Copy the generated OAuth2 link and share it with students

### For Students

1. **Click the Join Link**: Students click the OAuth2 link provided by the admin
2. **Authorize with Discord**: Discord prompts them to authorize the TSU bot
3. **Automatic Role Assignment**: Upon authorization, they are automatically:
   - Added to the TSU Discord server (if not already a member)
   - Assigned the class role
   - Granted access to the class channel

## Technical Architecture

### Components

1. **Frontend**: Static HTML/CSS/JavaScript site
   - Hosted on Render
   - Includes input validation, loading states, error handling
   - Password protected (basic HTTP auth via JavaScript)

2. **Backend**: n8n workflow automation
   - Webhook endpoint: `https://tsu-n8n.onrender.com/webhook/create-discord-class`
   - Discord API integration for resource creation
   - Google Sheets API integration for logging
   - Error handling with automatic rollback on failure

3. **OAuth Flow**: n8n workflow for student onboarding
   - Webhook endpoint: `https://tsu-n8n.onrender.com/webhook/discord-oauth`
   - Handles Discord OAuth2 callback
   - Adds users to server and assigns roles

4. **Logging**: Google Sheets
   - Tracks all created classes
   - Records: Date, Class Name, Category ID, Channel ID, Role ID, OAuth URL

### Tech Stack

- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Automation**: n8n (self-hosted on Render)
- **APIs**: Discord API, Google Sheets API
- **Hosting**: Render (static site + n8n instance)

## Deployment

### Frontend Deployment

The frontend is deployed as a static site on Render:
- Automatically deploys from the `main` branch
- No build process required (static HTML)
- Live URL: (Render will provide this)

### n8n Configuration

The n8n instance requires the following environment variables:

```
DISCORD_BOT_TOKEN=<your_bot_token>
DISCORD_GUILD_ID=<your_guild_id>
DISCORD_CLIENT_ID=<your_client_id>
GOOGLE_SHEET_ID=<your_sheet_id>
```

### Discord Bot Setup

The Discord bot requires the following permissions:
- Manage Roles
- Manage Channels
- View Channels
- Read Messages/View Channels

OAuth2 Redirect URI:
```
https://tsu-n8n.onrender.com/webhook/discord-oauth
```

## Files

- `index.html` - Main frontend interface
- `tsu_logo.jpg` - TSU logo image
- `favicon.png` - Browser favicon
- `.gitignore` - Excludes sensitive files from Git
- `setup_discord_sheet.py` - Python script to initialize Google Sheet with headers

## Security Notes

- The `.env` file contains sensitive credentials and is excluded from Git
- The `.git-token` file contains the GitHub personal access token and is excluded from Git
- Basic password protection is implemented in the frontend
- OAuth flow uses secure Discord authorization

## Support

For issues or questions, contact the TSU development team.

## License

Internal use only - TradeSmart University
