from flask import Flask, render_template
import random
import pandas as pd
import google.generativeai as genai

app = Flask(__name__)

# Initialize Gemini API
GOOGLE_API_KEY = 'YOUR_API_KEY'
genai.configure(api_key=GOOGLE_API_KEY)
gmodel = genai.GenerativeModel('gemini-1.5-flash')

def load_student_data(csv_file):
    return pd.read_csv(csv_file)

def find_common_interests(group):
    interests = {
        'Favorite Movie': [],
        'Favorite Color': [],
        'Hobby': [],
        'Pet Type': [],
        'Sport': [],
        'Personality Trait': []
    }
    for student in group:
        for key in interests:
            interests[key].append(student[key])
    common_interests = {}
    for key, values in interests.items():
        common_interests[key] = pd.Series(values).mode()[0]
    return common_interests

def group_students_by_interests(df, group_size=5):
    students = df.to_dict(orient='records')
    random.shuffle(students)
    groups = [students[i:i+group_size] for i in range(0, len(students), group_size)]
    grouped_interests = []
    for group in groups:
        common_interests = find_common_interests(group)
        grouped_interests.append((group, common_interests))
    return grouped_interests

def generate_questions(common_interests):
    questions = []
    for interest, value in common_interests.items():
        questions.append(f"What do you all particularly love about {value} that makes it your favorite {interest}?")
    return questions

def send_to_gemini(group, common_interests, questions):
    try:
        group_ids = [student['Student ID'] for student in group]
        interests_summary = ', '.join([f"{key}: {value}" for key, value in common_interests.items()])
        prompt = f"""You are a friendly AI helping to group students based on common interests. 
        The group consists of the following students: {group_ids}. 
        The common interests for this group are: {interests_summary}.
        Here are some fun questions for them to discuss: {questions}.
        Please provide a child-friendly response that encourages them to interact and have fun together!"""

        response = gmodel.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Oops! Something went wrong. But don't worry, you can still have fun with your new friends!"

@app.route('/')
def home():
    csv_file = '/Users/tejasvinichawla/Desktop/PDF QA BOT/Fake data - Sheet1.csv'  # Update this path
    df = load_student_data(csv_file)
    grouped_data = group_students_by_interests(df)
    
    results = []
    for group, common_interests in grouped_data:
        questions = generate_questions(common_interests)
        gemini_response = send_to_gemini(group, common_interests, questions)
        
        group_info = {
            'members': [student['Student ID'] for student in group],
            'interests': common_interests,
            'questions': questions,
            'gemini_response': gemini_response
        }
        results.append(group_info)
    
    return render_template('index.html', groups=results)

if __name__ == '__main__':
    app.run(debug=True)