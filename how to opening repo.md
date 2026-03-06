# 📖 How to Open the Veryfyn Repository

**A step-by-step guide to opening and running the Veryfyn Personal Tracking System project.**

---

## 📋 Table of Contents

| # | Section |
|---|---------|
| 1 | [Prerequisites](#1-prerequisites) |
| 2 | [Clone the Repository](#2-clone-the-repository) |
| 3 | [Open in VS Code](#3-open-in-vs-code) |
| 4 | [Running the Project](#4-running-the-project) |
| 4.1 | [Opening the Localhost (Streamlit App)](#-41-opening-the-localhost-streamlit-app) |
| 5 | [Troubleshooting](#5-troubleshooting) |
| 6 | [Quick Reference](#6-quick-reference) |

---

## §1 Prerequisites

Before opening the project, ensure you have the following installed:

| Tool | Purpose | Download |
|------|---------|----------|
| **VS Code** | Code editor | [code.visualstudio.com](https://code.visualstudio.com/) |
| **Git** | Version control | [git-scm.com](https://git-scm.com/) |
| **Python 3.8+** | Backend runtime | [python.org](https://www.python.org/) |
| **Web Browser** | Running the app | Chrome, Firefox, Safari, or Edge |

### Optional but Recommended

| Tool | Purpose |
|------|---------|
| **Live Server Extension** | Hot reload for development (VS Code extension) |
| **ESLint Extension** | Code quality (VS Code extension) |
| **Prettier Extension** | Code formatting (VS Code extension) |

---

## §2 Clone the Repository

### Option A: Using Terminal/Command Line

```bash
# Navigate to where you want the project
cd ~/Documents

# Clone the repository
git clone https://github.com/Rstiltski/tracking-system.git

# Navigate into the project folder
cd tracking-system
```

### Option B: Using VS Code

1. Open VS Code
2. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
3. Type `Git: Clone` and select it
4. Paste the repository URL: `https://github.com/Rstiltski/tracking-system.git`
5. Choose a folder location for the project
6. Click "Open" when prompted

---

## §3 Open in VS Code

### Method 1: Double-Click Workspace File (Easiest)

1. Navigate to the project folder in your file explorer
2. **Double-click `veryfyn.code-workspace`**
3. VS Code will open with all project settings configured

### Method 2: Open Folder

1. Open VS Code
2. Go to **File → Open Folder**
3. Navigate to and select the `tracking-system` folder
4. Click **Open**

### Method 3: Command Line

```bash
# From the project directory
code .

# Or open the workspace file directly
code veryfyn.code-workspace
```

### Method 4: Right-Click (Windows/Linux)

1. Right-click the `tracking-system` folder
2. Select **"Open with Code"**

---

## §4 Running the Project

The project can run in two modes:

### 🌐 Mode 1: Browser-Only (Simplest)

No server required - runs entirely in your browser using LocalStorage.

**Steps:**

1. Open the project folder in VS Code
2. Locate `index.html` in the file explorer (left sidebar)
3. **Right-click `index.html`** → Select **"Open with Live Server"** (if extension installed)
   
   **OR**
   
   **Right-click `index.html`** → Select **"Reveal in File Explorer"** → Double-click to open in browser

**Using Live Server Port:**
- The workspace is configured to use port **5501**
- Access at: `http://localhost:5501`

### 🐍 Mode 2: Full System (With Python Backend)

Includes the Brain system with AI features, database, and admin interface.

**Steps:**

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Initialize the database (first time only)
python3 init_db_script.py
python3 force_admin_reset.py

# 3. Run the system
python3 run_system.py
```

**Access the application:**
- Open your browser to: **http://localhost:5501**

---

## 🚀 §4.1 Opening the Localhost (Streamlit App)

The main tracking system runs as a **Streamlit application** on port **8501**. Follow these steps to start and access it:

### Starting the Streamlit Server

Open a terminal and run:

```bash
# Navigate to the project directory
cd "/home/ramplestiltski/Documents/a_tracking>system/project tracking system/tracking-system"

# Start the Streamlit server
streamlit run tracking_app/app.py --server.port 8501
```

### Accessing the Application

Once the server is running, you'll see output like:

```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.100.54:8501
```

**Open your browser and navigate to:**

| URL | Description |
|-----|-------------|
| **http://localhost:8501** | Local access (this computer) |
| **http://192.168.100.54:8501** | Network access (other devices on same network) |

### Quick Commands Reference

| Action | Command |
|--------|---------|
| Start server | `streamlit run tracking_app/app.py --server.port 8501` |
| Stop server | Press `Ctrl+C` in the terminal |
| Use different port | `streamlit run tracking_app/app.py --server.port 8502` |
| Run in background | `streamlit run tracking_app/app.py --server.port 8501 &` |

### Troubleshooting the Localhost

**"Port 8501 already in use"**

```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or find and kill specific process
lsof -i :8501
kill -9 <PID>
```

**"Module not found" errors**

```bash
# Ensure you're in the correct directory
cd "/home/ramplestiltski/Documents/a_tracking>system/project tracking system/tracking-system"

# Reinstall dependencies
pip install -r requirements.txt
```

**Browser doesn't open automatically**

- Manually open your browser
- Type `http://localhost:8501` in the address bar
- Press Enter

### One-Liner Quick Start

For fastest startup, copy and paste this entire command:

```bash
cd "/home/ramplestiltski/Documents/a_tracking>system/project tracking system/tracking-system" && streamlit run tracking_app/app.py --server.port 8501 && xdg-open http://localhost:8501
```

---

## §5 Troubleshooting

### "Git is not recognized"

**Solution:** Install Git from [git-scm.com](https://git-scm.com/) and restart VS Code.

### "Python is not recognized"

**Solution:** 
- Install Python from [python.org](https://www.python.org/)
- On Windows, check "Add Python to PATH" during installation
- Restart VS Code after installation

### "Port 5501 already in use"

**Solution:**
```bash
# Find and kill the process using the port
# On Linux/Mac:
lsof -i :5501
kill -9 <PID>

# On Windows:
netstat -ano | findstr :5501
taskkill /PID <PID> /F
```

### "Port 8501 already in use" (Streamlit)

**Solution:**
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use a different port
streamlit run run_system.py --server.port=8502
```

### "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### "Can't login to admin interface"

**Solution:**
```bash
# Reset the admin user
python3 force_admin_reset.py
```

### Live Server not working

**Solution:**
1. Install the Live Server extension in VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Live Server"
4. Click Install

---

## §6 Quick Reference

### Essential Files

| File | Purpose |
|------|---------|
| `veryfyn.code-workspace` | VS Code workspace file (double-click to open) |
| `index.html` | Main HTML entry point |
| `run_system.py` | Python backend entry point |
| `requirements.txt` | Python dependencies |

### Key Directories

| Directory | Contents |
|-----------|----------|
| `js/` | JavaScript modules |
| `css/` | Stylesheets |
| `brain/` | Python AI Brain system |
| `docs/` | Documentation |

### Common Commands

```bash
# Clone repository
git clone https://github.com/Rstiltski/tracking-system.git

# Open in VS Code
code veryfyn.code-workspace

# Install Python dependencies
pip install -r requirements.txt

# Run full system
python3 run_system.py

# Run tests
python -m pytest brain/immune/tests/
```

### Ports

| Service | Port |
|---------|------|
| Live Server | 5501 |
| Streamlit (Full System) | 8501 |

---

## 📚 Next Steps

After opening the project:

1. Read [GETTING_STARTED.md](GETTING_STARTED.md) for a full overview
2. Check [PROJECT_RULES.md](PROJECT_RULES.md) for coding standards
3. See [FEATURE_MAP.md](FEATURE_MAP.md) to find specific features
4. Review [README.md](README.md) for complete documentation

---

**Made with ❤️ for the Veryfyn project**