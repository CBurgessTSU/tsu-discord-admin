#!/usr/bin/env python3
"""
Setup the TSU Discord Classes Google Sheet with proper headers and formatting
"""

from google.oauth2.service_account import Credentials
import gspread
from gspread.exceptions import WorksheetNotFound
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SHEET_ID = "1XpW6157Yo3ExH0vEnvJBJocCdgF98SNcp1TPBvDN2Bs"
SHEET_NAME = "Links"

# Scopes for Google Sheets
SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

def setup_discord_sheet():
    """Setup the Discord Classes sheet with headers and formatting"""

    # Authenticate
    creds_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    if not creds_file:
        print("ERROR: GOOGLE_SERVICE_ACCOUNT_FILE not set in .env")
        return

    credentials = Credentials.from_service_account_file(creds_file, scopes=SCOPES)
    gc = gspread.authorize(credentials)

    # Open spreadsheet
    try:
        spreadsheet = gc.open_by_key(SHEET_ID)
        print(f"✅ Opened spreadsheet: {spreadsheet.title}")
    except Exception as e:
        print(f"❌ Error opening spreadsheet: {e}")
        return

    # Get or create "Links" worksheet
    try:
        worksheet = spreadsheet.worksheet(SHEET_NAME)
        print(f"✅ Found existing worksheet: {SHEET_NAME}")

        # Don't clear - user has existing data
        print(f"⚠️  Existing content will be preserved, only updating headers")
    except WorksheetNotFound:
        # Create new worksheet
        worksheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=100, cols=10)
        print(f"✅ Created new worksheet: {SHEET_NAME}")

    # Define headers
    headers = [
        "Date Created",
        "Class Name",
        "Category ID",
        "Category Name",
        "Channel ID",
        "Channel Name",
        "Role ID",
        "Role Name",
        "Role Color",
        "OAuth URL"
    ]

    # Add headers to row 1
    worksheet.update(values=[headers], range_name='A1:J1')
    print(f"✅ Added headers: {', '.join(headers)}")

    # Format header row
    worksheet.format('A1:J1', {
        'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
        'textFormat': {
            'bold': True,
            'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
            'fontSize': 11
        },
        'horizontalAlignment': 'CENTER',
        'verticalAlignment': 'MIDDLE'
    })
    print(f"✅ Formatted headers with dark background and white bold text")

    # Note: Column widths must be set manually in Google Sheets UI
    # gspread no longer supports set_column_width in newer versions
    print(f"ℹ️  Column widths should be adjusted manually in Google Sheets if needed")

    # Freeze header row
    worksheet.freeze(rows=1)
    print(f"✅ Froze header row")

    print(f"\n🎉 Sheet setup complete!")
    print(f"📊 Sheet ID: {SHEET_ID}")
    print(f"📄 Sheet Name: {SHEET_NAME}")
    print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")

if __name__ == "__main__":
    setup_discord_sheet()
