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

class ChatSession(models.Model):
    user_account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_account.user.username}"

class Message(models.Model):
    # このメッセージが関連するチャット履歴への外部キー
    chat_history = models.ForeignKey('ChatSession', on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('system', 'system'),
        ('user', 'user'),
        ('assistant', 'assistant'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()

    # メッセージの日時
    timestamp = models.DateTimeField(auto_now_add=True)

class Summary(models.Model):
    # このメッセージが関連するチャット履歴への外部キー
    chat_history = models.ForeignKey('ChatSession', on_delete=models.CASCADE, related_name='summary')
    ROLE_CHOICES = [
        ('system', 'system'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()

    # メッセージの日時
    timestamp = models.DateTimeField(auto_now_add=True)