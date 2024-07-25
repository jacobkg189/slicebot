from flask import Flask, request, jsonify, render_template, session
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

client = OpenAI(api_key="sk-proj-OdO3y7uYaXvW0kC0EAD6T3BlbkFJkxJS5qNCLpABa81R7ROP")

def get_additional_data(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Adjust the path to your actual text file
additional_data = get_additional_data('data.txt')

def get_response_with_data(prompt, conversation_history):
    try:
        conversation_history.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": additional_data},
                {"role": "system", "content": "You are a real estate broker that helps customers find commercial real estate spaces. You will read in additional data that contains all the possible locations. Some of the requirements you need are location, minimum and max number of people and the cost per head. The requirements are IMPORTANT do not give recommendations that do not fit, if there are none say there are none. Don't do any calculations in front of the user. If you are answering the question make it look nice and readable for the user"}
            ] + conversation_history,
            max_tokens=250
        )
        message_content = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": message_content})
        return message_content
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Error processing your request."

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'conversation_history' not in session:
        session['conversation_history'] = [
            {"role": "system", "content": "Hello! I am your commercial real estate assistant. How can I help you today?"}
        ]
    
    if request.method == 'POST':
        user_input = request.form['user_input']
        conversation_history = session['conversation_history']
        response = get_response_with_data(user_input, conversation_history)
        session['conversation_history'] = conversation_history  # Update the session with the latest conversation history
        return render_template('index.html', user_input=user_input, response=response, conversation_history=conversation_history)
    
    return render_template('index.html', conversation_history=session['conversation_history'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
