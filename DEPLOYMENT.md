# Production Deployment Guide

## File Storage in Production

### Where Files Are Saved:
- **Local Development**: `C:\Users\mohsin\Downloads\Cursor 26 - CG on CK recommendations script\`
- **Production**: Files saved to the **app's working directory** where Streamlit runs

### Platform-Specific Paths:
- **Heroku**: `/app/` directory
- **Railway**: `/app/` directory  
- **Streamlit Cloud**: `/app/` directory
- **Docker**: `/app/` directory
- **VPS/Server**: `/home/user/app/` or wherever you deploy

### How It Works:
1. App starts in a specific directory (working directory)
2. All files are saved using `os.path.abspath()` for absolute paths
3. Frontend can access files because they're in the same directory
4. "Recent Files" section shows all generated files with download links

## Deployment Steps

### 1. Git Setup
```bash
git init
git add .
git commit -m "Initial commit"
```

### 2. Create GitHub Repository
- Go to GitHub.com
- Create new repository
- Copy the repository URL

### 3. Push to GitHub
```bash
git remote add origin <your-repo-url>
git push -u origin main
```

### 4. Deploy to Platform

#### Option A: Streamlit Cloud (Recommended)
1. Go to share.streamlit.io
2. Connect your GitHub repository
3. Deploy automatically

#### Option B: Railway
1. Go to railway.app
2. Connect GitHub repository
3. Auto-deploy

#### Option C: Heroku
1. Install Heroku CLI
2. Create Procfile: `web: streamlit run cardgenius_dashboard.py --server.port $PORT --server.address 0.0.0.0`
3. Deploy

## Environment Variables

For production, you may need to set:
- `CARDGENIUS_API_URL`: Your API endpoint
- `CARDGENIUS_API_KEY`: Your API key (if required)

## File Persistence

**Important**: Most cloud platforms have **ephemeral file systems**:
- Files are lost when the app restarts
- Use cloud storage (S3, Google Drive) for permanent file storage
- Current setup works for temporary file generation and download

## Monitoring

The app includes:
- Real-time processing logs
- Progress tracking
- Error handling and reporting
- File generation verification
