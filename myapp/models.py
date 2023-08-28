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
    

class ChatGPTSystemCommand(models.Model): #最初のキャラ付け用の命令を格納
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーとのリレーション
    chatgpt_template = models.TextField(max_length=200)

    def __str__(self):
        return self.command_text

class ChatHistory(models.Model): #会話履歴を格納
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーとのリレーション
    message_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) # 会話が追加された日時

    def __str__(self):
        return self.message_content