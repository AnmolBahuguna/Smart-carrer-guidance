from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, Response
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv
import requests
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app)

# API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENROUTER_API_KEY = os.environ.get('OPENAI_API_KEY', '')  # Using same key for OpenRouter
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
USE_FREE_API = os.environ.get('USE_FREE_API', 'True').lower() == 'true'

# Scholarship & Opportunity APIs
NSP_API_KEY = os.environ.get('NSP_API_KEY', '')
BUDDY4STUDY_API_KEY = os.environ.get('BUDDY4STUDY_API_KEY', '')
INTERNSHALA_API_KEY = os.environ.get('INTERNSHALA_API_KEY', '')
NAUKRI_API_KEY = os.environ.get('NAUKRI_API_KEY', '')

# API Cache for performance
scholarships_cache = {'data': [], 'last_updated': None}
internships_cache = {'data': [], 'last_updated': None}
jobs_cache = {'data': [], 'last_updated': None}

# In-memory storage (replaces database)
users_storage = {}
quiz_results_storage = []
chat_history_storage = []
progress_storage = []

# API Integration Functions

def fetch_nsp_scholarships():
    """Fetch scholarships from National Scholarships Portal"""
    try:
        # Mock data for demonstration - replace with actual API call
        scholarships = [
            {
                'id': 'nsp_001',
                'title': 'Post-Matric Scholarship for OBC Students',
                'provider': 'Ministry of Social Justice and Empowerment',
                'amount': 'Up to ₹10,000 per annum',
                'eligibility': 'OBC students with family income < ₹8 lakh',
                'deadline': '2025-12-31',
                'link': 'https://scholarships.gov.in/',
                'category': 'Government',
                'state': 'All India',
                'education_level': 'Post-Matric'
            },
            {
                'id': 'nsp_002', 
                'title': 'National Merit Scholarship',
                'provider': 'Ministry of Education',
                'amount': '₹12,000 per annum',
                'eligibility': 'Meritorious students with 80%+ marks',
                'deadline': '2025-11-30',
                'link': 'https://scholarships.gov.in/',
                'category': 'Government',
                'state': 'All India',
                'education_level': 'Graduate'
            },
            {
                'id': 'nsp_003',
                'title': 'AICTE Pragati Scholarship for Girls',
                'provider': 'AICTE',
                'amount': '₹30,000 per annum + ₹2,000/month for hostel',
                'eligibility': 'Girl students in technical courses',
                'deadline': '2025-11-15',
                'link': 'https://www.aicte-india.org/',
                'category': 'Government',
                'state': 'All India',
                'education_level': 'Diploma/Degree'
            }
        ]
        return scholarships
    except Exception as e:
        print(f"Error fetching NSP scholarships: {e}")
        return []

def fetch_buddy4study_scholarships():
    """Fetch scholarships from Buddy4Study API"""
    try:
        # Mock data for demonstration - replace with actual API call
        scholarships = [
            {
                'id': 'buddy_001',
                'title': 'Tata Trusts Scholarship Program',
                'provider': 'Tata Trusts',
                'amount': 'Up to ₹60,000 per year',
                'eligibility': 'Students from economically weaker sections',
                'deadline': '2025-12-15',
                'link': 'https://www.buddy4study.com/',
                'category': 'Private',
                'state': 'All India',
                'education_level': 'Graduate'
            },
            {
                'id': 'buddy_002',
                'title': 'HDFC Educational Crisis Scholarship',
                'provider': 'HDFC Bank',
                'amount': 'Up to ₹35,000',
                'eligibility': 'Students affected by personal crises',
                'deadline': '2025-11-20',
                'link': 'https://www.buddy4study.com/',
                'category': 'Private',
                'state': 'All India',
                'education_level': 'Any'
            }
        ]
        return scholarships
    except Exception as e:
        print(f"Error fetching Buddy4Study scholarships: {e}")
        return []

def fetch_internships():
    """Fetch internships from Internshala API"""
    try:
        # Mock data for demonstration - replace with actual API call
        internships = [
            {
                'id': 'intern_001',
                'title': 'Web Development Intern',
                'company': 'TechStart Solutions',
                'location': 'Bangalore, Karnataka',
                'stipend': '₹10,000 - ₹15,000 per month',
                'duration': '3 months',
                'link': 'https://internshala.com/',
                'category': 'Web Development',
                'posted_date': '2025-10-25',
                'deadline': '2025-11-15'
            },
            {
                'id': 'intern_002',
                'title': 'Data Science Intern',
                'company': 'Analytics Pro',
                'location': 'Mumbai, Maharashtra',
                'stipend': '₹15,000 - ₹20,000 per month',
                'duration': '6 months',
                'link': 'https://internshala.com/',
                'category': 'Data Science',
                'posted_date': '2025-10-24',
                'deadline': '2025-11-10'
            },
            {
                'id': 'intern_003',
                'title': 'Digital Marketing Intern',
                'company': 'GrowthHackers',
                'location': 'Remote',
                'stipend': '₹8,000 - ₹12,000 per month',
                'duration': '2 months',
                'link': 'https://internshala.com/',
                'category': 'Marketing',
                'posted_date': '2025-10-23',
                'deadline': '2025-11-05'
            }
        ]
        return internships
    except Exception as e:
        print(f"Error fetching internships: {e}")
        return []

def fetch_fresher_jobs():
    """Fetch fresher jobs from Naukri API"""
    try:
        # Mock data for demonstration - replace with actual call
        jobs = [
            {
                'id': 'job_001',
                'title': 'Junior Software Developer',
                'company': 'InnovateTech Solutions',
                'location': 'Pune, Maharashtra',
                'salary': '₹4,00,000 - ₹6,00,000 per annum',
                'experience': '0-1 years',
                'link': 'https://www.naukri.com/',
                'category': 'Software Development',
                'posted_date': '2025-10-25',
                'skills': ['Python', 'JavaScript', 'SQL']
            },
            {
                'id': 'job_002',
                'title': 'Trainee Business Analyst',
                'company': 'DataDriven Corp',
                'location': 'Hyderabad, Telangana',
                'salary': '₹3,50,000 - ₹5,00,000 per annum',
                'experience': '0-1 years',
                'link': 'https://www.naukri.com/',
                'category': 'Business Analysis',
                'posted_date': '2025-10-24',
                'skills': ['Excel', 'SQL', 'Communication']
            },
            {
                'id': 'job_003',
                'title': 'Content Writer (Fresher)',
                'company': 'Creative Minds Agency',
                'location': 'Delhi NCR',
                'salary': '₹2,50,000 - ₹4,00,000 per annum',
                'experience': '0-1 years',
                'link': 'https://www.naukri.com/',
                'category': 'Content Writing',
                'posted_date': '2025-10-23',
                'skills': ['Content Writing', 'SEO', 'English']
            }
        ]
        return jobs
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []

def should_update_cache(last_updated, cache_duration_hours=1):
    """Check if cache should be updated"""
    if not last_updated:
        return True
    update_time = datetime.fromisoformat(last_updated) + timedelta(hours=cache_duration_hours)
    return datetime.now() > update_time

def get_scholarships():
    """Get scholarships with caching"""
    global scholarships_cache
    
    if should_update_cache(scholarships_cache['last_updated']):
        print("Updating scholarships cache...")
        nsp_scholarships = fetch_nsp_scholarships()
        buddy_scholarships = fetch_buddy4study_scholarships()
        
        all_scholarships = nsp_scholarships + buddy_scholarships
        
        # Sort by deadline (urgent first)
        all_scholarships.sort(key=lambda x: x.get('deadline', '9999-12-31'))
        
        scholarships_cache['data'] = all_scholarships
        scholarships_cache['last_updated'] = datetime.now().isoformat()
    
    return scholarships_cache['data']

def get_internships():
    """Get internships with caching"""
    global internships_cache
    
    if should_update_cache(internships_cache['last_updated']):
        print("Updating internships cache...")
        internships_data = fetch_internships()
        
        # Sort by posted date (newest first)
        internships_data.sort(key=lambda x: x.get('posted_date', ''), reverse=True)
        
        internships_cache['data'] = internships_data
        internships_cache['last_updated'] = datetime.now().isoformat()
    
    return internships_cache['data']

def get_jobs():
    """Get jobs with caching"""
    global jobs_cache
    
    if should_update_cache(jobs_cache['last_updated']):
        print("Updating jobs cache...")
        jobs_data = fetch_fresher_jobs()
        
        # Sort by posted date (newest first)
        jobs_data.sort(key=lambda x: x.get('posted_date', ''), reverse=True)
        
        jobs_cache['data'] = jobs_data
        jobs_cache['last_updated'] = datetime.now().isoformat()
    
    return jobs_cache['data']

# Routes
@app.route('/')
def index():
    """Home page - Clean SmartCareer UI"""
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    """Quiz page"""
    return render_template('quiz.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    """Process quiz submission and predict career"""
    try:
        data = request.get_json()
        answers = data.get('answers', {})
        
        # Process quiz answers
        career_recommendations = predict_career(answers)
        
        # Save to session and in-memory storage
        session['quiz_results'] = {
            'answers': answers,
            'predicted_career': career_recommendations[0]['career'],
            'score': career_recommendations[0]['score'],
            'recommendations': career_recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
        # Store in memory if user is logged in
        if 'user_email' in session:
            quiz_results_storage.append({
                'user_email': session['user_email'],
                'answers': answers,
                'recommendations': career_recommendations,
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'recommendations': career_recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def predict_career(answers):
    """Predict career based on quiz answers"""
    # This is a simplified version. Replace with actual ML model
    # For now, using rule-based logic
    
    interests = answers.get('interests', [])
    skills = answers.get('skills', [])
    personality = answers.get('personality', '')
    
    career_scores = {
        'Software Developer': 0,
        'Data Scientist': 0,
        'UX/UI Designer': 0,
        'Digital Marketing': 0,
        'Business Analyst': 0,
        'Cybersecurity Expert': 0,
        'AI/ML Engineer': 0,
        'Content Writer': 0,
        'Product Manager': 0,
        'Cloud Architect': 0
    }
    
    # Scoring logic based on interests
    interest_mapping = {
        'technology': ['Software Developer', 'Data Scientist', 'AI/ML Engineer', 'Cybersecurity Expert'],
        'creative': ['UX/UI Designer', 'Content Writer', 'Digital Marketing'],
        'business': ['Business Analyst', 'Product Manager', 'Digital Marketing'],
        'analytics': ['Data Scientist', 'Business Analyst', 'AI/ML Engineer'],
        'design': ['UX/UI Designer', 'Product Manager'],
        'communication': ['Digital Marketing', 'Content Writer', 'Product Manager']
    }
    
    for interest in interests:
        if interest.lower() in interest_mapping:
            for career in interest_mapping[interest.lower()]:
                career_scores[career] += 20
    
    # Scoring based on skills
    skill_mapping = {
        'programming': ['Software Developer', 'AI/ML Engineer', 'Data Scientist'],
        'design': ['UX/UI Designer'],
        'writing': ['Content Writer', 'Digital Marketing'],
        'mathematics': ['Data Scientist', 'AI/ML Engineer', 'Business Analyst'],
        'problemsolving': ['Software Developer', 'Cybersecurity Expert', 'Cloud Architect']
    }
    
    for skill in skills:
        skill_key = skill.lower().replace(' ', '').replace('-', '')
        if skill_key in skill_mapping:
            for career in skill_mapping[skill_key]:
                career_scores[career] += 15
    
    # Sort careers by score
    sorted_careers = sorted(career_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return top 3 recommendations
    recommendations = []
    for i, (career, score) in enumerate(sorted_careers[:3]):
        recommendations.append({
            'rank': i + 1,
            'career': career,
            'score': min(score, 100),  # Cap at 100
            'description': get_career_description(career),
            'skills_needed': get_career_skills(career),
            'avg_salary': get_career_salary(career)
        })
    
    return recommendations

def get_career_description(career):
    descriptions = {
        'Software Developer': 'Design, develop, and maintain software applications and systems.',
        'Data Scientist': 'Analyze complex data to help companies make better decisions.',
        'UX/UI Designer': 'Create intuitive and beautiful user interfaces for digital products.',
        'Digital Marketing': 'Promote products and brands through digital channels.',
        'Business Analyst': 'Analyze business processes and recommend improvements.',
        'Cybersecurity Expert': 'Protect organizations from cyber threats and attacks.',
        'AI/ML Engineer': 'Develop intelligent systems using artificial intelligence and machine learning.',
        'Content Writer': 'Create engaging written content for various platforms.',
        'Product Manager': 'Lead product development from conception to launch.',
        'Cloud Architect': 'Design and manage cloud computing infrastructure.'
    }
    return descriptions.get(career, 'Exciting career opportunity')

def get_career_skills(career):
    skills = {
        'Software Developer': ['Python', 'JavaScript', 'Git', 'Problem Solving'],
        'Data Scientist': ['Python', 'Statistics', 'Machine Learning', 'SQL'],
        'UX/UI Designer': ['Figma', 'Adobe XD', 'Design Thinking', 'Prototyping'],
        'Digital Marketing': ['SEO', 'Content Marketing', 'Social Media', 'Analytics'],
        'Business Analyst': ['SQL', 'Excel', 'Data Analysis', 'Communication'],
        'Cybersecurity Expert': ['Network Security', 'Ethical Hacking', 'Security Protocols'],
        'AI/ML Engineer': ['Python', 'TensorFlow', 'Deep Learning', 'Mathematics'],
        'Content Writer': ['Writing', 'SEO', 'Research', 'Creativity'],
        'Product Manager': ['Strategy', 'Agile', 'Communication', 'Analytics'],
        'Cloud Architect': ['AWS', 'Azure', 'Cloud Security', 'DevOps']
    }
    return skills.get(career, [])

def get_career_salary(career):
    salaries = {
        'Software Developer': '$75,000 - $120,000',
        'Data Scientist': '$85,000 - $140,000',
        'UX/UI Designer': '$65,000 - $110,000',
        'Digital Marketing': '$50,000 - $90,000',
        'Business Analyst': '$65,000 - $100,000',
        'Cybersecurity Expert': '$80,000 - $130,000',
        'AI/ML Engineer': '$90,000 - $150,000',
        'Content Writer': '$40,000 - $70,000',
        'Product Manager': '$85,000 - $140,000',
        'Cloud Architect': '$95,000 - $160,000'
    }
    return salaries.get(career, '$50,000 - $100,000')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot conversation"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        # Get chatbot response
        bot_response = get_chatbot_response(user_message)
        
        # Save to in-memory storage
        chat_entry = {
            'message': user_message,
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        }
        
        if 'user_email' in session:
            chat_entry['user_email'] = session['user_email']
        
        chat_history_storage.append(chat_entry)
        
        # Also save to session
        if 'chat_history' not in session:
            session['chat_history'] = []
        session['chat_history'].append(chat_entry)
        
        return jsonify({
            'success': True,
            'response': bot_response
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Handle streaming chatbot conversation for real-time responses"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        def generate():
            try:
                # Try OpenAI streaming first
                if OPENAI_API_KEY and not USE_FREE_API:
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=OPENAI_API_KEY)
                        
                        system_prompt = """You are a helpful career guidance counselor named SmartCareer AI Mentor. 
                        Provide advice about careers, education, skills, colleges, scholarships, and professional development. 
                        Keep responses concise, actionable, and engaging. Use emojis to make responses friendly. 
                        Focus on Indian context but include global opportunities. Be encouraging and motivational."""
                        
                        stream = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_message}
                            ],
                            max_tokens=300,
                            temperature=0.7,
                            stream=True
                        )
                        
                        for chunk in stream:
                            if chunk.choices[0].delta.content:
                                yield f"data: {chunk.choices[0].delta.content}\n\n"
                        return
                        
                    except Exception as e:
                        print(f"OpenAI streaming error: {e}")
                
                # Fallback to regular response
                response = get_chatbot_response(user_message)
                yield f"data: {response}\n\n"
                
            except Exception as e:
                yield f"data: Sorry, I encountered an error: {str(e)}\n\n"
        
        return Response(generate(), mimetype='text/plain')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_chatbot_response(message):
    """Generate chatbot response using AI or rule-based system"""
    
    # Try OpenRouter/OpenAI API first if configured
    if OPENAI_API_KEY:
        try:
            return get_openai_response(message)
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fall back to rule-based
    
    # Try Gemini API as alternative
    if GEMINI_API_KEY:
        try:
            return get_gemini_response(message)
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Fall back to rule-based
    
    # Try free alternative API
    if USE_FREE_API:
        try:
            return get_free_ai_response(message)
        except Exception as e:
            print(f"Free API error: {e}")
            # Fall back to rule-based
    
    # Rule-based fallback
    return get_rule_based_response(message)

def get_openai_response(message):
    """Get response from OpenAI API with streaming support"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        system_prompt = """You are a helpful career guidance counselor named SmartCareer AI Mentor. 
        Provide advice about careers, education, skills, colleges, scholarships, and professional development. 
        Keep responses concise, actionable, and engaging. Use emojis to make responses friendly. 
        Focus on Indian context but include global opportunities. Be encouraging and motivational."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7,
            stream=False
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Try OpenRouter as fallback
        try:
            return get_openrouter_response(message)
        except:
            raise Exception(f"OpenAI API error: {str(e)}")

def get_openrouter_response(message):
    """Get response from OpenRouter API"""
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        
        system_prompt = """You are a helpful career guidance counselor named SmartCareer AI Mentor. 
        Provide advice about careers, education, skills, colleges, scholarships, and professional development. 
        Keep responses concise, actionable, and engaging. Use emojis to make responses friendly. 
        Focus on Indian context but include global opportunities. Be encouraging and motivational."""
        
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"OpenRouter API error: {str(e)}")


def get_gemini_response(message):
    """Get response from Google Gemini API"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        
        # Use a working model from the available list
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""You are a helpful career guidance counselor named SmartCareer AI Mentor. 
        Provide advice about careers, education, skills, colleges, scholarships, and professional development. 
        Keep responses concise, actionable, and engaging. Use emojis to make responses friendly. 
        Focus on Indian context but include global opportunities. Be encouraging and motivational.
        
        User: {message}
        
        Provide a helpful response:"""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

def get_free_ai_response(message):
    """Get response from rule-based system"""
    return get_rule_based_response(message)

def get_rule_based_response(message):
    """Enhanced rule-based chatbot responses with comprehensive career guidance"""
    message_lower = message.lower()
    
    # Expanded responses database
    responses = {
        # Greetings
        'hello': "Hello! 👋 I'm your AI Career Mentor from SmartCareer. I'm here to guide you through your career journey!\n\nI can help with:\n✅ Career exploration & planning\n✅ College & course recommendations\n✅ Skill development roadmaps\n✅ Interview preparation\n✅ Salary insights\n\nWhat would you like to explore today?",
        'hi': "Hi there! 😊 Welcome to SmartCareer!\n\nHow can I assist you with your career today?",
        'hey': "Hey! 🙌 I'm here to help you succeed in your career!\n\nWhat's on your mind?",
        
        # AI/ML related
        'artificial intelligence': "Artificial Intelligence is revolutionizing the world! 🤖\n\n**Career Paths:**\n• AI Research Scientist (₹20-40 LPA)\n• ML Engineer (₹15-30 LPA)\n• AI Product Manager (₹25-50 LPA)\n\n**Essential Skills:**\n• Python, TensorFlow, PyTorch\n• Deep Learning & Neural Networks\n• Mathematics (Linear Algebra, Calculus)\n• NLP & Computer Vision\n\n**Top Colleges:**\n• IIT Madras, Delhi, Bombay\n• IIIT Hyderabad\n• ISI Kolkata\n\n**Learning Resources:**\n• Andrew Ng's ML Course (Coursera)\n• Fast.ai\n• DeepLearning.AI\n\nVisit our AI/ML/Data Science section for detailed roadmap!",
        'machine learning': "Machine Learning is the future! 🧠\n\n**What You Need:**\n• Python (scikit-learn, pandas, NumPy)\n• Statistics & Probability\n• Algorithms & Data Structures\n• Math (Linear Algebra)\n\n**Career Options:**\n1. ML Engineer - ₹15-28 LPA\n2. Data Scientist - ₹12-25 LPA\n3. Research Scientist - ₹18-35 LPA\n\n**Learning Path:**\n1. Python basics (2 months)\n2. Math foundations (2 months)\n3. ML algorithms (3 months)\n4. Projects & Kaggle (ongoing)\n\n**Top Companies Hiring:**\nGoogle, Microsoft, Amazon, Netflix, Uber\n\nWant a detailed roadmap?",
        'data science': "Data Science is booming! 📊\n\n**Core Skills:**\n• Python (pandas, NumPy, matplotlib)\n• Statistics & Hypothesis Testing\n• SQL & Database Management\n• Machine Learning\n• Data Visualization (Tableau, Power BI)\n\n**Career Path:**\n• Junior Data Analyst: ₹4-8 LPA\n• Data Scientist: ₹12-20 LPA\n• Senior DS: ₹25-40 LPA\n• Lead/Principal: ₹50+ LPA\n\n**Best Colleges:**\n• IIT Madras, Bombay, Delhi\n• IIIT Hyderabad (₹32 LPA avg!)\n• ISI Kolkata\n\n**Free Resources:**\n• Google Data Analytics (Coursera)\n• Python for Data Science (edX)\n• Kaggle Learn\n\nCheck our Career Insights for latest trends!",
        
        # Engineering & Computer Science
        'software': "Software Development - Great choice! 💻\n\n**Career Options:**\n• Full Stack Developer (₹6-15 LPA)\n• Backend Engineer (₹8-20 LPA)\n• Frontend Developer (₹5-12 LPA)\n• DevOps Engineer (₹10-22 LPA)\n\n**Tech Stacks to Learn:**\n**Frontend:** HTML, CSS, JavaScript, React/Angular/Vue\n**Backend:** Node.js, Python (Django/Flask), Java (Spring)\n**Database:** SQL, MongoDB, PostgreSQL\n**Tools:** Git, Docker, AWS/Azure\n\n**Learning Path:**\n1. Choose a language (Python/JavaScript)\n2. Learn basics (3 months)\n3. Build projects (Portfolio)\n4. Learn frameworks (2 months)\n5. Deploy projects (Git, Cloud)\n\n**Top Colleges:**\n• IITs, NITs, IIIT Hyderabad\n• BITS Pilani, DTU, VIT\n\nStart with freeCodeCamp or The Odin Project!",
        'web development': "Web Development - Build the internet! 🌐\n\n**Path 1: Frontend Developer**\n• HTML, CSS, JavaScript\n• React.js or Vue.js\n• Tailwind CSS, Bootstrap\n• Responsive Design\nSalary: ₹5-12 LPA\n\n**Path 2: Backend Developer**\n• Node.js or Python (Django)\n• REST APIs, GraphQL\n• Databases (SQL, MongoDB)\n• Authentication & Security\nSalary: ₹8-18 LPA\n\n**Path 3: Full Stack**\n• All of the above!\n• MERN/MEAN Stack\nSalary: ₹10-25 LPA\n\n**Free Resources:**\n• freeCodeCamp (Best for beginners)\n• The Odin Project\n• MDN Web Docs\n• JavaScript30 Challenge\n\nBuild 5-10 projects for your portfolio!",
        'computer science': "Computer Science - The foundation! 🖥️\n\n**Core Subjects:**\n• Data Structures & Algorithms\n• Operating Systems\n• Database Management\n• Computer Networks\n• Software Engineering\n• Object-Oriented Programming\n\n**Top Colleges in India:**\n1. IIT Madras (NIRF #1)\n2. IIT Delhi (NIRF #2)\n3. IIT Bombay (NIRF #3)\n4. IIIT Hyderabad (₹32 LPA avg)\n5. BITS Pilani\n6. NIT Trichy, NITK\n\n**Entrance Exams:**\n• JEE Advanced (IITs)\n• JEE Main (NITs, IIITs)\n• BITSAT (BITS)\n• VITEEE (VIT)\n\n**Career Options:**\n• Software Engineer: ₹8-25 LPA\n• Data Scientist: ₹12-30 LPA\n• ML Engineer: ₹15-35 LPA\n• Product Manager: ₹20-50 LPA\n\nCheck our College Finder for detailed info!",
        
        # Career guidance
        'career': "Let me help you find the right career! 🎯\n\n**Top Fields in 2025:**\n\n🔵 **Technology** (High Growth)\n• Software Development\n• AI/ML Engineering\n• Data Science\n• Cloud Architecture\n• Cybersecurity\n\n🟢 **Healthcare** (Stable)\n• Doctor (MBBS/MD)\n• Nursing\n• Pharmacy\n• Medical Research\n\n🟣 **Business** (Versatile)\n• Management (MBA)\n• Marketing\n• Finance & Consulting\n• Entrepreneurship\n\n🔴 **Creative** (Growing)\n• UI/UX Design\n• Content Creation\n• Digital Marketing\n• Video Production\n\n💡 **Take our Career Quiz** for personalized recommendations!\n\nWhich field interests you most?",
        'best career': "Best careers in 2025! 🚀\n\n**Highest Growth:**\n1. AI/ML Engineer (+45% growth, ₹18-35 LPA)\n2. Cloud Architect (+38% growth, ₹15-30 LPA)\n3. Data Scientist (+35% growth, ₹12-25 LPA)\n4. Cybersecurity Expert (+40% growth, ₹16-32 LPA)\n5. Blockchain Developer (+55% growth, ₹20-40 LPA)\n\n**Most In-Demand:**\n• Full Stack Developer (120K+ jobs)\n• Data Analyst (95K+ jobs)\n• DevOps Engineer (85K+ jobs)\n\n**Best for Freshers:**\n• Software Development\n• Data Analytics\n• Digital Marketing\n• UI/UX Design\n\n**Factors to Consider:**\n✅ Your interests & strengths\n✅ Job market demand\n✅ Salary expectations\n✅ Work-life balance\n✅ Growth opportunities\n\nTake our quiz to find YOUR best fit!",
        
        # College related
        'college': "College selection guide! 🎓\n\n**Top Engineering Colleges:**\n• IIT Madras (NIRF #1, ₹21.48 LPA)\n• IIT Bombay (NIRF #3, ₹19.27 LPA)\n• IIIT Hyderabad (₹32 LPA avg!)\n• BITS Pilani (₹18 LPA)\n\n**Top Medical Colleges:**\n• AIIMS Delhi (NIRF #1)\n• CMC Vellore (NIRF #3)\n• JIPMER (Free education!)\n\n**Top Management:**\n• IIM Ahmedabad (₹32.79 LPA)\n• IIM Bangalore (₹28.98 LPA)\n• ISB Hyderabad\n\n**Top Law:**\n• NLSIU Bangalore (NIRF #1)\n• NLU Delhi (NIRF #2)\n\n**Selection Factors:**\n1. NIRF Ranking\n2. Placement Record\n3. Fee Structure\n4. Location\n5. Infrastructure\n\n👉 Use our College Finder to explore 100+ colleges!\n\nWhich field are you interested in?",
        'iit': "IIT - India's Premier Engineering Institutes! 🏆\n\n**Top 5 IITs:**\n1. **IIT Madras** (NIRF #1)\n   • Avg: ₹21.48 LPA\n   • Highest: ₹1.3 Cr\n   • Best for: CS, AI/ML, EE\n\n2. **IIT Delhi** (NIRF #2)\n   • Avg: ₹18.22 LPA\n   • QS Rank: 197\n   • Best for: CS, Civil, EE\n\n3. **IIT Bombay** (NIRF #3)\n   • Avg: ₹19.27 LPA\n   • Highest: ₹1.68 Cr\n   • Best for: CS, Aerospace\n\n4. **IIT Kanpur** (NIRF #4)\n5. **IIT Kharagpur** (NIRF #5)\n\n**Entrance:** JEE Advanced\n**Eligibility:** Top 2.5 lakh in JEE Main\n**Seats per IIT:** 800-1600\n**Fees:** ₹2-2.5 Lakh/year\n\n**All 23 IITs:**\nMadras, Delhi, Bombay, Kanpur, Kharagpur, Roorkee, Guwahati, Hyderabad, Indore, BHU, Ropar, + 12 newer IITs\n\nCheck College Finder for complete details!",
        'aiims': "AIIMS - Premier Medical Institutes! 🏥\n\n**AIIMS Delhi** (NIRF #1)\n• Est. 1956\n• MBBS Seats: 125\n• Fees: ₹1,400/year (Almost FREE!)\n• Acceptance: 0.01% (Hardest to get!)\n• Best medical education in India\n\n**Other Top AIIMS:**\n• AIIMS Jodhpur (NIRF #8)\n• AIIMS Bhopal (NIRF #9)\n• AIIMS Bhubaneswar\n• AIIMS Rishikesh\n• AIIMS Patna\n\n**Total AIIMS:** 22 across India\n\n**Entrance:** NEET UG\n**What You Need:**\n• NEET Score: 680+ (General)\n• Physics, Chemistry, Biology\n• Strong determination!\n\n**Career After AIIMS:**\n• Doctor (Govt/Private)\n• Medical Research\n• Teaching\n• Super-specialization\n\n**Alternatives:**\n• CMC Vellore (NIRF #3)\n• JIPMER (Free education)\n• Top State Medical Colleges\n\nVisit our College Finder for all medical colleges!",
        'scholarship': "Scholarship Guide! 💰\n\n**For Indian Students:**\n\n📚 **Merit-Based:**\n• PM Scholarship Scheme (₹3,000/month)\n• INSPIRE Scholarship (₹80,000/year)\n• KVPY Fellowship (₹7,000/month)\n• JN Tata Scholarship (Abroad)\n\n💼 **For Engineering:**\n• Google India Scholarship\n• Microsoft Scholarship\n• Adobe Women in Tech\n• Oracle Academy\n\n🏥 **For Medical:**\n• AIIMS Free Education\n• JIPMER Free Education\n• State Govt Scholarships\n\n📖 **For MBA:**\n• Aditya Birla Scholarship\n• IIM Need-based Aid\n• Bank Education Loans\n\n🌍 **Study Abroad:**\n• Fulbright Scholarship (USA)\n• Chevening (UK)\n• DAAD (Germany)\n• Commonwealth Scholarship\n\n**How to Apply:**\n1. Check eligibility\n2. Prepare documents\n3. Write strong essays\n4. Apply before deadline\n5. Follow up\n\nVisit our Scholarships page for complete list!",
        
        # Skills & Learning
        'python': "Python - Most Versatile Language! 🐍\n\n**Why Learn Python?**\n• Easiest to learn\n• High demand (50K+ jobs)\n• Versatile (Web, AI, Data Science)\n• Great salary (₹8-20 LPA)\n\n**Learning Path:**\n1. **Basics** (1 month)\n   • Variables, Data Types\n   • Loops, Conditions\n   • Functions\n\n2. **Intermediate** (2 months)\n   • OOP concepts\n   • File handling\n   • Libraries (NumPy, Pandas)\n\n3. **Advanced** (3 months)\n   • Web Dev (Django/Flask)\n   • Data Science\n   • Machine Learning\n\n**Free Resources:**\n• Python.org Tutorial\n• Automate the Boring Stuff\n• CS50's Python\n• freeCodeCamp Python\n\n**Projects to Build:**\n• Calculator\n• To-Do App\n• Web Scraper\n• Data Analysis Dashboard\n• ML Model\n\n**Career Options:**\n• Python Developer: ₹8-15 LPA\n• Data Scientist: ₹12-25 LPA\n• ML Engineer: ₹15-30 LPA\n\nStart today!",
        
        # Interview & Job Prep
        'interview': "Interview Preparation Guide! 💼\n\n**Technical Interview:**\n1. **Data Structures & Algorithms**\n   • Arrays, Linked Lists, Trees\n   • Sorting & Searching\n   • Dynamic Programming\n   • Practice: LeetCode, HackerRank\n\n2. **System Design** (for experienced)\n   • Scalability\n   • Database design\n   • API design\n\n3. **Coding Round**\n   • 2-3 coding problems\n   • Time: 60-90 minutes\n   • Focus: Logic + Clean code\n\n**HR Interview:**\n• Tell me about yourself\n• Why this company?\n• Strengths & weaknesses\n• Career goals\n• Salary expectations\n\n**Behavioral Questions:**\n• STAR method (Situation, Task, Action, Result)\n• Past experiences\n• Team conflicts\n• Leadership examples\n\n**Preparation Timeline:**\n• 3 months: Intensive prep\n• Daily: 2-3 hours practice\n• Week before: Mock interviews\n\n**Resources:**\n• Cracking the Coding Interview (book)\n• InterviewBit\n• Pramp (mock interviews)\n\n**Pro Tips:**\n✅ Research company\n✅ Prepare questions to ask\n✅ Dress professionally\n✅ Arrive 10 minutes early\n✅ Follow up with thank you email\n\nGood luck! 🍀",
        'resume': "Resume Building Guide! 📄\n\n**Perfect Resume Structure:**\n\n1. **Header**\n   • Name (Large, Bold)\n   • Phone, Email, LinkedIn, GitHub\n   • Location (City, State)\n\n2. **Professional Summary** (3-4 lines)\n   • Your expertise\n   • Years of experience\n   • Key achievements\n\n3. **Skills**\n   • Technical: Python, Java, React, SQL\n   • Tools: Git, Docker, AWS\n   • Soft: Leadership, Communication\n\n4. **Experience** (Reverse chronological)\n   • Job Title | Company | Duration\n   • 3-5 bullet points\n   • Start with action verbs\n   • Quantify achievements\n\n5. **Projects** (3-5 best)\n   • Project name + Tech stack\n   • Brief description\n   • Impact/Results\n   • GitHub link\n\n6. **Education**\n   • Degree | College | Year | GPA\n   • Relevant coursework\n   • Certifications\n\n7. **Additional** (Optional)\n   • Achievements\n   • Publications\n   • Volunteer work\n\n**Pro Tips:**\n✅ Keep it 1-2 pages\n✅ Use ATS-friendly format\n✅ Quantify everything (increased by 30%)\n✅ Use action verbs (Developed, Implemented)\n✅ Tailor for each job\n✅ No typos or grammar errors!\n✅ Include keywords from job description\n\n**Action Verbs:**\nDeveloped, Implemented, Designed, Led, Optimized, Achieved, Increased, Created\n\n**Use our Resume Builder** for professional templates!\n\nWant me to review your resume?",
        
        # Salary related
        'salary': "Salary Insights 2025! 💵\n\n**Tech Salaries (India):**\n\n**Freshers (0-2 years):**\n• Software Developer: ₹4-8 LPA\n• Data Analyst: ₹3-6 LPA\n• Web Developer: ₹3-7 LPA\n\n**Mid-Level (3-5 years):**\n• Software Engineer: ₹12-20 LPA\n• Data Scientist: ₹15-25 LPA\n• ML Engineer: ₹18-30 LPA\n• DevOps Engineer: ₹12-22 LPA\n\n**Senior (5-10 years):**\n• Senior Engineer: ₹25-40 LPA\n• Tech Lead: ₹30-50 LPA\n• Architect: ₹35-60 LPA\n\n**Expert (10+ years):**\n• Principal Engineer: ₹50-80 LPA\n• Director: ₹80 LPA - 1 Cr+\n\n**Highest Paying Companies:**\n🏆 Google: ₹30-80 LPA\n🏆 Microsoft: ₹25-70 LPA\n🏆 Amazon: ₹20-60 LPA\n🏆 Netflix: ₹50-1 Cr\n🏆 Uber: ₹25-55 LPA\n\n**Salary Factors:**\n• Location (Bangalore > Tier 2)\n• Company (Product > Service)\n• Skills (AI/ML premium)\n• Negotiation\n• Education (IIT premium)\n\n**Top Paying Skills:**\n1. AI/ML: +40% premium\n2. Cloud (AWS/Azure): +30%\n3. Blockchain: +50%\n4. DevOps: +25%\n5. Cybersecurity: +35%\n\nCheck Career Insights for detailed data!",
        
        # General help
        'help': "I'm here to help! 🌟\n\n**What I Can Do:**\n\n🎯 **Career Guidance**\n• Explore career options\n• Career path recommendations\n• Industry trends & insights\n\n🎓 **Education**\n• Top colleges (100+ listed!)\n• Course recommendations\n• Entrance exam tips\n\n💡 **Skill Development**\n• Learning roadmaps\n• Free resources\n• Skill requirements by role\n\n💼 **Job Preparation**\n• Interview tips\n• Resume building\n• Salary negotiation\n\n💰 **Financial**\n• Scholarship opportunities\n• Education loans\n• ROI analysis\n\n**Popular Questions:**\n• \"Tell me about AI careers\"\n• \"Best colleges for computer science\"\n• \"How to prepare for interviews?\"\n• \"What skills for data science?\"\n• \"IIT vs NIT comparison\"\n\n**Try Our Tools:**\n• Career Quiz (personalized recommendations)\n• College Finder (100+ colleges)\n• Skills Section (trending skills)\n• Resume Builder\n\nWhat would you like to explore?",
        'thank': "You're welcome! 😊\n\nFeel free to ask me anything else about your career!\n\nHere to help you succeed! 🚀",
    }
    
    # Enhanced keyword matching with multiple checks
    for keyword, response in responses.items():
        if keyword in message_lower:
            return response
    
    # Check for common question patterns
    if any(word in message_lower for word in ['iit', 'engineering college', 'best college for engineering']):
        return responses['iit']
    
    if any(word in message_lower for word in ['medical college', 'mbbs', 'doctor', 'aiims']):
        return responses['aiims']
    
    if any(word in message_lower for word in ['ml', 'machine learning', 'ai']):
        return responses['machine learning']
    
    if any(word in message_lower for word in ['web dev', 'website', 'frontend', 'backend']):
        return responses['web development']
    
    if any(word in message_lower for word in ['job', 'placement', 'interview']):
        return responses['interview']
    
    if any(word in message_lower for word in ['money', 'pay', 'package', 'ctc']):
        return responses['salary']
    
    # Intelligent default response with suggestions
    if '?' in message:
        return "Great question! 🤔\n\nI specialize in career guidance and can help you with:\n\n🎯 Career exploration & planning\n🎓 College recommendations (100+ listed!)\n💡 Skill development roadmaps\n💼 Interview & job preparation\n💰 Salary insights & scholarships\n\n**Popular topics:**\n• AI/ML and Data Science careers\n• Engineering colleges (IITs, NITs)\n• Medical colleges (AIIMS, etc.)\n• Interview preparation\n• Skill requirements\n\nCould you be more specific about what you'd like to know?\n\nOr try: 'help' to see all I can do!"
    
    return "Hi! I'm your AI Career Mentor! 🎯\n\nI'm here to guide you through your career journey!\n\n**Ask me about:**\n• Career paths (AI, Data Science, Software Dev)\n• Top colleges (IITs, AIIMS, IIMs, NITs)\n• Skills needed for any field\n• Interview preparation tips\n• Salary information\n• Scholarships & financial aid\n\n**Try asking:**\n'What skills do I need for software development?'\n'Tell me about IIT Madras'\n'Best career for 2024?'\n'How to prepare for interviews?'\n\n**Or use our tools:**\n• Take Career Quiz\n• Browse College Finder\n• Check Trending Skills\n\nWhat would you like to know?"

@app.route('/chatbot')
def chatbot():
    """Chatbot page"""
    return render_template('chatbot.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_email' not in session:
        flash('Please login to view dashboard', 'warning')
        return redirect(url_for('login'))
    
    # Get user info from session
    user = {
        'name': session.get('user_name', 'User'),
        'email': session.get('user_email', '')
    }
    
    # Get quiz result from session
    quiz_result = session.get('quiz_results', None)
    
    # Get progress for this user
    user_progress = [p for p in progress_storage if p.get('user_email') == session['user_email']]
    
    return render_template('dashboard.html', user=user, quiz_result=quiz_result, progress=user_progress)

@app.route('/roadmap')
def roadmap_general():
    """Show general learning roadmap"""
    return render_template('roadmap.html', career=None, roadmap=[])

@app.route('/roadmap/<career>')
def roadmap(career):
    """Show personalized career roadmap"""
    roadmap_data = get_career_roadmap(career)
    return render_template('roadmap.html', career=career, roadmap=roadmap_data)

def get_career_roadmap(career):
    """Get roadmap for specific career"""
    roadmaps = {
        'Software Developer': [
            {'phase': 'Beginner', 'duration': '3-6 months', 'skills': ['HTML/CSS', 'JavaScript', 'Git basics'], 'resources': ['freeCodeCamp', 'MDN Web Docs']},
            {'phase': 'Intermediate', 'duration': '6-12 months', 'skills': ['React/Vue', 'Node.js', 'Databases'], 'resources': ['Udemy', 'The Odin Project']},
            {'phase': 'Advanced', 'duration': '12+ months', 'skills': ['System Design', 'Cloud (AWS)', 'DevOps'], 'resources': ['LeetCode', 'System Design Primer']},
        ],
        'Data Scientist': [
            {'phase': 'Beginner', 'duration': '3-6 months', 'skills': ['Python', 'Statistics', 'SQL'], 'resources': ['Coursera', 'DataCamp']},
            {'phase': 'Intermediate', 'duration': '6-12 months', 'skills': ['Machine Learning', 'Pandas', 'Visualization'], 'resources': ['Kaggle', 'Fast.ai']},
            {'phase': 'Advanced', 'duration': '12+ months', 'skills': ['Deep Learning', 'Big Data', 'MLOps'], 'resources': ['Papers with Code', 'AWS ML']},
        ],
    }
    
    return roadmaps.get(career, [])

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))
        
        # Check if email already exists
        if email in users_storage:
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        # Store user in memory
        hashed_password = generate_password_hash(password)
        users_storage[email] = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.now().isoformat()
        }
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        user = users_storage.get(email)
        
        if user and check_password_hash(user['password'], password):
            session['user_email'] = user['email']
            session['user_name'] = user['name']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/results')
def results():
    """Show quiz results"""
    # Get quiz results from session
    quiz_data = session.get('quiz_results')
    
    if quiz_data and 'recommendations' in quiz_data:
        recommendations = quiz_data['recommendations']
        return render_template('results.html', recommendations=recommendations)
    else:
        flash('No quiz results found. Please take the quiz first.', 'warning')
        return redirect(url_for('quiz'))

@app.route('/resume_builder')
@app.route('/resume-builder')
def resume_builder():
    """Resume builder page"""
    return render_template('resume_builder.html')

@app.route('/college_finder')
@app.route('/college-finder')
def college_finder():
    """College finder page"""
    return render_template('college_finder.html')

@app.route('/scholarships')
def scholarships():
    """Scholarships page with real-time data"""
    return render_template('scholarships.html')

@app.route('/career_insights')
@app.route('/career-insights')
def career_insights():
    """Career insights and trends"""
    insights = get_career_insights()
    return render_template('career_insights.html', insights=insights)

@app.route('/ai_ml_datascience')
@app.route('/ai-ml-datascience')
def ai_ml_datascience():
    """AI/ML/Data Science career guide"""
    return render_template('ai_ml_datascience.html')

# API Routes for Real-Time Data
@app.route('/api/scholarships')
def api_scholarships():
    """API endpoint for scholarships"""
    try:
        scholarships = get_scholarships()
        return jsonify({
            'success': True,
            'data': scholarships,
            'count': len(scholarships),
            'last_updated': scholarships_cache['last_updated']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/internships')
def api_internships():
    """API endpoint for internships"""
    try:
        internships = get_internships()
        return jsonify({
            'success': True,
            'data': internships,
            'count': len(internships),
            'last_updated': internships_cache['last_updated']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs')
def api_jobs():
    """API endpoint for fresher jobs"""
    try:
        jobs = get_jobs()
        return jsonify({
            'success': True,
            'data': jobs,
            'count': len(jobs),
            'last_updated': jobs_cache['last_updated']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/opportunities')
def api_opportunities():
    """Combined API endpoint for all opportunities"""
    try:
        scholarships = get_scholarships()
        internships = get_internships()
        jobs = get_jobs()
        
        return jsonify({
            'success': True,
            'data': {
                'scholarships': scholarships,
                'internships': internships,
                'jobs': jobs
            },
            'counts': {
                'scholarships': len(scholarships),
                'internships': len(internships),
                'jobs': len(jobs),
                'total': len(scholarships) + len(internships) + len(jobs)
            },
            'last_updated': {
                'scholarships': scholarships_cache['last_updated'],
                'internships': internships_cache['last_updated'],
                'jobs': jobs_cache['last_updated']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search')
def api_search():
    """Search API for scholarships, internships, and jobs"""
    try:
        query = request.args.get('q', '').lower()
        category = request.args.get('category', 'all')
        location = request.args.get('location', '').lower()
        
        scholarships = get_scholarships()
        internships = get_internships()
        jobs = get_jobs()
        
        # Filter based on search criteria
        filtered_scholarships = []
        filtered_internships = []
        filtered_jobs = []
        
        # Search scholarships
        if category in ['all', 'scholarships']:
            for item in scholarships:
                if (query in item.get('title', '').lower() or 
                    query in item.get('provider', '').lower() or
                    query in item.get('eligibility', '').lower()):
                    if not location or location in item.get('state', '').lower():
                        filtered_scholarships.append(item)
        
        # Search internships
        if category in ['all', 'internships']:
            for item in internships:
                if (query in item.get('title', '').lower() or 
                    query in item.get('company', '').lower() or
                    query in item.get('category', '').lower()):
                    if not location or location in item.get('location', '').lower():
                        filtered_internships.append(item)
        
        # Search jobs
        if category in ['all', 'jobs']:
            for item in jobs:
                if (query in item.get('title', '').lower() or 
                    query in item.get('company', '').lower() or
                    query in item.get('category', '').lower()):
                    if not location or location in item.get('location', '').lower():
                        filtered_jobs.append(item)
        
        return jsonify({
            'success': True,
            'data': {
                'scholarships': filtered_scholarships,
                'internships': filtered_internships,
                'jobs': filtered_jobs
            },
            'counts': {
                'scholarships': len(filtered_scholarships),
                'internships': len(filtered_internships),
                'jobs': len(filtered_jobs),
                'total': len(filtered_scholarships) + len(filtered_internships) + len(filtered_jobs)
            },
            'query': {
                'search': query,
                'category': category,
                'location': location
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_colleges_data():
    """Get Indian college recommendations with NIRF 2025 rankings"""
    return [
        # IITs
        {
            'name': 'Indian Institute of Technology Madras',
            'short_name': 'IIT Madras',
            'location': 'Chennai, Tamil Nadu',
            'nirf_rank': 1,
            'ranking': 'NIRF #1',
            'type': 'IIT',
            'programs': ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Data Science'],
            'established': 1959,
            'avg_package': '₹21.48 LPA',
            'highest_package': '₹1.3 Cr',
            'fees': '₹2.18 Lakh/year',
            'acceptance': '2.5%',
            'total_seats': 1100,
            'rating': 4.8,
            'website': 'https://www.iitm.ac.in',
            'entrance_exam': 'JEE Advanced',
            'highlights': ['QS World Rank: 227', 'Top Research Institute', 'Best Placement Record']
        },
        {
            'name': 'Indian Institute of Technology Delhi',
            'short_name': 'IIT Delhi',
            'location': 'New Delhi, Delhi',
            'nirf_rank': 2,
            'ranking': 'NIRF #2',
            'type': 'IIT',
            'programs': ['Computer Science', 'AI/ML', 'Electronics', 'Civil Engineering'],
            'established': 1961,
            'avg_package': '₹18.22 LPA',
            'highest_package': '₹1.2 Cr',
            'fees': '₹2.25 Lakh/year',
            'acceptance': '2.8%',
            'total_seats': 1150,
            'rating': 4.7,
            'website': 'https://home.iitd.ac.in',
            'entrance_exam': 'JEE Advanced',
            'highlights': ['QS World Rank: 197', 'Strong Alumni Network', 'Premier Research Facilities']
        },
        {
            'name': 'Indian Institute of Technology Bombay',
            'short_name': 'IIT Bombay',
            'location': 'Mumbai, Maharashtra',
            'nirf_rank': 3,
            'ranking': 'NIRF #3',
            'type': 'IIT',
            'programs': ['Computer Science', 'Aerospace Engineering', 'Chemical Engineering', 'Biotechnology'],
            'established': 1958,
            'avg_package': '₹19.27 LPA',
            'highest_package': '₹1.68 Cr',
            'fees': '₹2.21 Lakh/year',
            'acceptance': '2.3%',
            'total_seats': 1200,
            'rating': 4.8,
            'website': 'https://www.iitb.ac.in',
            'entrance_exam': 'JEE Advanced',
            'highlights': ['QS World Rank: 149', 'Highest International Placements', 'Top Startup Ecosystem']
        },
        {
            'name': 'Indian Institute of Technology Kanpur',
            'short_name': 'IIT Kanpur',
            'location': 'Kanpur, Uttar Pradesh',
            'nirf_rank': 4,
            'ranking': 'NIRF #4',
            'type': 'IIT',
            'programs': ['Computer Science', 'Mechanical Engineering', 'Aerospace', 'Materials Science'],
            'established': 1959,
            'avg_package': '₹17.5 LPA',
            'highest_package': '₹1.5 Cr',
            'fees': '₹2.15 Lakh/year',
            'acceptance': '3.0%',
            'total_seats': 1000,
            'rating': 4.6,
            'website': 'https://www.iitk.ac.in',
            'entrance_exam': 'JEE Advanced',
            'highlights': ['QS World Rank: 264', 'Excellence in Research', 'Strong Industry Tie-ups']
        },
        {
            'name': 'Indian Institute of Technology Kharagpur',
            'short_name': 'IIT Kharagpur',
            'location': 'Kharagpur, West Bengal',
            'nirf_rank': 5,
            'ranking': 'NIRF #5',
            'type': 'IIT',
            'programs': ['Computer Science', 'Mining Engineering', 'Ocean Engineering', 'Agriculture & Food Engineering'],
            'established': 1951,
            'avg_package': '₹16.9 LPA',
            'highest_package': '₹2.0 Cr',
            'fees': '₹2.20 Lakh/year',
            'acceptance': '3.2%',
            'total_seats': 1600,
            'rating': 4.6,
            'website': 'https://www.iitkgp.ac.in',
            'entrance_exam': 'JEE Advanced',
            'highlights': ['Oldest IIT', 'Largest Campus', 'Diverse Programs']
        },
        
        # NITs
        {
            'name': 'National Institute of Technology Tiruchirappalli',
            'short_name': 'NIT Trichy',
            'location': 'Tiruchirappalli, Tamil Nadu',
            'nirf_rank': 9,
            'ranking': 'NIRF #9',
            'type': 'NIT',
            'programs': ['Computer Science', 'Electronics', 'Production Engineering', 'Instrumentation'],
            'established': 1964,
            'avg_package': '₹12.5 LPA',
            'highest_package': '₹42 LPA',
            'fees': '₹1.52 Lakh/year',
            'acceptance': '5.5%',
            'total_seats': 850,
            'rating': 4.5,
            'website': 'https://www.nitt.edu',
            'entrance_exam': 'JEE Main',
            'highlights': ['Top NIT', 'Strong Faculty', 'Excellent Infrastructure']
        },
        {
            'name': 'National Institute of Technology Karnataka',
            'short_name': 'NITK Surathkal',
            'location': 'Surathkal, Karnataka',
            'nirf_rank': 10,
            'ranking': 'NIRF #10',
            'type': 'NIT',
            'programs': ['Computer Science', 'Information Technology', 'Mechanical', 'Civil Engineering'],
            'established': 1960,
            'avg_package': '₹13.2 LPA',
            'highest_package': '₹48 LPA',
            'fees': '₹1.45 Lakh/year',
            'acceptance': '6.0%',
            'total_seats': 800,
            'rating': 4.4,
            'website': 'https://www.nitk.ac.in',
            'entrance_exam': 'JEE Main',
            'highlights': ['Scenic Campus', 'Strong Alumni', 'Research Excellence']
        },
        
        # IIITs
        {
            'name': 'International Institute of Information Technology Hyderabad',
            'short_name': 'IIIT Hyderabad',
            'location': 'Hyderabad, Telangana',
            'nirf_rank': 62,
            'ranking': 'NIRF #62',
            'type': 'IIIT',
            'programs': ['Computer Science', 'Electronics & Communication', 'Computational Natural Sciences'],
            'established': 1998,
            'avg_package': '₹32 LPA',
            'highest_package': '₹1.4 Cr',
            'fees': '₹4.5 Lakh/year',
            'acceptance': '1.5%',
            'total_seats': 150,
            'rating': 4.7,
            'website': 'https://www.iiit.ac.in',
            'entrance_exam': 'JEE Main + IIIT-H Entrance',
            'highlights': ['Best CS Program', 'Highest Avg Package', 'Research Powerhouse']
        },
        
        # Management Institutes
        {
            'name': 'Indian Institute of Management Ahmedabad',
            'short_name': 'IIM Ahmedabad',
            'location': 'Ahmedabad, Gujarat',
            'nirf_rank': 1,
            'ranking': 'NIRF #1 (Management)',
            'type': 'IIM',
            'programs': ['MBA', 'PGPX', 'PhD', 'ePGP'],
            'established': 1961,
            'avg_package': '₹32.79 LPA',
            'highest_package': '₹1.15 Cr',
            'fees': '₹25 Lakh (2-year MBA)',
            'acceptance': '0.8%',
            'total_seats': 395,
            'rating': 4.9,
            'website': 'https://www.iima.ac.in',
            'entrance_exam': 'CAT',
            'highlights': ['#1 B-School', 'World-Class Faculty', 'Excellent ROI']
        },
        {
            'name': 'Indian Institute of Management Bangalore',
            'short_name': 'IIM Bangalore',
            'location': 'Bangalore, Karnataka',
            'nirf_rank': 2,
            'ranking': 'NIRF #2 (Management)',
            'type': 'IIM',
            'programs': ['MBA', 'Executive MBA', 'PhD', 'Enterprise Data Science'],
            'established': 1973,
            'avg_package': '₹28.98 LPA',
            'highest_package': '₹1.02 Cr',
            'fees': '₹24.5 Lakh (2-year MBA)',
            'acceptance': '0.9%',
            'total_seats': 406,
            'rating': 4.8,
            'website': 'https://www.iimb.ac.in',
            'entrance_exam': 'CAT',
            'highlights': ['Tech Hub Location', 'Strong Consulting Placements', 'Global Exposure']
        },
        
        # Universities
        {
            'name': 'Birla Institute of Technology and Science Pilani',
            'short_name': 'BITS Pilani',
            'location': 'Pilani, Rajasthan',
            'nirf_rank': 25,
            'ranking': 'NIRF #25',
            'type': 'Deemed University',
            'programs': ['Computer Science', 'Electronics', 'Chemical Engineering', 'Pharmacy'],
            'established': 1964,
            'avg_package': '₹18.05 LPA',
            'highest_package': '₹60 LPA',
            'fees': '₹4.69 Lakh/year',
            'acceptance': '8.0%',
            'total_seats': 900,
            'rating': 4.6,
            'website': 'https://www.bits-pilani.ac.in',
            'entrance_exam': 'BITSAT',
            'highlights': ['Industry-Ready Graduates', 'Practice School System', 'Strong Alumni']
        },
        {
            'name': 'Vellore Institute of Technology',
            'short_name': 'VIT Vellore',
            'location': 'Vellore, Tamil Nadu',
            'nirf_rank': 11,
            'ranking': 'NIRF #11',
            'type': 'Deemed University',
            'programs': ['Computer Science', 'Electronics', 'Mechanical', 'Biotechnology'],
            'established': 1984,
            'avg_package': '₹7.52 LPA',
            'highest_package': '₹75 LPA',
            'fees': '₹1.98 Lakh/year',
            'acceptance': '15%',
            'total_seats': 3000,
            'rating': 4.3,
            'website': 'https://vit.ac.in',
            'entrance_exam': 'VITEEE',
            'highlights': ['Large Campus', 'International Tie-ups', 'Good Placements']
        },
        {
            'name': 'Delhi Technological University',
            'short_name': 'DTU Delhi',
            'location': 'New Delhi, Delhi',
            'nirf_rank': 34,
            'ranking': 'NIRF #34',
            'type': 'State University',
            'programs': ['Computer Science', 'Software Engineering', 'Information Technology', 'Electronics'],
            'established': 1941,
            'avg_package': '₹12.3 LPA',
            'highest_package': '₹1.8 Cr',
            'fees': '₹1.74 Lakh/year',
            'acceptance': '8%',
            'total_seats': 1100,
            'rating': 4.4,
            'website': 'https://www.dtu.ac.in',
            'entrance_exam': 'JEE Main',
            'highlights': ['Capital Location', 'Strong Industry Connect', 'Active Societies']
        },
        {
            'name': 'Manipal Institute of Technology',
            'short_name': 'MIT Manipal',
            'location': 'Manipal, Karnataka',
            'nirf_rank': 45,
            'ranking': 'NIRF #45',
            'type': 'Deemed University',
            'programs': ['Computer Science', 'Information Technology', 'Mechanical', 'Civil'],
            'established': 1957,
            'avg_package': '₹7.5 LPA',
            'highest_package': '₹44 LPA',
            'fees': '₹3.35 Lakh/year',
            'acceptance': '18%',
            'total_seats': 2000,
            'rating': 4.2,
            'website': 'https://manipal.edu',
            'entrance_exam': 'MET',
            'highlights': ['Good Infrastructure', 'Medical Sciences', 'Active Campus Life']
        },
        {
            'name': 'Netaji Subhas University of Technology',
            'short_name': 'NSUT Delhi',
            'location': 'New Delhi, Delhi',
            'nirf_rank': 68,
            'ranking': 'NIRF #68',
            'type': 'State University',
            'programs': ['Computer Science', 'IT', 'Electronics', 'Instrumentation'],
            'established': 1983,
            'avg_package': '₹11.8 LPA',
            'highest_package': '₹52 LPA',
            'fees': '₹1.58 Lakh/year',
            'acceptance': '7%',
            'total_seats': 650,
            'rating': 4.3,
            'website': 'http://www.nsut.ac.in',
            'entrance_exam': 'JEE Main',
            'highlights': ['Delhi Location', 'Strong CS Program', 'Growing Reputation']
        }
    ]

def get_scholarships_data():
    """Get scholarship information"""
    return [
        {
            'name': 'Gates Scholarship',
            'amount': 'Full Tuition',
            'deadline': 'September 15',
            'eligibility': 'High school seniors, Pell-eligible',
            'url': '#'
        },
        {
            'name': 'Google Generation Scholarship',
            'amount': '$10,000',
            'deadline': 'December 1',
            'eligibility': 'Computer Science students',
            'url': '#'
        },
        {
            'name': 'Coca-Cola Scholars',
            'amount': '$20,000',
            'deadline': 'October 31',
            'eligibility': 'High school seniors',
            'url': '#'
        },
        {
            'name': 'Dell Scholars Program',
            'amount': '$20,000',
            'deadline': 'December 1',
            'eligibility': 'Low-income, college-bound students',
            'url': '#'
        }
    ]

def get_career_insights():
    """Get career market insights with comprehensive skills data"""
    return {
        'trending_careers': [
            {'name': 'AI/ML Engineer', 'growth': '+35%', 'salary': '$120,000', 'demand': 'Very High'},
            {'name': 'Cloud Architect', 'growth': '+28%', 'salary': '$140,000', 'demand': 'High'},
            {'name': 'Data Scientist', 'growth': '+31%', 'salary': '$115,000', 'demand': 'Very High'},
            {'name': 'Cybersecurity Expert', 'growth': '+33%', 'salary': '$110,000', 'demand': 'Very High'},
            {'name': 'DevOps Engineer', 'growth': '+25%', 'salary': '$105,000', 'demand': 'High'},
            {'name': 'Full Stack Developer', 'growth': '+27%', 'salary': '$95,000', 'demand': 'Very High'},
            {'name': 'Blockchain Developer', 'growth': '+42%', 'salary': '$130,000', 'demand': 'High'}
        ],
        'top_skills': [
            {
                'skill': 'Python Programming',
                'category': 'Programming',
                'demand': 95,
                'avg_salary': '₹12 LPA',
                'jobs': '50,000+',
                'growth': '+32%',
                'difficulty': 'Beginner',
                'icon': 'fab fa-python',
                'color': 'blue',
                'description': 'Most versatile programming language for AI, web, and data science'
            },
            {
                'skill': 'Artificial Intelligence & ML',
                'category': 'Technical',
                'demand': 93,
                'avg_salary': '₹18 LPA',
                'jobs': '35,000+',
                'growth': '+45%',
                'difficulty': 'Advanced',
                'icon': 'fas fa-brain',
                'color': 'purple',
                'description': 'Build intelligent systems and machine learning models'
            },
            {
                'skill': 'Cloud Computing (AWS/Azure)',
                'category': 'Infrastructure',
                'demand': 90,
                'avg_salary': '₹15 LPA',
                'jobs': '45,000+',
                'growth': '+38%',
                'difficulty': 'Intermediate',
                'icon': 'fas fa-cloud',
                'color': 'indigo',
                'description': 'Design and manage scalable cloud infrastructure'
            },
            {
                'skill': 'Data Science & Analytics',
                'category': 'Data',
                'demand': 88,
                'avg_salary': '₹14 LPA',
                'jobs': '40,000+',
                'growth': '+35%',
                'difficulty': 'Intermediate',
                'icon': 'fas fa-chart-bar',
                'color': 'green',
                'description': 'Extract insights from data using statistical methods'
            },
            {
                'skill': 'JavaScript & React',
                'category': 'Programming',
                'demand': 85,
                'avg_salary': '₹10 LPA',
                'jobs': '55,000+',
                'growth': '+28%',
                'difficulty': 'Beginner',
                'icon': 'fab fa-js',
                'color': 'yellow',
                'description': 'Build modern, interactive web applications'
            },
            {
                'skill': 'Cybersecurity',
                'category': 'Security',
                'demand': 87,
                'avg_salary': '₹16 LPA',
                'jobs': '30,000+',
                'growth': '+40%',
                'difficulty': 'Advanced',
                'icon': 'fas fa-shield-alt',
                'color': 'red',
                'description': 'Protect systems and networks from cyber threats'
            },
            {
                'skill': 'DevOps & CI/CD',
                'category': 'Infrastructure',
                'demand': 84,
                'avg_salary': '₹13 LPA',
                'jobs': '38,000+',
                'growth': '+33%',
                'difficulty': 'Intermediate',
                'icon': 'fas fa-cogs',
                'color': 'orange',
                'description': 'Automate software development and deployment'
            },
            {
                'skill': 'SQL & Database Management',
                'category': 'Data',
                'demand': 82,
                'avg_salary': '₹9 LPA',
                'jobs': '48,000+',
                'growth': '+25%',
                'difficulty': 'Beginner',
                'icon': 'fas fa-database',
                'color': 'teal',
                'description': 'Design and optimize database systems'
            },
            {
                'skill': 'Mobile App Development',
                'category': 'Programming',
                'demand': 80,
                'avg_salary': '₹11 LPA',
                'jobs': '32,000+',
                'growth': '+30%',
                'difficulty': 'Intermediate',
                'icon': 'fas fa-mobile-alt',
                'color': 'pink',
                'description': 'Build iOS and Android applications'
            },
            {
                'skill': 'Docker & Kubernetes',
                'category': 'Infrastructure',
                'demand': 78,
                'avg_salary': '₹14 LPA',
                'jobs': '28,000+',
                'growth': '+42%',
                'difficulty': 'Advanced',
                'icon': 'fab fa-docker',
                'color': 'cyan',
                'description': 'Container orchestration and microservices'
            },
            {
                'skill': 'UI/UX Design',
                'category': 'Design',
                'demand': 76,
                'avg_salary': '₹8 LPA',
                'jobs': '25,000+',
                'growth': '+27%',
                'difficulty': 'Beginner',
                'icon': 'fas fa-palette',
                'color': 'purple',
                'description': 'Create user-friendly and beautiful interfaces'
            },
            {
                'skill': 'Blockchain Development',
                'category': 'Technical',
                'demand': 75,
                'avg_salary': '₹20 LPA',
                'jobs': '15,000+',
                'growth': '+55%',
                'difficulty': 'Advanced',
                'icon': 'fas fa-link',
                'color': 'amber',
                'description': 'Build decentralized applications and smart contracts'
            },
            {
                'skill': 'Digital Marketing & SEO',
                'category': 'Marketing',
                'demand': 74,
                'avg_salary': '₹7 LPA',
                'jobs': '42,000+',
                'growth': '+24%',
                'difficulty': 'Beginner',
                'icon': 'fas fa-bullhorn',
                'color': 'blue',
                'description': 'Promote products and brands online effectively'
            },
            {
                'skill': 'Git & Version Control',
                'category': 'Tools',
                'demand': 72,
                'avg_salary': '₹8 LPA',
                'jobs': '60,000+',
                'growth': '+20%',
                'difficulty': 'Beginner',
                'icon': 'fab fa-git-alt',
                'color': 'orange',
                'description': 'Manage and collaborate on code effectively'
            },
            {
                'skill': 'Business Analytics',
                'category': 'Business',
                'demand': 70,
                'avg_salary': '₹10 LPA',
                'jobs': '35,000+',
                'growth': '+22%',
                'difficulty': 'Intermediate',
                'icon': 'fas fa-chart-line',
                'color': 'green',
                'description': 'Make data-driven business decisions'
            }
        ],
        'skill_categories': [
            {
                'name': 'Programming Languages',
                'count': 5,
                'icon': 'fas fa-code',
                'skills': ['Python', 'JavaScript', 'Java', 'C++', 'Go']
            },
            {
                'name': 'Cloud & Infrastructure',
                'count': 4,
                'icon': 'fas fa-cloud',
                'skills': ['AWS', 'Azure', 'Docker', 'Kubernetes']
            },
            {
                'name': 'Data & AI',
                'count': 6,
                'icon': 'fas fa-robot',
                'skills': ['Machine Learning', 'Data Science', 'Deep Learning', 'NLP', 'Computer Vision', 'Big Data']
            },
            {
                'name': 'Development Tools',
                'count': 5,
                'icon': 'fas fa-tools',
                'skills': ['Git', 'VS Code', 'Jenkins', 'Jira', 'Postman']
            }
        ],
        'industries': [
            {'name': 'Technology', 'jobs': '2.5M', 'growth': '+22%'},
            {'name': 'Healthcare', 'jobs': '3.1M', 'growth': '+18%'},
            {'name': 'Finance', 'jobs': '1.8M', 'growth': '+15%'},
            {'name': 'E-commerce', 'jobs': '1.2M', 'growth': '+30%'},
            {'name': 'Education', 'jobs': '1.5M', 'growth': '+25%'},
            {'name': 'Manufacturing', 'jobs': '2.2M', 'growth': '+12%'}
        ]
    }

if __name__ == '__main__':
    # Run the app
    print("🚀 SmartCareer Platform Starting...")
    print("📍 Access the application at: http://localhost:5000")
    print("💡 No database required - using in-memory storage")
    
    # Production vs Development mode
    is_production = os.environ.get('FLASK_ENV') == 'production'
    
    if is_production:
        print("🔒 Running in PRODUCTION mode")
        app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("🔧 Running in DEVELOPMENT mode")
        app.run(debug=True, port=5000, host='127.0.0.1')
