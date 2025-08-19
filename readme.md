# MoSPI Smart Survey Tool - Deployment Guide

## 🚀 Quick Deployment Options

### Option 1: Streamlit Cloud (Recommended - FREE)

**Steps:**
1. Create a GitHub repository
2. Upload these files to your repository:
   - `app.py` (main application file)
   - `requirements.txt`
   - `.streamlit/config.toml`

3. Go to [share.streamlit.io](https://share.streamlit.io)
4. Connect your GitHub account
5. Select your repository
6. Click "Deploy"
7. Your app will be live at: `https://[your-app-name].streamlit.app`

**Time to deploy:** 5-10 minutes

### Option 2: Railway (Easy - FREE tier available)

**Steps:**
1. Create account at [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Add environment variables if needed
4. Deploy automatically

### Option 3: Render (Simple - FREE tier)

**Steps:**
1. Create account at [render.com](https://render.com)
2. Connect GitHub repository
3. Choose "Web Service"
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

## 📁 Required Files Structure

```
your-repository/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md             # This file
```

## 🔧 Environment Variables (Optional)

For OpenAI integration, add:
- `OPENAI_API_KEY=your_api_key_here`

## 🌐 Sharing with Client

Once deployed, you'll get a public URL like:
- `https://your-app-name.streamlit.app` (Streamlit Cloud)
- `https://your-app-name.railway.app` (Railway)
- `https://your-app-name.onrender.com` (Render)

## 📱 Mobile Responsive

The application is fully responsive and works on:
- Desktop browsers
- Mobile phones
- Tablets

## 🔒 Security Note

This is a demo application. For production use:
- Add proper authentication
- Use secure database storage
- Implement rate limiting
- Add data encryption

## 📊 Features Available in Demo

✅ AI-powered survey generation  
✅ Manual survey builder  
✅ Interactive survey taking  
✅ Real-time data validation  
✅ Analytics dashboard  
✅ Adaptive questioning  
✅ Auto-classification  
✅ Quality scoring  

## 💡 Usage Tips

1. **For Survey Administrators:** Use the Survey Builder to create new surveys
2. **For Testing:** Use the "Take Survey" section to experience the user journey
3. **For Analytics:** Check the Analytics dashboard after completing surveys
4. **For Validation:** Try the Validation Demo to see data quality features

## 🎯 Demo Scenarios

**Scenario 1: Survey Creation**
- Go to Survey Builder → AI Generator
- Enter: "Create a census survey for urban households"
- Generate and save the survey

**Scenario 2: Data Collection**
- Go to Take Survey
- Complete the sample survey
- Experience adaptive questions

**Scenario 3: Analytics**
- Go to Analytics Dashboard
- View response patterns and quality metrics

## 📞 Support

For questions about the survey tool or deployment, contact your development team.

---

**Deployment Checklist:**
- [ ] Repository created
- [ ] Files uploaded
- [ ] Platform selected
- [ ] App deployed
- [ ] URL shared with client
- [ ] Demo scenarios tested