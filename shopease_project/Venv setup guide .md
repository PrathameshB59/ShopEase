# VIRTUAL ENVIRONMENT SETUP GUIDE
===================================

## 🎯 COMPLETE VIRTUAL ENVIRONMENT WORKFLOW

This guide will help you set up a virtual environment for your ShopEase project safely.

---

## 📋 STEP 1: CREATE VIRTUAL ENVIRONMENT

### **Windows (Your System):**

```bash
# Navigate to your project
cd C:\Users\Prathmesh D Birajdar\OneDrive\Desktop\ShopEase\shopease_project

# Create virtual environment named 'venv'
python -m venv venv
```

**What happens:**
- Creates a `venv` folder in your project
- Contains isolated Python installation
- Keeps your system Python clean

---

## 📋 STEP 2: ACTIVATE VIRTUAL ENVIRONMENT

### **Windows Command Prompt:**
```bash
venv\Scripts\activate
```

### **Windows PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

### **If PowerShell gives error:**
```bash
# Run this first (one time only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
venv\Scripts\Activate.ps1
```

### **Git Bash (if using):**
```bash
source venv/Scripts/activate
```

### **Success Indicator:**
```bash
(venv) C:\Users\...\shopease_project>
 ^^^^
 This means it's ACTIVE!
```

---

## 📋 STEP 3: INSTALL PACKAGES FROM requirements.txt

### **With virtual environment ACTIVE:**

```bash
# Install all packages at once
pip install -r requirements.txt
```

**What this does:**
- ✅ Installs Django 5.2.4
- ✅ Installs Pillow 11.3.0 (for images)
- ✅ Installs all other dependencies
- ✅ Creates isolated environment

### **To verify installation:**
```bash
pip list
```

**You should see:**
```
Package         Version
--------------- -------
Django          5.2.4
Pillow          11.3.0
...
```

---

## 📋 STEP 4: DEACTIVATE VIRTUAL ENVIRONMENT (When Done)

```bash
deactivate
```

**You'll see:**
```bash
C:\Users\...\shopease_project>
(no more (venv) prefix)
```

---

## 🎯 DAILY WORKFLOW

### **Every Time You Work on the Project:**

```bash
# 1. Navigate to project
cd shopease_project

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Work on your project
python manage.py runserver

# 4. When done, deactivate
deactivate
```

---

## 📦 PACKAGE MANAGEMENT

### **Install New Package:**
```bash
# Make sure venv is active first!
(venv) > pip install package-name

# Add to requirements.txt
(venv) > pip freeze > requirements.txt
```

### **Update Existing Package:**
```bash
(venv) > pip install --upgrade package-name
(venv) > pip freeze > requirements.txt
```

### **Uninstall Package:**
```bash
(venv) > pip uninstall package-name
(venv) > pip freeze > requirements.txt
```

### **Update All Packages:**
```bash
(venv) > pip list --outdated
(venv) > pip install --upgrade package1 package2 package3
(venv) > pip freeze > requirements.txt
```

---

## 🔄 REGENERATE requirements.txt

### **To create fresh requirements.txt:**

```bash
# Activate venv
venv\Scripts\activate

# Generate requirements file
pip freeze > requirements.txt
```

**This captures ALL installed packages with exact versions.**

---

## 🆕 SETTING UP ON NEW MACHINE

### **When you clone project to another computer:**

```bash
# 1. Clone/copy project
cd shopease_project

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
venv\Scripts\activate

# 4. Install all dependencies
pip install -r requirements.txt

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

**Done! Project works on new machine! 🎉**

---

## 🎨 VSCODE INTEGRATION

### **Auto-activate in VSCode:**

1. **Open Command Palette:** `Ctrl + Shift + P`
2. **Type:** `Python: Select Interpreter`
3. **Select:** `./venv/Scripts/python.exe`
4. **Open new terminal:** `` Ctrl + ` ``
5. **Virtual environment auto-activates!** ✅

### **VSCode Settings (Optional):**

Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\venv\\Scripts\\python.exe",
    "python.terminal.activateEnvironment": true
}
```

---

## 📁 PROJECT STRUCTURE WITH VENV

```
ShopEase/
└── shopease_project/
    ├── venv/                    ← Virtual environment (DON'T commit to git!)
    │   ├── Scripts/
    │   ├── Lib/
    │   └── ...
    ├── accounts/
    ├── products/
    ├── orders/
    ├── static/
    ├── templates/
    ├── manage.py
    ├── requirements.txt         ← Package list (COMMIT this!)
    ├── .gitignore              ← Must include venv/
    └── db.sqlite3
```

---

## 🚫 .gitignore FILE

### **IMPORTANT: Don't commit venv to Git!**

Create `.gitignore` in project root:

```
# Virtual Environment
venv/
env/
.venv/
ENV/

# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class

# Django
*.log
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

---

## ✅ VERIFICATION CHECKLIST

After setup, verify everything works:

```bash
# Check Python location (should be in venv)
where python
# Expected: C:\...\shopease_project\venv\Scripts\python.exe

# Check pip location (should be in venv)
where pip
# Expected: C:\...\shopease_project\venv\Scripts\pip.exe

# Check Django version
python -m django --version
# Expected: 5.2.4

# Check installed packages
pip list

# Check if Django works
python manage.py check
# Expected: System check identified no issues (0 silenced).
```

---

## 🐛 TROUBLESHOOTING

### **Problem: "venv is not recognized"**
**Solution:**
```bash
python -m venv venv
```

### **Problem: "cannot be loaded because running scripts is disabled"**
**Solution:**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Problem: "pip is not recognized"**
**Solution:**
```bash
# Activate venv first
venv\Scripts\activate

# Then use pip
pip install -r requirements.txt
```

### **Problem: "Django is not installed"**
**Solution:**
```bash
# Make sure venv is active (you see (venv) prefix)
pip install django
```

### **Problem: Packages install to system instead of venv**
**Solution:**
```bash
# Deactivate and reactivate
deactivate
venv\Scripts\activate

# Verify you're in venv
where python
# Should show path in venv folder
```

---

## 🎯 QUICK REFERENCE COMMANDS

```bash
# CREATE VENV
python -m venv venv

# ACTIVATE (Windows CMD)
venv\Scripts\activate

# ACTIVATE (PowerShell)
venv\Scripts\Activate.ps1

# INSTALL REQUIREMENTS
pip install -r requirements.txt

# FREEZE CURRENT PACKAGES
pip freeze > requirements.txt

# DEACTIVATE
deactivate

# CHECK IF ACTIVE
where python

# UPDATE PIP
python -m pip install --upgrade pip
```

---

## 📊 PACKAGE VERSIONS IN requirements.txt

### **Why Specific Versions?**

```
Django==5.2.4          # Exact version (recommended)
Pillow>=11.0.0         # Minimum version
requests~=2.31.0       # Compatible release
```

**Recommended:** Use exact versions (==) for reproducibility

**Flexible:** Use >= or ~= for development

---

## 🔐 SECURITY BEST PRACTICES

1. ✅ **Always use virtual environment**
2. ✅ **Never commit venv folder to git**
3. ✅ **Keep requirements.txt updated**
4. ✅ **Regularly update packages** (security patches)
5. ✅ **Use specific versions** in production
6. ✅ **Test after updating packages**

---

## 🚀 PRODUCTION DEPLOYMENT

### **For Production Server:**

```bash
# 1. Create venv on server
python -m venv venv

# 2. Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install production requirements
pip install -r requirements.txt

# 4. Additional production packages
pip install gunicorn whitenoise

# 5. Update requirements
pip freeze > requirements.txt
```

---

## 💡 PRO TIPS

**Tip 1: Separate Dev and Production Requirements**
```
requirements.txt          # Production
requirements-dev.txt      # Development only
```

**Tip 2: Use Comments in requirements.txt**
```
# Core Framework
Django==5.2.4

# Image Processing
Pillow==11.3.0
```

**Tip 3: Automate Activation**
```bash
# Create activate.bat in project root:
@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
```

**Tip 4: Check for Outdated Packages**
```bash
pip list --outdated
```

**Tip 5: Create Multiple Virtual Environments**
```bash
python -m venv venv-dev     # Development
python -m venv venv-prod    # Production testing
python -m venv venv-test    # Testing
```

---

## 🎉 SUCCESS!

After following this guide:

✅ Virtual environment created  
✅ Packages installed from requirements.txt  
✅ Project isolated from system Python  
✅ Easy to share and deploy  
✅ Safe to experiment  
✅ Professional setup  

**You're ready to develop safely!** 🚀

---

## 📞 QUICK HELP

**Stuck?** Run this diagnostic:

```bash
# Check current directory
cd

# Check if venv exists
dir venv

# Check Python version
python --version

# Check pip version
pip --version

# Check active environment
where python
```

Send output if you need help!