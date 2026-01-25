---

Perfect — now I’ll give you a **STEP-BY-STEP FULL SETUP GUIDE** for this exact architecture on **Windows 11** 💻🔥
(Django + MySQL + MongoDB Atlas + Redis + Celery + Nginx + Ngrok + Security)

We’ll go layer by layer.

---

# 🧩 PART 1 — DJANGO + MYSQL (Core App)

### 1️⃣ Activate Virtual Environment

```bash
.venv\\Scripts\\activate
```

### 2️⃣ Install Required Packages

```bash
pip install django mysqlclient pymongo python-decouple redis celery gunicorn
```

---

### 3️⃣ `.env` File (Project Root)

```env
SECRET\_KEY=your\_secret\_key
DEBUG=False

DB\_NAME=shopease\_db
DB\_USER=shopease\_user
DB\_PASSWORD=yourpassword
DB\_HOST=127.0.0.1
DB\_PORT=3306

MONGO\_URI=mongodb+srv://username:password@cluster.mongodb.net/

EMAIL\_HOST\_USER=your\_email@gmail.com
EMAIL\_HOST\_PASSWORD=your\_email\_password
```

---

### 4️⃣ MySQL Database Config

`settings.py`

```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB\_NAME'),
        'USER': config('DB\_USER'),
        'PASSWORD': config('DB\_PASSWORD'),
        'HOST': config('DB\_HOST'),
        'PORT': config('DB\_PORT'),
    }
}
```

Run:

```bash
python manage.py migrate
```

---

# 🧩 PART 2 — MONGODB ATLAS (Logs \& Flexible Data)

### Create `mongo.py`

```python
from pymongo import MongoClient
from decouple import config

client = MongoClient(config("MONGO\_URI"))
mongo\_db = client\["shopease\_logs"]
```

### Example usage

```python
from .mongo import mongo\_db

def log\_activity(user\_id, action):
    mongo\_db.activity.insert\_one({
        "user\_id": user\_id,
        "action": action
    })
```

---

# 🧩 PART 3 — REDIS (WSL)

Open **Ubuntu (WSL)**:

```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

Test:

```bash
redis-cli ping
# PONG
```

---

### Django Redis Cache

```python
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}
```

---

# 🧩 PART 4 — CELERY (Background Tasks)

### `shopease/celery.py`

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO\_SETTINGS\_MODULE', 'shopease.settings')
app = Celery('shopease')
app.config\_from\_object('django.conf:settings', namespace='CELERY')
app.autodiscover\_tasks()
```

### `shopease/\_\_init\_\_.py`

```python
from .celery import app as celery\_app
\_\_all\_\_ = ('celery\_app',)
```

### `settings.py`

```python
CELERY\_BROKER\_URL = 'redis://127.0.0.1:6379/0'
```

### Run worker

```bash
celery -A shopease worker --loglevel=info
```

---

# 🧩 PART 5 — GUNICORN (App Server)

```bash
gunicorn shopease.wsgi:application --bind 127.0.0.1:8000
```

---

# 🧩 PART 6 — NGINX (WSL Reverse Proxy)

In WSL:

```bash
sudo apt install nginx
sudo nano /etc/nginx/sites-available/default
```

Replace server block:

```nginx
server {
    listen 80;

    location / {
        proxy\_pass http://127.0.0.1:8000;
        proxy\_set\_header Host $host;
        proxy\_set\_header X-Real-IP $remote\_addr;
    }
}
```

Restart:

```bash
sudo service nginx restart
```

---

# 🧩 PART 7 — NGROK (Public HTTPS)

### Start Django

```bash
python manage.py runserver 0.0.0.0:8000
```

### Start Ngrok

```bash
ngrok http 8000
```

Use the HTTPS URL generated 🌍

---

# 🔒 PART 8 — SECURITY HARDENING

Add in `settings.py`:

```python
DEBUG = False
ALLOWED\_HOSTS = \['.ngrok-free.app']

SESSION\_COOKIE\_SECURE = True
CSRF\_COOKIE\_SECURE = True
SECURE\_SSL\_REDIRECT = True
SECURE\_BROWSER\_XSS\_FILTER = True
SECURE\_CONTENT\_TYPE\_NOSNIFF = True
X\_FRAME\_OPTIONS = 'DENY'
```

Change admin URL:

```python
path('secure-admin-portal/', admin.site.urls)
```

---

# 🚀 HOW TO RUN EVERYTHING TOGETHER

### Terminal 1

```bash
python manage.py runserver 0.0.0.0:8000
```

### Terminal 2

```bash
celery -A shopease worker --loglevel=info
```

### Terminal 3

```bash
ngrok http 8000
```

### (WSL)

```bash
sudo service redis-server start
sudo service nginx start
```

---

# ✅ YOU NOW HAVE

✔ Multi-database backend
✔ Background task system
✔ Caching layer
✔ Reverse proxy
✔ HTTPS public URL
✔ Security protections

All running locally like a real production system 🔥

---

If you want next, I’ll give you
👉 **Django middleware to log every user action into MongoDB automatically**
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Got it — you want to know **how to install WSL (Windows Subsystem for Linux)** on Windows 11 💻🐧
This is needed so you can run **Redis and Nginx**.

Follow these exact steps 👇

---

# 🧩 STEP 1 — Enable WSL in Windows

### 1️⃣ Open **PowerShell as Administrator**

Press:

```
Start Menu → type "PowerShell" → Right-click → Run as Administrator
```

### 2️⃣ Run this command:

```powershell
wsl --install
```

This will:
✔ Enable WSL feature
✔ Install Virtual Machine Platform
✔ Download **Ubuntu Linux**
✔ Set WSL version 2

---

# 🔄 STEP 2 — Restart Your Computer

After installation, Windows will ask to restart.
Restart your PC.

---

# 🐧 STEP 3 — Set Up Ubuntu

After restart:

1. Ubuntu window opens automatically
2. It will say:

```
   Installing, this may take a few minutes...
   ```

3. Then it will ask:

```
   Enter new UNIX username:
   ```

   👉 Choose any username (example: `prathamesh`)

4. Then set a password (Linux password — separate from Windows)

   Now Ubuntu is ready ✅

   ---

   # 🧪 STEP 4 — Test WSL is Working

   Open **Command Prompt** and type:

   ```bash
   wsl
   ```

   You should see something like:

   ```
   prathamesh@DESKTOP-XXXX:~$
   ```

   That means Linux is running inside Windows 🎉

   ---

   # 🧱 STEP 5 — Update Ubuntu Packages

   Inside the Ubuntu terminal, run:

   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

   ---

   # 🔴 STEP 6 — Install Redis (Inside WSL)

   ```bash
   sudo apt install redis-server -y
   sudo service redis-server start
   ```

   Test:

   ```bash
   redis-cli ping
   ```

   You should get:

   ```
   PONG
   ```

   ---

   # 🌐 STEP 7 — Install Nginx (Inside WSL)

   ```bash
   sudo apt install nginx -y
   sudo service nginx start
   ```

   Open browser and go to:

   ```
   http://localhost
   ```

   You should see **Welcome to nginx!**

   ---

   # 🧠 How WSL Works (Simple)

   WSL is:
   ✔ A lightweight Linux system
   ✔ Running inside Windows
   ✔ Used to run server tools (Redis, Nginx)

   It does **NOT** replace Windows
   It runs like an app

   ---

   # ✅ Final Check

|Tool|Where it runs|
|-|-|
|Django|Windows|
|MySQL|Windows|
|Redis|WSL|
|Nginx|WSL|
|Celery|Windows|

---

Once WSL is installed, tell me — next we’ll connect **Redis to Celery** 🔥

