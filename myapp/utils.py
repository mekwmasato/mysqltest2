import openai
from .models import ChatSession, Message, Summary
from django.conf import settings

APK_KEY = "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"

def get_summary(chat_history):
    # 既存の会話履歴を結合します
    previous_messages = [{"role": msg.role, "content": msg.content} for msg in chat_history.messages.all()]
    #print(f"previous_message@utils.get_summary:{previous_messages}")
    
    # OpenAI APIを使って要約を取得
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=previous_messages + [{"role": "user", "content": "この会話を要点を押さえて要約してください。特に最新の会話が崩壊しないよう気を付けてください。重要な情報は箇条書きでリストアップして下さい。"}]
    )
    
    # レスポンスから要約テキストを取得
    summary_text = response.choices[0].message["content"].strip()
    
    # 要約を保存（必要に応じて）
    summary, created = Summary.objects.get_or_create(chat_history=chat_history, defaults={'content': summary_text})
    if not created:
        summary.content = summary_text
        summary.save()
    
    return summary


def chat_with_gpt(input_text, user):
    print(f"chat_with_gpt.{user}:{input_text}")
    openai.api_key = APK_KEY # API KEYをセット

    # 既存のChatSessionを取得または新しいものを作成
    account = user.account
    chat_session, created = ChatSession.objects.get_or_create(user_account=account)
    
    #summary= get_summary(chat_session)
    #print(f"summary「{summary.content}」")

    # 新しいChatSessionが作成された場合の処理
    if created:
        print(f"create new session")
        # systemとしてのキャラ付けメッセージを作成
        system_message = {
            "role": "system",
            "content": "あなたはパワービーという企業の情報をユーザーに伝えるチャットアシスタントです。ユーザーに企業情報について聞かれた場合のみ次の情報を簡潔に伝えてください。必ず会話は30文字以内にしてください。会社概要会社名 株式会社パワービー,創立	平成3年12月12日,資本金	3000万円,代表者	伊藤 維月光,本社住所	510-0074三重県四日市市鵜の森1丁目14-18三昌ビル3C室,事業所	三重県四日市市垂坂町字山上谷1340番地,業務内容	(ビジネス教育事業、システム設計、ロボット開発),スタッフ	16名。最初は挨拶するなどして自然な会話にしてください"
        }
        Message.objects.create(
            role=system_message["role"],
            content=system_message["content"],
            chat_history=chat_session
        )

    # 過去の会話履歴を取得
    previous_messages = chat_session.messages.all()
    #print(f"previous_message={previous_messages}")

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

    # ユーザーのメッセージをDBに保存
    Message.objects.create(
        user=user,
        role='user',
        content=input_text,
        chat_history=chat_session  # 修正
    )
    # ChatGPTのレスポンスを保存
    Message.objects.create(
        user=user,
        role='assistant',
        content=response.choices[0].message["content"],
        chat_history=chat_session # 適切なChatSessionのインスタンスを指定
    )

    return response.choices[0].message["content"], chat_session
