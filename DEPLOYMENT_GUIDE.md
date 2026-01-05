# 🌐 Deploying Tower Descent Simulation Online

## Quick Answer: Best & Easiest Options

### **🥇 RECOMMENDED: Render.com (FREE)**
- ✅ **100% Free** (for hobby projects)
- ✅ **No credit card required**
- ✅ **Automatic HTTPS**
- ✅ **Easy deployment** (connects to GitHub)
- ✅ **Custom domain** support (optional)
- ⏱️ Setup time: **15-20 minutes**

### **🥈 Alternative: PythonAnywhere (FREE)**
- ✅ **Free tier** available
- ✅ **Good for Python/Flask apps**
- ✅ **Easy setup**
- ⚠️ Custom domain requires paid plan
- ⏱️ Setup time: **20-30 minutes**

### **🥉 Quick Test: ngrok (FREE)**
- ✅ **Instant sharing** (temporary)
- ✅ **No signup** for basic use
- ✅ **Perfect for testing** with friends
- ⚠️ URL changes each time
- ⚠️ Not permanent
- ⏱️ Setup time: **5 minutes**

---

## 📋 Option 1: Render.com (BEST FOR PERMANENT HOSTING)

### **Step-by-Step:**

#### **1. Prepare Your Files**

Create a `requirements.txt` file:
```bash
# in your game folder, create requirements.txt
cd your_game_folder
echo "Flask==3.0.0" > requirements.txt
echo "reportlab==4.0.9" >> requirements.txt
```

Create a `render.yaml` file (tells Render how to run your app):
```yaml
services:
  - type: web
    name: mha-roguelike
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app_full.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

Update `app_full.py` last line to:
```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

#### **2. Create GitHub Repository**

```bash
# initialize git in your game folder
git init
git add .
git commit -m "Initial commit"

# create repo on github.com (click "New Repository")
# then connect it
git remote add origin https://github.com/yourusername/mha-roguelike.git
git branch -M main
git push -u origin main
```

#### **3. Deploy on Render**

1. Go to https://render.com
2. Sign up (free, use GitHub account)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Fill in settings:
   - **Name:** mha-roguelike (or whatever you want)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app_full.py`
6. Click "Create Web Service"
7. Wait 3-5 minutes for deployment

#### **4. Your Game is Live!**

You'll get a URL like: `https://mha-roguelike.onrender.com`

Share this URL with anyone! ✅

---

## 📋 Option 2: PythonAnywhere (ALTERNATIVE)

### **Step-by-Step:**

#### **1. Sign Up**
- Go to https://www.pythonanywhere.com
- Create free account ("Beginner" plan)

#### **2. Upload Files**
1. Click "Files" tab
2. Create folder: `/home/yourusername/mha_game`
3. Upload all your files:
   - `app_full.py`
   - `mha_roguelike_complete.py`
   - `homepage.html`
   - `templates/game.html`
   - `static/css/style.css`
   - `static/js/game_full.js`
   - All images

#### **3. Set Up Web App**
1. Click "Web" tab
2. "Add a new web app"
3. Choose "Flask"
4. Python version: 3.10
5. Set path to: `/home/yourusername/mha_game/app_full.py`

#### **4. Configure WSGI**
Edit the WSGI configuration file:
```python
import sys
path = '/home/yourusername/mha_game'
if path not in sys.path:
    sys.path.append(path)

from app_full import app as application
```

#### **5. Reload and Go Live**
Click "Reload" button

Your URL: `https://yourusername.pythonanywhere.com`

---

## 📋 Option 3: ngrok (QUICK TEST/DEMO)

### **Instant Sharing (Temporary):**

#### **1. Download ngrok**
- Go to https://ngrok.com/download
- Download for your OS
- Extract to a folder

#### **2. Run Your Game Locally**
```bash
python app_full.py
```

#### **3. In Another Terminal, Run ngrok**
```bash
cd /path/to/ngrok
./ngrok http 5000
```

#### **4. Share the URL**
ngrok will show you a URL like:
```
https://abc123.ngrok.io
```

**Anyone can visit this URL** to play your game! 🎮

**Note:** This URL expires when you close ngrok. Good for quick demos.

---

## 📋 Option 4: Heroku (Used to be free, now $5/month minimum)

If you're willing to pay $5/month:

### **Files Needed:**

**Procfile:**
```
web: python app_full.py
```

**requirements.txt:**
```
Flask==3.0.0
reportlab==4.0.9
gunicorn==21.2.0
```

**runtime.txt:**
```
python-3.11.0
```

### **Deploy:**
```bash
heroku login
heroku create mha-roguelike
git push heroku main
heroku open
```

Your URL: `https://mha-roguelike.herokuapp.com`

---

## 🎯 Comparison Table

| Service | Cost | Setup | Custom Domain | Permanent | Best For |
|---------|------|-------|---------------|-----------|----------|
| **Render** | Free | Medium | Yes (free) | Yes | Public release |
| **PythonAnywhere** | Free | Medium | Paid only | Yes | Python devs |
| **ngrok** | Free | Easy | No | No | Quick tests |
| **Heroku** | $5/mo | Medium | Yes | Yes | Serious projects |
| **Vercel** | Free | Hard* | Yes (free) | Yes | If you know Node |

*Vercel is Node-focused; Flask needs workarounds

---

## 💡 My Recommendation

### **For You (Beginner + Want Free + Want Permanent):**

**Use Render.com** because:
1. ✅ Completely free
2. ✅ No credit card needed
3. ✅ Easy GitHub integration
4. ✅ Automatic HTTPS
5. ✅ Your URL never changes
6. ✅ Can add custom domain later
7. ✅ Built for Flask/Python

### **Setup Time Breakdown:**
- Create GitHub repo: 5 minutes
- Create Render account: 2 minutes
- Connect & deploy: 5 minutes
- Wait for build: 3-5 minutes
- **Total: ~15-20 minutes**

---

## 📝 Quick Start Guide (Render)

```bash
# 1. add these files to your project
echo "Flask==3.0.0" > requirements.txt
echo "reportlab==4.0.9" >> requirements.txt

# 2. create .gitignore
echo "__pycache__/" > .gitignore
echo "*.pyc" >> .gitignore

# 3. initialize git
git init
git add .
git commit -m "Deploy to Render"

# 4. create github repo (on github.com)
# 5. push to github
git remote add origin YOUR_GITHUB_URL
git push -u origin main

# 6. go to render.com
# 7. new web service
# 8. connect github repo
# 9. deploy

# done you are live
```

---

## 🔧 Troubleshooting

### **"Module not found" errors:**
- Make sure `requirements.txt` is in your root folder
- Check that all imports in your code match installed packages

### **"Application failed to start":**
- Check Render logs (click "Logs" tab)
- Verify `app_full.py` has `if __name__ == '__main__': app.run()`

### **"Port already in use":**
- Change port in code or kill the process using port 5000

### **Static files not loading:**
- Make sure `/static` folder is in your git repo
- Check Render logs for 404 errors

---

## 🌐 Custom Domain (Optional)

### **After deploying to Render:**

1. Buy domain from Namecheap/GoDaddy (~$12/year)
2. In Render dashboard, click "Settings"
3. "Custom Domains" → "Add Custom Domain"
4. Enter your domain (e.g., `mha-game.com`)
5. Update DNS at your domain provider:
   - Add CNAME record pointing to your Render URL

Done! Your game at `https://yourgame.com` ✅

---

## 📊 Expected Costs

| Hosting | Free Tier | Paid Tier | Custom Domain |
|---------|-----------|-----------|---------------|
| Render | ✅ Yes | $7/mo | Included |
| PythonAnywhere | ✅ Limited | $5/mo | Extra $$ |
| ngrok | ✅ Temp | $8/mo | With paid |
| Heroku | ❌ No | $5/mo | Included |
| Domain Name | - | - | ~$12/year |

---

## 🎮 After Deployment

### **Share Your Game:**
1. Post URL on social media
2. Add to your portfolio
3. Share with MHA communities
4. Get feedback!

### **Monitor:**
- Check Render dashboard for uptime
- Read logs if issues arise
- Update code via git push

### **Update Game:**
```bash
# make changes to your code
git add .
git commit -m "Updated features"
git push

# render auto deploys changes
```

---

## ✅ Final Checklist

Before going live:
- [ ] Test game locally (all features work)
- [ ] Create requirements.txt
- [ ] Push to GitHub
- [ ] Deploy to Render
- [ ] Test deployed version
- [ ] Share URL!

---

**🎉 You're ready to share your game with the world!**

Questions? The Render.com documentation is excellent: https://render.com/docs
