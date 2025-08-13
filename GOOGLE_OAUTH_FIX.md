# Fix Google OAuth Error (redirect_uri_mismatch)

## The Problem
You're getting this error because the OAuth credentials are configured incorrectly in Google Cloud Console.

## Solution Steps:

1. **Go to Google Cloud Console**
   - https://console.cloud.google.com

2. **Select your project** (or create new one)

3. **Go to APIs & Services > Credentials**

4. **Delete the existing OAuth 2.0 Client ID** (if any)

5. **Create NEW OAuth 2.0 Client ID:**
   - Click "CREATE CREDENTIALS" > "OAuth client ID"
   - **Application type: Desktop app** ← IMPORTANT!
   - Name: "Virtual Secretary" (or any name)
   - Click "CREATE"

6. **Download the JSON file**
   - Click the download button
   - Save as `credentials.json` in the project folder

7. **Enable Required APIs:**
   - Go to "Library" section
   - Search and enable: "Gmail API"
   - Search and enable: "Google Calendar API"

## Common Mistakes:
- ❌ Using "Web application" instead of "Desktop app"
- ❌ Not enabling the Gmail/Calendar APIs
- ❌ Using wrong project

## After Fixing:
1. Replace your `credentials.json` with the new one
2. Delete any `token.pickle` or `calendar_token.pickle` files
3. Run the bot again - it will open browser for authorization