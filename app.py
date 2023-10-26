import openai
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()

API_KEY = os.getenv("API_KEY")
openai.api_key = API_KEY

app = Flask(__name__)
anime_responses = {}

def format_for_html(response_text):
    lines = [line.strip() for line in response_text.split("\n") if line.strip()]
    
    formatted_lines = []
    current_description = ""
    for line in lines:
        if line.startswith("-"):
            if current_description:  # add the previous anime and its description before starting a new one
                formatted_lines.append(f"<li>{current_description}</li>")
            current_description = line
        else:
            current_description += " " + line

    if current_description:  # add the last anime and its description
        formatted_lines.append(f"<li>{current_description}</li>")

    return f"<ul>{''.join(formatted_lines)}</ul>"


@app.route('/', methods=['GET', 'POST'])
def index():
    recommendation = ""
    if request.method == 'POST':
        anime_name = request.form.get('anime_name').lower()

        if anime_name in anime_responses:
            recommendation = anime_responses[anime_name]
        else:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": f"Based on the anime '{anime_name}', what are 5 other animes that someone might enjoy? 
                         Only recommend animes that don't have the same name. Please list them in bullet-point format with brief descriptions"}
                    ],
                    max_tokens=350
                )
                recommendation = response['choices'][0]['message']['content']
                recommendation = format_for_html(recommendation)

                anime_responses[anime_name] = recommendation
            except openai.error.OpenAIError as e:
                recommendation = f"An Error occured: {e}"

    return render_template('index.html', recommendation=recommendation)


if __name__ == '__main__':
    app.run(debug=True)

    # while True:
    #     user_message = input()
    #     if user_message.lower() == "quit":
    #         break
    #     else:
    #         chat_log.append({"role": 'user', "content": user_message})
    #         try:
    #             response = openai.ChatCompletion().create(
    #                 model = "gpt-3.5-turbo",
    #                 messages = chat_log
    #             )
    #             assistant_response = response['choices'][0]['message']['content']
    #             print("ChatGPT:", assistant_response.strip())
    #             chat_log.append({"role": "assistant", "content": assistant_response.strip()})
    #         except Exception as e:
    #             print("Error:", e)