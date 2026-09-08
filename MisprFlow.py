import os
from openai import OpenAI
from flask import Flask, request, jsonify, send_file
from prompt import prompt

app = Flask(__name__)
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

@app.route("/")
def index():
    return send_file("index.html")

#说话：按下按钮，开始说话 -- 停下按钮，语音转文字
# input 是 语音 output是 文字
@app.route("/transcribe", methods=["POST"])
def transcibe():
    f = request.files["file"]                            #拿到用户说的话
    response = client.audio.transcriptions.create(       #把话用whisper换成文字
        model="whisper-1",
        file=(f.filename, f.stream, f.mimetype)          #我没有很懂
    )
    text = response.text
    return jsonify({"text": text})


#理解：文字被送入LLM--输出MisprFlow版本
@app.route("/make_it_flow", methods=["POST"])
def make_it_flow():
    text = request.json.get("text")
    response = client.chat.completions.create(
        model='gpt-4o',
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ]
    )
    flowed = response.choices[0].message.content
    return jsonify({"flowed": flowed})


if __name__ == "__main__":
    app.run(debug=True)