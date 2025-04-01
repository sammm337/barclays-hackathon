from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
from openai import OpenAI
import json
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import pickle 
#linked in scaping 
# import time
# import random
# import traceback
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Enable CORS to allow frontend access
CORS(app, resources={
    r"/get-courses": {
        "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
# Initialize OpenAI client
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# ======== YouTube Courses Database ========
# youtube_courses = {
#     "python": [
#         {
#             "id": "1",
#             "title": "Python for Beginners - Full Course [2024]",
#             "description": "Learn Python programming in this complete course for beginners",
#             "difficulty_level": "beginner",
#             "is_free": True,
#             "video_id": "rfscVS0vtbw",
#             "thumbnail_url": "https://i.ytimg.com/vi/rfscVS0vtbw/maxresdefault.jpg"
#         },
#         {
#             "id": "2",
#             "title": "Python Tutorial - Python Full Course for Beginners",
#             "description": "Python tutorial for beginners full course",
#             "difficulty_level": "beginner",
#             "is_free": True,
#             "video_id": "_uQrJ0TkZlc",
#             "thumbnail_url": "https://i.ytimg.com/vi/_uQrJ0TkZlc/maxresdefault.jpg"
#         },
#         {
#             "id": "3",
#             "title": "Advanced Python Programming Course",
#             "description": "Learn advanced Python concepts and techniques",
#             "difficulty_level": "advanced",
#             "is_free": True,
#             "video_id": "HGOBQPFzWKo",
#             "thumbnail_url": "https://i.ytimg.com/vi/HGOBQPFzWKo/maxresdefault.jpg"
#         },
#         {
#             "id": "4",
#             "title": "Python Django Full Course for Beginners",
#             "description": "Learn Django web framework with Python",
#             "difficulty_level": "intermediate",
#             "is_free": True,
#             "video_id": "F5mRW0jo-U4",
#             "thumbnail_url": "https://i.ytimg.com/vi/F5mRW0jo-U4/maxresdefault.jpg"
#         },
#         {
#             "id": "5",
#             "title": "Python Data Science Tutorial - Full Course",
#             "description": "Learn Data Science with Python",
#             "difficulty_level": "intermediate",
#             "is_free": True,
#             "video_id": "LHBE6Q9XlzI",
#             "thumbnail_url": "https://i.ytimg.com/vi/LHBE6Q9XlzI/maxresdefault.jpg"
#         },
#         {
#             "id": "6",
#             "title": "Python Machine Learning Tutorial",
#             "description": "Complete machine learning course with Python",
#             "difficulty_level": "advanced",
#             "is_free": True,
#             "video_id": "7eh4d6sabA0",
#             "thumbnail_url": "https://i.ytimg.com/vi/7eh4d6sabA0/maxresdefault.jpg"
#         },
#         {
#             "id": "7",
#             "title": "Python Automation Tutorial - Full Course",
#             "description": "Learn how to automate tasks with Python",
#             "difficulty_level": "intermediate",
#             "is_free": True,
#             "video_id": "PXMJ6FS7llk",
#             "thumbnail_url": "https://i.ytimg.com/vi/PXMJ6FS7llk/maxresdefault.jpg"
#         },
#         {
#             "id": "8",
#             "title": "Python Game Development Tutorial",
#             "description": "Learn game development with Pygame",
#             "difficulty_level": "intermediate",
#             "is_free": True,
#             "video_id": "FfWpgLFMI7w",
#             "thumbnail_url": "https://i.ytimg.com/vi/FfWpgLFMI7w/maxresdefault.jpg"
#         }
#     ],
#     "react": [
#         {
#             "id": "9",
#             "title": "React JS Full Course for Beginners",
#             "description": "Complete React JS course for beginners",
#             "difficulty_level": "beginner",
#             "is_free": True,
#             "video_id": "w7ejDZ8SWv8",
#             "thumbnail_url": "https://i.ytimg.com/vi/w7ejDZ8SWv8/maxresdefault.jpg"
#         }
#     ]
# }

# ======== Existing Databases ========
# Sample database of quiz questions
questions_db = {
    "react": [
        {
            "id": 1,
            "question": "What is React?",
            "options": [
                "A JavaScript library for building user interfaces",
                "A programming language",
                "A database management system",
                "An operating system"
            ],
            "answer": "A JavaScript library for building user interfaces"
        },
        {
            "id": 2,
            "question": "What is JSX?",
            "options": [
                "A JavaScript extension for XML",
                "A Java XML parser",
                "A JSON formatter",
                "A JavaScript testing framework"
            ],
            "answer": "A JavaScript extension for XML"
        }
    ],
    "python": [
        {
            "id": 1,
            "question": "What is the primary use of Python?",
            "options": [
                "Game development",
                "Data science and web development",
                "Mobile application development",
                "Cybersecurity only"
            ],
            "answer": "Data science and web development"
        }
    ]
}

# Sample summary data
summary_data = {
    "currentSkills": [
        {"id": "1", "code": "AI", "name": "Artificial Intelligence", "color": "blue"},
        {"id": "2", "code": "ML", "name": "Machine Learning", "color": "green"},
        {"id": "3", "code": "PY", "name": "Python", "color": "yellow"}
    ],
    "targetSkills": [
        {"id": "1", "code": "WD", "name": "Web Development", "color": "purple"},
        {"id": "2", "code": "JV", "name": "Java", "color": "red"},
        {"id": "3", "code": "RB", "name": "Robotics", "color": "blue"}
    ],
    "buddies": [
        {"id": "1", "initial": "S", "name": "Sameer", "color": "blue"},
        {"id": "2", "initial": "S", "name": "Sahil", "color": "green"},
        {"id": "3", "initial": "R", "name": "Rahul", "color": "purple"}
    ],
    "mentors": [
        {"id": "1", "initial": "A", "name": "Aslam", "color": "amber"},
        {"id": "2", "initial": "S", "name": "Soham", "color": "red"},
        {"id": "3", "initial": "P", "name": "Priya", "color": "green"}
    ]
}

# Sample career progress data
career_goals_db = {
    "amdocs": {
        "goal": "Land a tech job at Amdocs",
        "current_progress": 65,  # % completion
        "skills": ["React.js", "Node.js", "SQL", "System Design"],
        "next_steps": ["Improve DSA", "Build projects", "Practice system design"],
    },
    "google": {
        "goal": "Software Engineer at Google",
        "current_progress": 40,
        "skills": ["Algorithms", "Data Structures", "Machine Learning"],
        "next_steps": ["Solve Leetcode daily", "Contribute to open source"],
    },
    "amazon": {
        "goal": "Software Engineer at Amazon",
        "current_progress": 50,
        "skills": ["Java", "AWS", "Distributed Systems"],
        "next_steps": ["Learn System Design", "Solve Medium/Hard Leetcode"],
    },
    "microsoft": {
        "goal": "Software Engineer at Microsoft",
        "current_progress": 55,
        "skills": ["C#", ".NET", "Azure", "OOP"],
        "next_steps": ["Build Azure projects", "Prepare for behavioral interviews"],
    }
} 

# YouTube API Configuration
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
token_file = "token.pkl"
# Add new imports
import google.auth.transport.requests
import google.auth.exceptions

# Update the client_secrets_file path
client_secrets_file = r"c:\Users\DELL\Downloads\client_secret.json"

# Replace the existing get_youtube_client function with the new one
def get_youtube_client():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    credentials = None

    if os.path.exists(token_file):
        try:
            with open(token_file, "rb") as token:
                credentials = pickle.load(token)
        except (EOFError, pickle.UnpicklingError, ImportError, ModuleNotFoundError) as e:
            print(f"Warning: Could not load token from {token_file}. Error: {e}. Re-authenticating.")
            credentials = None

    if not credentials or not credentials.valid or not all(scope in credentials.scopes for scope in scopes):
        if credentials and credentials.expired and credentials.refresh_token:
            print("Credentials expired, attempting refresh...")
            try:
                request_object = google.auth.transport.requests.Request()
                credentials.refresh(request_object)
                print("Credentials refreshed successfully.")
                with open(token_file, "wb") as token:
                    pickle.dump(credentials, token)
                print(f"Refreshed credentials saved to {token_file}")
            except google.auth.exceptions.RefreshError as e:
                print(f"Error refreshing token: {e}")
                print("Refresh failed. Deleting potentially invalid token and re-authenticating.")
                if os.path.exists(token_file):
                    try:
                        os.remove(token_file)
                    except OSError as oe:
                        print(f"Error removing token file {token_file}: {oe}")
                credentials = None
            except Exception as e:
                print(f"An unexpected error occurred during token refresh: {e}")
                credentials = None

        if not credentials or not credentials.valid:
            print("No valid credentials found or refresh failed, starting authentication flow...")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes
            )
            credentials = flow.run_local_server(port=0)
            with open(token_file, "wb") as token:
                pickle.dump(credentials, token)
            print(f"New credentials obtained and saved to {token_file}")

    if not credentials or not credentials.valid:
        raise Exception("Failed to obtain valid credentials")

    return googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

# Update the get_related_videos function to use better error handling
def get_related_videos(query, max_results=5):
    try:
        youtube = get_youtube_client()
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results
        )
        response = request.execute()
        
        videos = []
        for i, item in enumerate(response.get("items", [])):
            if item["id"]["kind"] == "youtube#video":
                snippet = item["snippet"]
                videos.append({
                    "id": str(i + 1),
                    "title": snippet.get("title", "No title"),
                    "description": snippet.get("description", ""),
                    "difficulty_level": "unknown",
                    "is_free": True,
                    "video_id": item["id"]["videoId"],
                    "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", "")
                })
        return videos
    except googleapiclient.errors.HttpError as e:
        print(f"YouTube API HTTP error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in get_related_videos: {e}")
        return []

@app.route("/get-courses", methods=["POST"])
def get_courses():
    try:
        data = request.get_json()
        topic = data.get("topic", "").lower()
        
        if not topic:
            return jsonify({
                "success": False,
                "message": "No topic provided",
                "courses": []
            }), 400
        
        courses = get_related_videos(topic)
        
        if courses:
            return jsonify({
                "success": True,
                "courses": courses
            })
        else:
            # Fallback to hardcoded courses
            hardcoded_courses = {
                "python": [{
                    "id": "1",
                    "title": "Python for Beginners - Full Course",
                    "description": "Complete Python programming course for beginners",
                    "difficulty_level": "beginner",
                    "is_free": True,
                    "video_id": "rfscVS0vtbw",
                    "thumbnail_url": "https://i.ytimg.com/vi/rfscVS0vtbw/maxresdefault.jpg"
                }],
                "react": [{
                    "id": "2",
                    "title": "React JS Full Course",
                    "description": "Complete React JS course for beginners",
                    "difficulty_level": "beginner",
                    "is_free": True,
                    "video_id": "w7ejDZ8SWv8",
                    "thumbnail_url": "https://i.ytimg.com/vi/w7ejDZ8SWv8/maxresdefault.jpg"
                }]
            }
            
            if topic in hardcoded_courses:
                return jsonify({
                    "success": True,
                    "courses": hardcoded_courses[topic]
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"No courses found for {topic}",
                    "courses": []
                })
                
    except Exception as e:
        print(f"Error in get_courses: {e}")
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "courses": []
        }), 500

# ======== Existing Databases and Endpoints ======== 
# [Keep all your existing databases and endpoints exactly as they are]
# This includes:
# - questions_db
# - summary_data
# - career_goals_db
# - All other endpoints (/get-summary, /generate-quiz, etc.)
#-------------------
# after clicking mark as complete
from youtube_transcript_api import YouTubeTranscriptApi
from flask import jsonify

@app.route("/generate-video-quiz", methods=["POST"])
def generate_video_quiz():
    """
    Generates video-specific quiz questions by:
    1. Fetching YouTube transcript
    2. Using LLM to create questions
    3. Returning structured quiz data
    """
    try:
        data = request.get_json()
        video_id = data["videoId"]
        topic = data.get("topic", "")
        title = data.get("title", "")

        # Get transcript with error handling
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript_text = " ".join([t['text'] for t in transcript])
        except Exception as e:
            print(f"Transcript error: {e}")
            transcript_text = f"Video about {topic}. Title: {title}"

        # Generate quiz using LLM
        prompt = f"""
        Generate 3 quiz questions about this YouTube video:
        Title: {title}
        Topic: {topic}
        
        Video Content:
        {transcript_text[:3000]}

        Requirements:
        - Questions must be specific to video content
        - Include multiple choice options
        - Return valid JSON format
        """
        
        # Use existing LLM integration
        quiz_data = generate_questions_from_prompt(prompt)
        
        return jsonify({
            "success": True,
            "questions": quiz_data,
            "video_id": video_id,
            "topic": topic
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "Using fallback topic questions"
        }), 500



@app.route("/get-summary", methods=["GET"])
def get_summary():
    return jsonify(summary_data)

@app.route("/generate-quiz", methods=["POST"])
def gernerate_questions_from_llm():
    data = request.get_json()
    topic = data.get("topic", "").lower()
    """Generate quiz questions dynamically using NVIDIA API."""
    prompt = f"""
    Generate exactly 3 multiple-choice questions for a quiz on {topic}.
    Return only a valid JSON array, without explanations or formatting.
    Each question should have:
    - "id" (integer)
    - "question" (string)
    - "options" (list of 4 strings)
    - "answer" (string, must match one of the options)
    
    Example output:
    [
      {{
        "id": 1,
        "question": "What is AI?",
        "options": ["Option1", "Option2", "Option3", "Option4"],
        "answer": "Option1"
      }}
    ]
    """

    completion = client.chat.completions.create(
        model="meta/llama3-70b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        top_p=1,
        max_tokens=512
    )

    response_text = completion.choices[0].message.content.strip()

    try:
        # Remove Markdown formatting (if present)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1].strip()
            response_text = response_text.replace("json", "").strip()

        # First attempt to parse JSON
        parsed_response = json.loads(response_text)

        # If `questions` key exists but is a string, decode it again
        if isinstance(parsed_response, dict) and "questions" in parsed_response:
            if isinstance(parsed_response["questions"], str):
                parsed_response["questions"] = json.loads(parsed_response["questions"])

        return jsonify({"questions":parsed_response})
    
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse LLM response", "details": str(e), "raw_response": response_text}), 500

@app.route("/get-topics", methods=["GET"])
def get_topics():
    # Merge all available topics
    combined_topics = list(set(
        ["Python", "React.js", "C++", "Data Science"] + 
        list(questions_db.keys()) + 
        list(youtube_courses.keys())
    ))
    return jsonify({"topics": combined_topics})

@app.route("/get-intro", methods=["POST"])
def get_intro():
    data = request.get_json()
    topic = data.get("topic", "").lower()

    if topic in career_goals_db:
        return jsonify({"topic": topic, "intro": career_goals_db[topic]})
    else:
        return jsonify({"error": "No introduction available for this topic"}), 404

@app.route("/get-career-goal", methods=["POST"])
def get_career_goal():
    data = request.get_json()
    company_name = data.get("company", "").strip().lower()

    if company_name in career_goals_db:
        return jsonify(career_goals_db[company_name])
    else:
        return jsonify({"error": "Career goal data not found"}), 404

@app.route("/get-required-skills", methods=["POST"])
def get_required_skills():
    data = request.get_json()
    company_name = data.get("company", "").strip().lower()

    # Mock required skills for companies
    company_skills = {
        "google": ["Algorithms", "System Design", "Python", "Machine Learning"],
        "amazon": ["Java", "AWS", "Distributed Systems", "Data Structures"],
        "microsoft": ["C#", ".NET", "Azure", "OOP"],
        "amdocs": ["Java", "Spring Boot", "Microservices", "SQL", "Cloud"],
    }

    if company_name in company_skills:
        return jsonify({"skills": company_skills[company_name]})
    else:
        return jsonify({"error": "Skills not found for this company"}), 404

@app.route('/extract-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        file = request.files['pdf']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Read and parse PDF
        with pdfplumber.open(file) as pdf:
            text = '\n'.join([page.extract_text() for page in pdf.pages if page.extract_text()])
        
        return jsonify({'text': text})
    except Exception as e:
        print('Error processing PDF:', e)
        return jsonify({'error': 'Error processing PDF file'}), 500

@app.route('/chat', methods=['POST'])
def handle_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Create a prompt that includes context about learning and skills
        prompt = f"""
        You are a helpful learning assistant. The user is working on developing their skills in:
        Current skills: {', '.join([skill['name'] for skill in summary_data['currentSkills']])}
        Target skills: {', '.join([skill['name'] for skill in summary_data['targetSkills']])}
        
        The user asked: "{user_message}"
        
        Provide a helpful, concise response focused on learning and skill development.
        """
        
        completion = client.chat.completions.create(
            model="meta/llama3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        bot_response = completion.choices[0].message.content.strip()
        return jsonify({'reply': bot_response})
    
    except Exception as e:
        print('Error in chat endpoint:', e)
        return jsonify({
            'reply': "Sorry, I'm having trouble responding right now. Please try again later."
        }), 500

# ats job discription passing to backend 

@app.route('/analyze-jd', methods=['POST'])
def analyze_jd():
    try:
        data = request.get_json()
        job_description = data.get('jobDescription')
        
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
            
        # Log the job description
        print("Received Job Description:", job_description)
        print("Job Description Length:", len(job_description))
        print("=" * 50)  # Separator for better visibility in logs
            
        return jsonify({
            'success': True,
            'message': 'Job description analyzed successfully'
        })
        
    except Exception as e:
        print("Error processing job description:", str(e))
        return jsonify({'error': str(e)}), 500

# #---------------------------
# # --- LinkedIn Scraper Constants ---
# LINKEDIN_EMAIL = "shreyashpatange59@gmail.com" 
# LINKEDIN_PASSWORD = "mG:vBA_H5#J6w=="
# LOGIN_URL = "https://www.linkedin.com/login"
# JOBS_URL_BASE = "https://www.linkedin.com/jobs/search/?keywords="

# def linkedin_job_scraper(search_keywords):
#     """
#     Scrapes LinkedIn for jobs based on keywords, attempts login, scrolls to load results,
#     parses job listings using BeautifulSoup, and returns the data as a JSON string.
#     """
#     print(f"--- Starting LinkedIn Scraper for: '{search_keywords}' ---")

#     # Selenium WebDriver Setup
#     options = webdriver.ChromeOptions()
#     options.add_argument("--headless")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--start-maximized")
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option('useAutomationExtension', False)
#     options.add_argument("--disable-infobars")
#     options.add_argument('--disable-blink-features=AutomationControlled')

#     jobs_data = []
#     driver = None

#     try:
#         print("Initializing WebDriver...")
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=options)
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#         print("WebDriver initiated.")

#         # LinkedIn Login
#         print(f"Navigating to Login page: {LOGIN_URL}")
#         driver.get(LOGIN_URL)
#         time.sleep(random.uniform(3.5, 5.5))
        
#         username_field = driver.find_element(By.ID, "username")
#         password_field = driver.find_element(By.ID, "password")
#         username_field.send_keys(LINKEDIN_EMAIL)
#         time.sleep(random.uniform(0.8, 1.5))
#         password_field.send_keys(LINKEDIN_PASSWORD)
#         time.sleep(random.uniform(1.0, 1.8))
#         password_field.send_keys(Keys.RETURN)
#         print("Attempting login...")
#         time.sleep(random.uniform(10, 25))

#         current_url = driver.current_url
#         if "login" in current_url or "checkpoint" in current_url or "challenge" in current_url:
#             print(f"WARNING: Login may have failed. URL: {current_url}")
#             raise Exception("Login failed or requires verification")

#         # Job Search
#         encoded_keywords = search_keywords.replace(' ', '%20')
#         search_url = f"{JOBS_URL_BASE}{encoded_keywords}"
#         print(f"Navigating to job search URL: {search_url}")
#         driver.get(search_url)
#         time.sleep(random.uniform(8, 15))

#         # Scrolling
#         print("Scrolling down...")
#         last_height = driver.execute_script("return document.body.scrollHeight")
#         scroll_attempts = 0
#         max_scroll_attempts = 5
#         no_change_streak = 0
#         max_no_change_streak = 2
        
#         while scroll_attempts < max_scroll_attempts:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             scroll_attempts += 1
#             print(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}...")
#             time.sleep(random.uniform(4, 8))
#             new_height = driver.execute_script("return document.body.scrollHeight")
#             if new_height == last_height:
#                 no_change_streak += 1
#                 if no_change_streak >= max_no_change_streak:
#                     print("Reached bottom or no new jobs loaded.")
#                     break
#             else:
#                 no_change_streak = 0
#                 last_height = new_height

#         # Parsing
#         print("Parsing job listings...")
#         page_source = driver.page_source
#         soup = BeautifulSoup(page_source, "lxml")
#         job_list_container = soup.find("ul", class_=lambda c: c and 'jobs-search__results-list' in c)

#         if job_list_container:
#             job_postings = job_list_container.find_all("li", recursive=False)
#             print(f"Found approximately {len(job_postings)} potential job elements.")
#             processed_links = set()
            
#             for job_item in job_postings:
#                 try:
#                     link_element = job_item.find("a", class_=lambda c: c and 'base-card__full-link' in c, href=True)
#                     title_element = job_item.find(["h3", "span"], class_=lambda c: c and 'base-search-card__title' in c)
#                     company_element = job_item.find(["h4", "a", "span"], class_=lambda c: c and 'base-search-card__subtitle' in c)
#                     location_element = job_item.find("span", class_=lambda c: c and 'job-search-card__location' in c)

#                     link = "N/A"
#                     if link_element:
#                         raw_link = link_element['href'].strip()
#                         link = ("https://www.linkedin.com" + raw_link) if raw_link.startswith("/") else raw_link
#                         link = link.split('?')[0]

#                     if link in processed_links or link == "N/A": continue
#                     processed_links.add(link)

#                     title = title_element.text.strip() if title_element else "N/A"
#                     company = company_element.text.strip() if company_element else "N/A"
#                     location = location_element.text.strip() if location_element else "N/A"

#                     if title == "N/A" or company == "N/A": continue

#                     jobs_data.append({
#                         "Title": title, 
#                         "Company": company, 
#                         "Location": location, 
#                         "Link": link
#                     })
#                 except Exception as parse_err:
#                     print(f"Error parsing one item: {parse_err}")

#         else:
#             print("ERROR: Could not find job list container.")

#         if jobs_data:
#             print(f"--- Successfully Scraped: {len(jobs_data)} Jobs ---")
#             return json.dumps(jobs_data, indent=4, ensure_ascii=False)
#         else:
#             print("\nNo job data was successfully scraped or parsed.")
#             return json.dumps([])

#     except Exception as e:
#         print(f"\n--- An critical error occurred during the scraping process ---")
#         print(f"Error Type: {type(e).__name__}")
#         print(f"Error Details: {e}")
#         traceback.print_exc()
#         error_info = {"error": f"Scraping failed: {type(e).__name__}", "details": str(e)}
#         return json.dumps(error_info, indent=4)

#     finally:
#         if driver:
#             print("Closing WebDriver...")
#             driver.quit()
#             print("WebDriver closed.")

# @app.route('/scrape-linkedin', methods=['POST'])
# def scrape_linkedin_route():
#     start_req_time = time.time()
#     print("\n--- Received request for /scrape-linkedin ---")

#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({'error': 'Invalid JSON payload received'}), 400

#         search_keywords = data.get('search_keywords')
#         if not search_keywords or not isinstance(search_keywords, str) or not search_keywords.strip():
#             return jsonify({'error': 'Missing or invalid "search_keywords" in JSON payload'}), 400

#         print(f"Received keywords: '{search_keywords}'")
#         print("Invoking LinkedIn scraper...")
#         scraper_json_string = linkedin_job_scraper(search_keywords)
#         print("Scraper function finished.")

#         try:
#             scraper_result_data = json.loads(scraper_json_string)
#         except json.JSONDecodeError as json_err:
#             print(f"Error: Scraper returned an invalid JSON string: {json_err}")
#             print(f"Scraper raw output: {scraper_json_string[:500]}...")
#             return jsonify({'error': 'Internal scraper error: Failed to parse scraper results', 'details': str(json_err)}), 500

#         is_error_result = isinstance(scraper_result_data, dict) and 'error' in scraper_result_data
#         end_req_time = time.time()
#         duration = end_req_time - start_req_time
#         print(f"--- Request processing finished in {duration:.2f} seconds ---")

#         if is_error_result:
#             print(f"Scraper returned an error: {scraper_result_data.get('error')}")
#             return jsonify(scraper_result_data), 500
#         else:
#             print(f"Scraper returned {len(scraper_result_data)} job items.")
#             return jsonify(scraper_result_data)

#     except Exception as e:
#         end_req_time = time.time()
#         duration = end_req_time - start_req_time
#         print(f"--- Request processing FAILED in {duration:.2f} seconds ---")
#         print(f"Error processing '/scrape-linkedin' request: {str(e)}")
#         traceback.print_exc()
#         return jsonify({'error': 'An unexpected server error occurred', 'details': str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)

    