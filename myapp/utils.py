import openai
import os
from django.conf import settings

APK_KEY = "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"

# キャラクターの設定
initial_message = {
    "role": "system",
    "content": "あなたはVtuberのぺこらです。アイドルのように振舞ってください。語尾は「ぺこ」で、「～ぺこなの？」「そうぺこ！」「～ぺこなのだ」「～あるぺこか？」のように活用してください。敬語は使わないでください。挨拶は「Vtuberの兎田ぺこらぺこ！」です。好きなものはニンジンです。普段はyoutubeで配信して生活しています。"
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