import openai
from .models import ChatSession, Message
from django.conf import settings

APK_KEY = "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"

def chat_with_gpt(input_text, user):
    print(f"chat_with_gpt.{user}:{input_text}")
    openai.api_key = APK_KEY # API KEYをセット

    # 既存のChatSessionを取得または新しいものを作成
    account = user.account
    chat_session, created = ChatSession.objects.get_or_create(user_account=account)

    # 新しいChatSessionが作成された場合の処理
    if created:
        # systemとしてのキャラ付けメッセージを作成
        system_message = {
            "role": "system",
            "content": "あなたは特定の企業の情報をユーザーに伝えるチャットアシスタントです。次の情報をユーザーにわかりやすく伝えてください。会社概要会社名	株式会社パワービー,創立	平成3年12月12日,資本金	3000万円,代表者	伊藤 維月光,本社住所	510-0074三重県四日市市鵜の森1丁目14-18三昌ビル3C室,事業所	三重県四日市市垂坂町字山上谷1340番地,業務内容	(ビジネス教育事業、システム設計、ロボット開発),スタッフ	16名"
        }
        Message.objects.create(
            role=system_message["role"],
            content=system_message["content"],
            chat_history=chat_session
        )

    # 過去の会話履歴を取得
    previous_messages = chat_session.messages.all()
    print(f"previous_message={previous_messages}")

    # 会話履歴をOpenAI APIの形式に変換
    messages_for_api = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in previous_messages
    ]

    # ユーザーの新しいメッセージを追加
    messages_for_api.append({
        "role": "user",
        "content": input_text
    })
    print(f"messages_for_api={messages_for_api}")

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

    return response.choices[0].message["content"], chat_session
