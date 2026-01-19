# Local Server Scripts

Quick scripts to run the Bhrikutimandap development server locally.

## 📝 Available Scripts

### 1. **run_server.bat** (Simplest - Recommended for daily use)
Start the Django development server immediately.

```bash
# Double-click or run from PowerShell:
.\run_server.bat
```

- ✅ Activates virtual environment
- ✅ Starts Django on http://127.0.0.1:8000
- ✅ Fast startup

**Use this for:** Regular development

---

### 2. **run_server.ps1** (PowerShell alternative)
Same as run_server.bat but using PowerShell with colored output.

```bash
# From PowerShell:
.\run_server.ps1
```

**Note**: May require execution policy change:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Use this for:** Developers who prefer PowerShell

---

### 3. **run_server_with_migrate.bat** (For after code/model changes)
Runs migrations first, then starts the server.

```bash
.\run_server_with_migrate.bat
```

- ✅ Activates virtual environment
- ✅ Runs database migrations (`python manage.py migrate`)
- ✅ Starts Django server

**Use this for:** After pulling code changes, adding new models, or creating migrations

---

### 4. **dev_setup.bat** (One-time setup)
Initial setup script - runs migrations and collects static files.

```bash
.\dev_setup.bat
```

- ✅ Activates virtual environment
- ✅ Runs migrations
- ✅ Collects static files
- ✅ Shows completion summary

**Use this for:** First-time setup or fresh clone

---

## 🚀 Quick Start

### First Time Setup
```bash
# 1. Double-click dev_setup.bat
.\dev_setup.bat

# 2. Then run the server
.\run_server.bat
```

### Daily Development
```bash
# Just run:
.\run_server.bat

# OR double-click the file in Explorer
```

### After Code Changes
```bash
# Run with migrations:
.\run_server_with_migrate.bat
```

---

## 🌐 Access Points

Once server is running:

| Service | URL | Purpose |
|---------|-----|---------|
| Site | http://127.0.0.1:8000 | Main website |
| Admin | http://127.0.0.1:8000/admin | Django admin panel |
| API (if enabled) | http://127.0.0.1:8000/api | REST API endpoints |

---

## ⚙️ What Each Script Does

### run_server.bat
```batch
1. Navigate to script directory
2. Activate .venv\Scripts\activate.bat
3. Run: python manage.py runserver 0.0.0.0:8000
4. Press Ctrl+C to stop
```

### run_server_with_migrate.bat
```batch
1. Navigate to script directory
2. Activate virtual environment
3. Run: python manage.py migrate
4. Run: python manage.py runserver 0.0.0.0:8000
```

### dev_setup.bat
```batch
1. Navigate to script directory
2. Activate virtual environment
3. Run: python manage.py migrate
4. Run: python manage.py collectstatic --noinput
5. Show completion message
```

---

## 🔧 Common Issues

### Issue: "virtual environment not found"
**Solution**: Create virtual environment first
```bash
python -m venv .venv
```

### Issue: "python not found"
**Solution**: Ensure Python is in PATH or use full path
```bash
C:\Python310\python.exe manage.py runserver
```

### Issue: "Port 8000 already in use"
**Solution**: Stop other instances or use different port
```bash
python manage.py runserver 0.0.0.0:8001
```

### Issue: "Permission denied" (PowerShell)
**Solution**: Change execution policy
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📋 Requirements

- Python virtual environment (`.venv/`) must exist
- Django must be installed in virtual environment
- `manage.py` must be in the same directory

---

## 🎯 Recommended Workflow

1. **First time**: Run `dev_setup.bat`
2. **Daily**: Double-click `run_server.bat`
3. **After git pull**: Run `run_server_with_migrate.bat`
4. **Fresh start**: Run `dev_setup.bat` again

---

## 📝 Manual Commands (for reference)

If you prefer to run commands manually:

```bash
# Activate virtual environment
.\.venv\Scripts\activate.ps1

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver 0.0.0.0:8000

# Collect static files
python manage.py collectstatic --noinput

# Create admin user
python manage.py createsuperuser
```

---

## 🔗 Related Scripts

- `dev_setup.bat` - Initial setup
- `run_server.bat` - Start server
- `run_server_with_migrate.bat` - Server with migrations
- `run_server.ps1` - PowerShell version

---

## ✅ Checklist Before First Run

- [ ] Virtual environment created (`.venv/`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] Database file exists or will be created
- [ ] Static files collected

---

**💡 Tip**: Add these scripts to your task scheduler or create desktop shortcuts for even faster access!

