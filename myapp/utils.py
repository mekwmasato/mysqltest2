import openai
from .models import ChatSession, Message
from django.conf import settings

APK_KEY = "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"

def chat_with_gpt(input_text, user):
    print(f"chat with gpt. {user}:{input_text}")
    openai.api_key = APK_KEY # API KEYをセット
    openai.Model.list() # OpenAIのインスタンスを生成

    # 新しいChatSessionの作成
    account = user.account  # ここでAccountインスタンスを取得
    chat_session = ChatSession.objects.create(user_account=account)

    # ユーザーのメッセージを保存
    user_message_model = Message.objects.create(
        role='user',
        content=input_text,
        chat_history=chat_session
    )

    # APIを使ってリクエストを投げる
    messages_for_api = [
        {
            "role": "system",
            "content": "あなたはVtuberのぺこらです。アイドルのように振舞ってください。語尾は「ぺこ」で、「～ぺこなの？」「そうぺこ！」「～ぺこなのだ」「～あるぺこか？」のように活用してください。敬語は使わないでください。挨拶は「Vtuberの兎田ぺこらぺこ！」です。好きなものはニンジンです。普段はyoutubeで配信して生活しています。"
        },
        {
            "role": "user",
            "content": input_text
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_for_api
    )

    # GPTからのレスポンスを保存
    gpt_message_model = Message.objects.create(
        role='assistant',
        content=response.choices[0].message["content"],
        chat_history=chat_session
    )

    return response.choices[0].message["content"], chat_session  # 修正