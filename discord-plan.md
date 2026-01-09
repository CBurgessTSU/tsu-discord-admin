# TSU Discord Admin Panel - Implementation Instructions for Claude Code

## Your Task
Build a complete admin panel system for TradeSmart University that allows team members to create Discord class channels with automated setup. You'll be building:
1. An n8n workflow that creates Discord resources (category, channel, role) and handles errors with rollback
2. A static HTML frontend for the admin panel
3. Google Sheets integration for logging
4. Full error handling and validation

**Start with the n8n workflow first** since n8n is already running. After that's tested, we'll build the frontend.

---

## Project Overview
Build an admin panel that allows TSU team members to create Discord class channels with one click. The system creates a category, channel, role, sets permissions, logs to Google Sheet, and generates an OAuth join link.

---

## Part 1: Frontend (HTML/CSS/JS Static Site)

### File: `index.html`

**Requirements:**
1. Clean, modern UI with TSU branding
2. Single input field: "Class Name"
3. Input validation: Only allow alphanumeric characters, spaces, hyphens, and underscores
4. "Create Discord Channel" button (disabled until valid input)
5. Loading state while webhook processes
6. Success display showing all created resources
7. "Copy Join Link" button with visual confirmation
8. Error display with details if creation fails
9. Basic HTTP authentication (username: "tsu", password: "tsu")

**Input Validation:**
```javascript
// Real-time validation as user types
// Regex pattern: ^[a-zA-Z0-9\s\-_]+$
// Show red border if invalid, green if valid
// Disable submit button if invalid
```

**Success Response Display:**
```
✅ Successfully created: [Class Name]

Discord Resources Created:
- Category: [Category Name] (ID: [Category ID])
- Channel: #[channel-name]-chat (ID: [Channel ID])
- Role: [Role Name] (ID: [Role ID])

[Copy Join Link] ← button with clipboard icon
```

**UI Specifications:**
- Max width: 600px, centered
- Font: System sans-serif
- Primary button color: #4b48d7
- Clean white background
- Subtle shadows for depth
- Mobile responsive

---

## Part 2: n8n Workflow Structure

### Webhook: `/webhook/create-discord-class`

**Input (POST JSON):**
```json
{
  "className": "Options 201"
}
```

**Output (Success):**
```json
{
  "success": true,
  "className": "Options 201",
  "category": {
    "id": "1234567890",
    "name": "Options 201"
  },
  "channel": {
    "id": "0987654321",
    "name": "options-201-chat"
  },
  "role": {
    "id": "1122334455",
    "name": "Options 201",
    "color": "#1f8b4c"
  },
  "oauthUrl": "https://discord.com/api/oauth2/authorize?client_id=...&state=1122334455"
}
```

**Output (Error):**
```json
{
  "success": false,
  "error": "Category 'Options 201' already exists",
  "rollback": "All created resources have been deleted"
}
```

### Workflow Steps (Sequential)

#### Step 1: Validate Input
- Check if `className` is provided
- Check if not empty after trim
- If invalid, return error immediately

#### Step 2: Check for Duplicates
Use Discord API to list:
- All categories (check if name exists)
- All channels (check if `[slugified-name]-chat` exists)
- All roles (check if role name exists)

If any exist, return error:
```json
{
  "success": false,
  "error": "Category/Channel/Role 'Options 201' already exists"
}
```

#### Step 3: Create Discord Role
**API:** `POST https://discord.com/api/guilds/{GUILD_ID}/roles`

**Body:**
```json
{
  "name": "Options 201",
  "color": 2066252,
  "hoist": false,
  "mentionable": false,
  "permissions": "0"
}
```

**IMPORTANT:** The role is created with NO permissions (permissions set to "0"). All permissions are denied at the role level. Permissions will ONLY be granted at the channel level via permission overwrites.

**Note:** `color` is decimal for #1f8b4c (Discord green)

**Store:** `roleId`, `roleName`

**Error handling:** If fails, return error and exit

#### Step 4: Create Discord Category
**API:** `POST https://discord.com/api/guilds/{GUILD_ID}/channels`

**Body:**
```json
{
  "name": "Options 201",
  "type": 4,
  "permission_overwrites": [
    {
      "id": "{GUILD_ID}",
      "type": 0,
      "deny": "1024"
    }
  ]
}
```

**IMPORTANT:** 
- The category is created as Private
- Only @everyone has permissions set (deny VIEW_CHANNEL)
- The class role is NOT added to category permissions - it will be added only to the channel

**Store:** `categoryId`, `categoryName`

**Error handling:** If fails, delete created role and return error

#### Step 5: Create Discord Channel
**API:** `POST https://discord.com/api/guilds/{GUILD_ID}/channels`

**Body:**
```json
{
  "name": "[slugified-class-name]-chat",
  "type": 0,
  "parent_id": "{categoryId}",
  "permission_overwrites": [
    {
      "id": "{GUILD_ID}",
      "type": 0,
      "deny": "1024"
    },
    {
      "id": "{roleId}",
      "type": 0,
      "allow": "448824462400",
      "deny": "0"
    }
  ]
}
```

**IMPORTANT:** 
- The channel is created as Private inside the category
- @everyone is denied VIEW_CHANNEL (1024)
- The class role is added with ALLOW permissions of 448824462400
- This bitmask includes these permissions:
  - VIEW_CHANNEL (1024)
  - SEND_MESSAGES (2048)
  - ADD_REACTIONS (64)
  - EMBED_LINKS (16384)
  - ATTACH_FILES (32768)
  - READ_MESSAGE_HISTORY (65536)
  - USE_EXTERNAL_EMOJIS (262144)
  - USE_APPLICATION_COMMANDS (2147483648)
  - CREATE_PUBLIC_THREADS (34359738368)
  - USE_EXTERNAL_STICKERS (137438953472)
  - SEND_MESSAGES_IN_THREADS (274877906944)
- All other permissions remain Inherited (neutral)

**Store:** `channelId`, `channelName`

**Error handling:** If fails, delete role and category, return error

#### Step 6: Generate OAuth URL
```javascript
const oauthUrl = `https://discord.com/api/oauth2/authorize?client_id=1458911804368490654&redirect_uri=https%3A%2F%2Ftsu-n8n.onrender.com%2Fwebhook%2Fdiscord-oauth&response_type=code&scope=identify%20guilds.join&state=${roleId}`;
```

#### Step 7: Log to Google Sheet
**Sheet Name:** "Discord Classes"

**Columns:**
| Date Created | Class Name | Category ID | Category Name | Channel ID | Channel Name | Role ID | Role Name | Role Color | OAuth URL |

**Row Data:**
```
[TODAY_DATE] | Options 201 | 1234567890 | Options 201 | 0987654321 | options-201-chat | 1122334455 | Options 201 | #1f8b4c | [OAUTH_URL]
```

Use Google Sheets node in n8n:
- Operation: Append
- Spreadsheet: (User will create and provide ID)
- Sheet: "Discord Classes"

#### Step 8: Return Success Response
Return the JSON structure specified above

---

## Part 3: Slugification Function

**Purpose:** Convert "Options 201" → "options-201-chat"

**Algorithm:**
```javascript
function slugify(className) {
  return className
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^a-z0-9\-_]/g, '')
    + '-chat';
}
```

**Examples:**
- "Options 201" → "options-201-chat"
- "Advanced Trading 101" → "advanced-trading-101-chat"
- "Futures & Options" → "futures-options-chat"

---

## Part 4: Permissions Architecture

### Role Permissions (Step 3)
The role itself has **NO permissions** - everything is denied/neutral:
```json
{
  "permissions": "0"
}
```

### Category Permissions (Step 4)
The category is Private with only @everyone permissions:
```json
"permission_overwrites": [
  {
    "id": "{GUILD_ID}",  // @everyone
    "type": 0,
    "deny": "1024"  // VIEW_CHANNEL denied
  }
]
```

### Channel Permissions (Step 5)
The channel is Private with @everyone denied and class role allowed specific permissions:
```json
"permission_overwrites": [
  {
    "id": "{GUILD_ID}",  // @everyone
    "type": 0,
    "deny": "1024"  // VIEW_CHANNEL denied
  },
  {
    "id": "{roleId}",  // The class role
    "type": 0,
    "allow": "448824462400",  // Specific permissions allowed
    "deny": "0"
  }
]
```

**The 448824462400 bitmask breakdown:**
```
VIEW_CHANNEL:                1024
SEND_MESSAGES:               2048
ADD_REACTIONS:               64
EMBED_LINKS:                 16384
ATTACH_FILES:                32768
READ_MESSAGE_HISTORY:        65536
USE_EXTERNAL_EMOJIS:         262144
USE_APPLICATION_COMMANDS:    2147483648
CREATE_PUBLIC_THREADS:       34359738368
USE_EXTERNAL_STICKERS:       137438953472
SEND_MESSAGES_IN_THREADS:    274877906944
-------------------------------------------
TOTAL:                       448824462400
```

---

## Part 5: Google Sheet Setup

**Manual Setup Required:**
1. Create new Google Sheet named "TSU Discord Classes"
2. Create sheet tab named "Discord Classes"
3. Add header row:
```
   Date Created | Class Name | Category ID | Category Name | Channel ID | Channel Name | Role ID | Role Name | Role Color | OAuth URL
```
4. Share with n8n service account email
5. Copy Sheet ID from URL
6. Provide Sheet ID to n8n workflow

---

## Part 6: Rollback Logic

**When Error Occurs:**

Track which resources were created in workflow variables:
```javascript
let createdResources = {
  roleId: null,
  categoryId: null,
  channelId: null
};
```

**On Error, Delete in Reverse Order:**
1. If `channelId` exists: `DELETE https://discord.com/api/channels/{channelId}`
2. If `categoryId` exists: `DELETE https://discord.com/api/channels/{categoryId}`
3. If `roleId` exists: `DELETE https://discord.com/api/guilds/{GUILD_ID}/roles/{roleId}`

Return error message: "Error occurred: [DETAILS]. All created resources have been rolled back."

---

## Part 7: Deployment Checklist

### Frontend Deployment to Render:
1. Create GitHub repo: `tsu-discord-admin`
2. Add `index.html` to repo root
3. Create Render Static Site
4. Connect to GitHub repo
5. Set build command: (none needed)
6. Set publish directory: `/`
7. Add environment variable for basic auth (if Render supports, otherwise handle in HTML)
8. Deploy

### n8n Webhook Configuration:
1. Enable webhook endpoint: `/webhook/create-discord-class`
2. Set method: POST
3. Enable CORS for frontend domain
4. Test with Postman/curl before connecting frontend

### Testing Checklist:
- [ ] Valid input creates all resources correctly
- [ ] Invalid characters are blocked by frontend
- [ ] Duplicate names return appropriate error
- [ ] OAuth URL works (assigns role correctly)
- [ ] Google Sheet logs data correctly
- [ ] Rollback works when Discord API fails
- [ ] Copy button copies URL to clipboard
- [ ] Mobile responsive layout works
- [ ] Basic auth protects the page
- [ ] Channel permissions are correctly set (role members can view/chat)
- [ ] Category shows as Private in Discord UI
- [ ] Channel shows as Private in Discord UI
- [ ] Non-role members cannot see the category or channel

---

## Part 8: Environment Variables Needed

**For n8n workflow:**
```
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
DISCORD_CLIENT_ID=your_client_id_here
GOOGLE_SHEET_ID=your_google_sheet_id_here
```

**For frontend:**
```
N8N_WEBHOOK_URL=https://tsu-n8n.onrender.com/webhook/create-discord-class
```

---

## Part 9: Implementation Order

**Do in this exact order:**

1. **Create Google Sheet** (using Google Sheets API and your Google Sheets Skills)
2. **Build n8n workflow** (test with Postman)
3. **Test rollback logic** (simulate failures)
4. **Build frontend HTML** (test locally)
5. **Deploy to Render** (static site)
6. **End-to-end testing** (create real class)
7. **Verify permissions** (check that only role members can see channel)
8. **Clean up test resources** (delete test categories/roles)
9. **Document for TSU team** (how to use)

---

## Success Criteria

✅ TSU team member can:
1. Open admin panel at `https://tsu-discord-admin.onrender.com`
2. Login with tsu/tsu
3. Type "Options 201" in input field
4. Click "Create Discord Channel"
5. See success message within 5 seconds
6. Click "Copy Join Link"
7. Paste link into ClickFunnels Thank You page
8. Student clicks link and gets role assigned
9. Student immediately sees the new category and channel in Discord
10. Student can send messages in the channel

✅ Error handling works:
- Duplicate names prevented
- Invalid input blocked
- Failed API calls rolled back
- Clear error messages displayed

✅ Data logging works:
- All resources logged to Google Sheet
- Sheet readable and organized

✅ Permissions work correctly:
- @everyone cannot see category or channel
- Role members can view channel
- Role members can send messages and interact
- Admin roles maintain full access

---

## Architecture Summary
```
Admin Panel Frontend (Render Static Site)
    ↓
POST to n8n webhook: /webhook/create-discord-class
    ↓
n8n Workflow:
  1. Validate input
  2. Check for duplicates
  3. Create Discord Role (NO permissions, color #1f8b4c)
  4. Create Discord Category (Private, @everyone denied)
  5. Create Discord Channel (Private, @everyone denied, role allowed specific permissions)
  6. Generate OAuth URL with role ID
  7. Log to Google Sheet
  8. Return success JSON
  ↓ (if error at any step)
  Rollback: Delete all created resources
    ↓
Frontend displays result (success or error)
```

---

## Notes on Discord Permissions

**Permission Overwrites Structure:**
- `id`: Role ID or Guild ID
- `type`: 0 for role, 1 for member
- `allow`: Permissions to grant (bitmask as string)
- `deny`: Permissions to deny (bitmask as string)

**Key Understanding:**
- Role itself has permissions: "0" (nothing granted at role level)
- Category has overwrites: only @everyone denied
- Channel has overwrites: @everyone denied + class role allowed specific actions
- Everything not explicitly allowed or denied is "Inherited" (neutral)

---

## Key Implementation Details

### Naming Conventions:
- **Category:** Exactly as user types (e.g., "Options 201")
- **Channel:** Slugified + "-chat" suffix (e.g., "options-201-chat")
- **Role:** Exactly as user types (e.g., "Options 201")

### Role Configuration:
- **Color:** 2066252 (decimal for #1f8b4c)
- **Hoist:** false (don't display separately)
- **Mentionable:** false (prevents spam)
- **Permissions:** "0" (no server-wide permissions)

### Channel Types (Discord):
- 0 = Text channel
- 4 = Category

### Permission Bitmasks (as strings in API):
- Category @everyone deny: "1024"
- Channel @everyone deny: "1024"
- Channel role allow: "448824462400"
- Channel role deny: "0"

### Date Format for Google Sheet:
```javascript
new Date().toLocaleDateString('en-US')  // "1/8/2026"
```

---

## Critical Reminders

1. **Role permissions are "0"** - all permissions happen at the channel level
2. **Category does NOT have the role in permissions** - only @everyone is denied
3. **Channel has BOTH @everyone deny AND role allow** - this is where the magic happens
4. **Use strings for permission bitmasks** in API calls, not integers
5. **All three resources must be tracked for rollback** - delete in reverse order if any step fails

---

## Start Here

**Begin with Step 1:** Get the Discord Guild ID and Google Sheet ID, then start building the n8n workflow at `/webhook/create-discord-class`. 

**Test the permissions carefully** - create a test class, assign yourself the test role, and verify you can see and interact with the channel. Then remove the role and verify you cannot see it anymore.

Let me know when you're ready to begin!