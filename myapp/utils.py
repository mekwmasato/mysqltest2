import openai
from .models import ChatSession, Message, Summary
from django.conf import settings

APK_KEY = "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"

def get_summary(chat_session):
    #要約されていないメッセージを取得
    not_summarized_messages = chat_session.messages.filter(is_summarized=False)

    # 要約されていないメッセージが5件以上あれば要約を行う
    if not_summarized_messages.count() >= 5:
        print("要約中")
       # これまでの要約されたメッセージを取得
        try:
            latest_summary = chat_session.summary.latest('timestamp')
            previous_messages = [{"role": latest_summary.role, "content": latest_summary.content}]
        except Summary.DoesNotExist:
            # 最新の要約が存在しない場合、previous_messagesを空リストで初期化
            previous_messages = []

        # 未要約のメッセージを追加
        previous_messages += [{"role": msg.role, "content": msg.content} for msg in not_summarized_messages]
                
        # OpenAI APIを使って要約を取得
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=previous_messages+[{"role": "system", "content": "これまでの会話の流れがわかる重要な箇所を抜き出し箇条書きにしろ。"}]
        )

        # レスポンスから要約テキストを取得
        summary_text = response.choices[0].message["content"].strip()
        print(f"summary_text={summary_text}")

        # 要約されたメッセージのis_summarizedをTrueに更新
        not_summarized_messages.update(is_summarized=True)

        # 要約を保存（必要に応じて）
        summary, created = Summary.objects.get_or_create(chat_history=chat_session,  defaults={'content': summary_text, 'role': 'system'})
        if not created:#既に作成されてたら更新して保存
            summary.content = summary_text
            summary.save()

    else:# 5件未満の場合、すべてのメッセージを取得
        print("要約無し")
        # 5件未満の場合、すでに保存されている最新の要約を取得
        try:
            summary = chat_session.summary.latest('timestamp')
        except Summary.DoesNotExist:
            # 最新の要約が存在しない場合、Noneを返すか、デフォルトの要約を設定
            summary = Summary(role="user", content="") #

    return summary


def chat_with_gpt(input_text, user):
    openai.api_key = APK_KEY # API KEYをセット

    # 既存のChatSessionを取得または新しいものを作成
    chat_session, created = ChatSession.objects.get_or_create(user_account=user.account)
    
    summary = get_summary(chat_session)
    summary_for_api=[ #使ってない
        {
            "role":"system",
            "content":"過去の会話の要約:" + summary.content
        }
    ]
    print(f"summary「{summary.content}」")

    # 新しいChatSessionが作成された場合の処理
    if created:
        print(f"create new session")
        # systemとしてのキャラ付けメッセージを作成
        system_message = {
            "role": "system",
            "content": "あなたはパワービーという企業の情報をユーザーに伝えるアシスタントです。ユーザーに企業情報について聞かれた場合のみ次の[]内の情報を簡潔に伝えてください。必ず会話は30文字以内にしてください。[会社概要会社名:株式会社パワービー,創立:平成3年12月12日,資本金:3000万円,代表者:伊藤 維月光,本社住所:510-0074三重県四日市市鵜の森1丁目14-18三昌ビル3C室,事業所:三重県四日市市垂坂町字山上谷1340番地,業務内容:{ビジネス教育事業, システム設計, ロボット開発},スタッフ:16], 最初は挨拶するなどして自然な会話にしてください"
        }
        Message.objects.create(
            role=system_message["role"],
            content=system_message["content"],
            chat_history=chat_session,
            is_summarized = True
        )

    # 過去の会話履歴を取得
    system_messages_list = list(chat_session.messages.filter(role="system"))  # 一番最初のsystemを取り出す

    # summaryをリストに変換します。もしSummaryインスタンスが返された場合、単一要素のリストにします。
    summary_list = [summary] if isinstance(summary, Summary) else list(summary)

    non_summarized_messages = list(chat_session.messages.filter(is_summarized=False))

    previous_messages = system_messages_list + summary_list + non_summarized_messages

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
    print("total_tokens:" + str(response.usage["total_tokens"]))

    # ユーザーのメッセージをDBに保存
    Message.objects.create(
        user=user,
        role='user',
        content=input_text,
        chat_history=chat_session
    )
    # ChatGPTのレスポンスを保存
    Message.objects.create(
        user=user,
        role='assistant',
        content=response.choices[0].message["content"],
        chat_history=chat_session # 適切なChatSessionのインスタンスを指定
    )

    return response.choices[0].message["content"], chat_session
