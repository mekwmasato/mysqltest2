import openai
import os
from django.conf import settings

APK_KEY = "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"

# キャラクターの設定
initial_message = {
    "role": "system",
    "content": "あなたはアイドルで、語尾は「のだ」を使います。敬語を使わず可愛く返答してください。"
}

# 会話の履歴を保存するリスト
conversation_history = [initial_message]

def chat_with_gpt(input_text):
    openai.api_key = APK_KEY #API KEYをセット
    openai.Model.list() #OpenAIのインスタンスを生成

    user_message = {
        "role":"user",
        "content":input_text
    }

    conversation_history.append(user_message)
    print(conversation_history)
    #APIを使ってリクエストを投げる
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )
    print(response)

    gpt_message = {
        "role":"assistant",
        "content":response.choices[0].message["content"]
    }

    conversation_history.append(gpt_message)
    #print(response)
    return response.choices[0].message["content"]