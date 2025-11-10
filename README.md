# 🎓 SmartCareer - AI-Powered Career Guidance Platform

## 📋 Overview
SmartCareer is an intelligent career guidance platform that helps students and professionals discover their ideal career path through AI-powered assessments, personalized recommendations, and interactive mentoring.

## ✨ Features

### 🏠 Home Page
- Modern hero section with gradient banner
- Quick access to Quiz and AI Chatbot
- Testimonials and success stories
- Responsive navigation

### 📝 Career Assessment Quiz
- Dynamic multiple-choice questions
- Real-time progress tracking
- Personalized career recommendations
- Compatibility scoring

### 🤖 AI Chatbot Mentor
- Interactive chat interface
- Career guidance and counseling
- Course recommendations
- College and scholarship information

### 📊 Dashboard
- Personalized career recommendations
- Progress tracking
- Resume builder access
- Learning roadmap

### 🗺️ Career Roadmap
- Step-by-step learning paths
- Skill requirements
- Resource recommendations
- Timeline estimation

### 📄 Resume Builder
- AI-powered resume generation
- Professional templates
- Download in PDF format

## 🛠️ Tech Stack

### Frontend
- HTML5
- Tailwind CSS
- JavaScript (Vanilla)
- Chart.js (visualizations)
- AOS.js (animations)

### Backend
- Flask (Python)
- In-Memory Storage (Session-based)
- Scikit-learn (ML)
- Pandas (Data processing)

### APIs & Libraries
- Flask-CORS
- Werkzeug (Security)
- JSON for data handling

## 📁 Project Structure

```
smartcareer/
├── app.py                      # Main Flask application
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   ├── main.js            # Main JavaScript
│   │   ├── quiz.js            # Quiz functionality
│   │   └── chatbot.js         # Chatbot interface
│   └── images/                # Image assets
├── templates/
│   ├── index.html             # Home page
│   ├── quiz.html              # Quiz interface
│   ├── chatbot.html           # Chatbot page
│   ├── results.html           # Quiz results
│   ├── dashboard.html         # User dashboard
│   ├── roadmap.html           # Career roadmap
│   ├── login.html             # Login page
│   └── register.html          # Registration page
├── models/
│   └── recommendation_model.pkl  # ML model (to be trained)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd smartcareer
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: No Database Setup Required
This application uses in-memory storage (sessions and dictionaries), so no database configuration is needed!

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 📱 Usage

### For Students
1. **Register/Login** - Create your account
2. **Take the Quiz** - Answer questions about your interests and skills
3. **Get Recommendations** - Receive AI-powered career suggestions
4. **Explore Roadmap** - View personalized learning paths
5. **Chat with AI** - Get instant career guidance
6. **Build Resume** - Create professional resume

### For Developers
1. Clone and setup the project
2. Modify templates in `templates/` folder
3. Add custom styles in `static/css/`
4. Extend Flask routes in `app.py`
5. Train custom ML model for better predictions

## 🎯 Roadmap

### Phase 1: ✅ Core Development
- [x] Project setup
- [x] Flask backend
- [x] Basic frontend
- [x] Database schema

### Phase 2: 🔄 Feature Implementation
- [x] Quiz module
- [x] Chatbot integration
- [x] User authentication
- [ ] ML model training

### Phase 3: 🔜 Advanced Features
- [ ] Resume builder
- [ ] Job trends API
- [ ] Voice interaction
- [ ] Mobile app

### Phase 4: 🚀 Deployment
- [ ] Frontend deployment (Netlify)
- [ ] Backend deployment (Render/Heroku)
- [ ] Optional: Add database for data persistence
- [ ] Domain setup

## 🤝 Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Team
- **Developer**: Your Name
- **Project Type**: Career Guidance Platform
- **Version**: 1.0.0

## 📞 Contact
- Email: your.email@example.com
- GitHub: @yourusername
- LinkedIn: /in/yourprofile

## 🙏 Acknowledgments
- Tailwind CSS for the UI framework
- Flask community for excellent documentation
- All open-source contributors

## 🔒 Security
- Passwords are hashed using Werkzeug
- Session management via Flask
- In-memory storage (data persists only during runtime)
- CORS enabled for API security

**Note:** Data is stored in memory and will be reset when the server restarts. For production, consider adding database integration.

## 📈 Future Enhancements
- Integration with OpenAI GPT for advanced chatbot
- Real-time job market data
- Video resume feature
- Peer mentoring platform
- Mobile application (React Native)
- Alumni network integration

---

**Made with ❤️ for students pursuing their dream careers**
