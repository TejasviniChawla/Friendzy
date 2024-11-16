from flask import Flask, request, jsonify, render_template
from wie import KidsInteractiveChatbot
import markdown

app = Flask(__name__)
chatbot = KidsInteractiveChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get('question')
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        # Generate response using the chatbot
        response = chatbot.generate_response(question)
        # Convert response to HTML (in case there's any markdown)
        response_html = markdown.markdown(response)
        return jsonify({'answer': response_html})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)