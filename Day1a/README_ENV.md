# Environment Variables Setup for Day1a Agents

This guide explains how to set up the `.env` file for running agents in Day1a.

## Quick Setup

1. **Copy the example file:**
   ```powershell
   cd kaggle-5-day-agents\Day1a\helpful_assistant
   copy .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   - Replace `your-gemini-api-key-here` with your actual Google AI API key
   - Verify `GOOGLE_CLOUD_PROJECT` is set to your project ID

3. **Verify your setup:**
   ```powershell
   cd ..
   .\verify-env.ps1
   ```

## Required Environment Variables

### GOOGLE_CLOUD_PROJECT
- **Required**: Yes
- **Description**: Your Google Cloud Project ID
- **Example**: `aiagent-capstoneproject`
- **Used by**: Vertex AI initialization for all agents

### GOOGLE_API_KEY
- **Required**: Yes
- **Description**: Google AI API key for Gemini API access
- **How to get**: [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Used by**: Gemini model access

## Optional Environment Variables

### GOOGLE_CLOUD_LOCATION
- **Required**: No (defaults to `us-central1`)
- **Description**: Google Cloud region/location
- **Default**: `us-central1`
- **Used by**: Vertex AI initialization

### GOOGLE_APPLICATION_CREDENTIALS
- **Required**: No (can use gcloud auth instead)
- **Description**: Path to service account JSON file
- **Alternative**: Run `gcloud auth application-default login`
- **Used by**: Vertex AI authentication

### ADK_LOG_LEVEL
- **Required**: No
- **Description**: Logging level for ADK (DEBUG, INFO, WARNING, ERROR)
- **Default**: DEBUG
- **Used by**: Agent logging configuration

## Example .env File

```env
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=aiagent-capstoneproject
GOOGLE_CLOUD_LOCATION=us-central1

# Google AI API Key
GOOGLE_API_KEY=AIzaSyAaPeS-PaJ0UGRG6vAMuSoa5joAOpdQ5O8

# Optional: Service Account
# GOOGLE_APPLICATION_CREDENTIALS=../service-account.json
```

## Verification

Run the verification script to check your configuration:

```powershell
cd kaggle-5-day-agents\Day1a
.\verify-env.ps1
```

This will check:
- ✓ All required variables are set
- ✓ Values are not empty
- ✓ Service account file exists (if specified)

## Authentication Setup

You have two options for Vertex AI authentication:

### Option 1: Application Default Credentials (Recommended)

```powershell
gcloud auth application-default login
```

This sets up authentication automatically and is the easiest method.

### Option 2: Service Account JSON File

1. Download service account JSON from Google Cloud Console
2. Place it in a secure location
3. Set the path in `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
   ```

## Getting Your Google AI API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Select your project (or create a new one)
4. Copy the API key
5. Paste it in your `.env` file as `GOOGLE_API_KEY`

## Troubleshooting

### Error: "Missing key inputs argument"

This means required environment variables are not set. Run:
```powershell
.\verify-env.ps1
```

### Error: "Authentication failed"

Make sure you've set up authentication:
```powershell
gcloud auth application-default login
```

Or set `GOOGLE_APPLICATION_CREDENTIALS` to a valid service account file.

### Error: "Project not found"

Verify your `GOOGLE_CLOUD_PROJECT` is correct:
```powershell
gcloud projects list
```

### .env file not loading

Make sure:
1. The `.env` file is in the same directory as `agent.py`
2. You're using `load_dotenv()` in your code (already included)
3. The file is named exactly `.env` (not `.env.txt`)

## Security Notes

⚠️ **Important**: Never commit your `.env` file to version control!

The `.env` file should be in `.gitignore` (it already is). It contains sensitive credentials:
- API keys
- Service account paths
- Project IDs

Always use `.env.example` as a template for others, without actual credentials.

## Additional Resources

- [Google AI Studio](https://aistudio.google.com/app/apikey) - Get API keys
- [Vertex AI Authentication](https://cloud.google.com/vertex-ai/docs/authentication)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)

