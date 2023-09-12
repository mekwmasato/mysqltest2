from django.db import models
# ユーザー認証
from django.contrib.auth.models import User #Djangoですでに用意されているUser model

# ユーザーアカウントのモデルクラス
class Account(models.Model):

    # ユーザー認証のインスタンス(1vs1関係)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # 追加フィールド
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    account_image = models.ImageField(upload_to="profile_pics",blank=True)

    def __str__(self):
        return self.user.username
    

class ChatHistory(models.Model):
    # 会話を行ったユーザーの情報 (Accountモデルへの外部キー)
    user_account = models.ForeignKey(Account, on_delete=models.CASCADE)

    # ユーザーからの質問やコメント
    user_message = models.TextField()

    # ChatGPTからの応答
    chatgpt_response = models.TextField()

    # 会話の日時
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_account.user.username} - {self.timestamp}"