from django.shortcuts import render
from django.views.generic import TemplateView #テンプレートタグ
from .forms import AccountForm, AddAccountForm #ユーザーアカウントフォーム
from django.views import View
from .utils import chat_with_gpt 


# ログイン・ログアウト処理に利用
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Message, Account, ChatSession

from django.shortcuts import redirect
from django.contrib import messages


#ログイン
def Login(request):
    # POST
    if request.method == 'POST':
        # フォーム入力のユーザーID・パスワード取得
        ID = request.POST.get('userid')
        Pass = request.POST.get('password')

        # Djangoの認証機能
        user = authenticate(username=ID, password=Pass)

        # ユーザー認証
        if user:
            #ユーザーアクティベート判定
            if user.is_active:
                # ログイン
                login(request,user)
                # ホームページ遷移
                return HttpResponseRedirect(reverse('myapp:home'))
            else:
                # アカウント利用不可
                return HttpResponse("アカウントが有効ではありません")
        # ユーザー認証失敗
        else:
            return HttpResponse("ログインIDまたはパスワードが間違っています")
    # GET
    else:
        return render(request, 'myapp/login.html')

#ログアウト
@login_required
def Logout(request):
    logout(request)
    # ログイン画面遷移
    return HttpResponseRedirect(reverse('myapp:Login'))


#ホーム
@login_required
def home(request):
    try:
        account = request.user.account
    except Account.DoesNotExist:
        return HttpResponse("関連するアカウントが存在しません。")

    #POST
    if request.method == 'POST':
        input_text = request.POST['input_text']
        
        # Chat-GPTへのリクエスト
        response, chat_session = chat_with_gpt(input_text, request.user)  # 修正

        context = {
            'UserID': request.user,
            'input_text': input_text,
            'response': response,
        }
        print(f"context:{context}")
        # ユーザーの過去の会話履歴を取得
        message_count = Message.objects.filter(user=request.user).count()
        chat_histories = Message.objects.filter(user=request.user).order_by('timestamp')[max(0, message_count-10):message_count]

        context['chat_histories'] = chat_histories

        return render(request, 'myapp/home.html', context)
        
    #GET
    else:
        # ユーザーの過去の会話履歴を取得
        message_count = Message.objects.filter(user=request.user).count()
        chat_histories = Message.objects.filter(user=request.user).order_by('timestamp')[max(0, message_count-10):message_count]
        
        params = {
            "UserID": request.user,
            "chat_histories": chat_histories,
        }
        return render(request, "myapp/home.html", context=params)

#ChatSessionを削除してHomeにリダイレクト
@login_required
def delete_session(request):
    try:
        account = request.user.account
        chat_session = ChatSession.objects.get(user_account=account)
        chat_session.delete()
        messages.success(request, "ChatSessionを削除しました。")
    except ChatSession.DoesNotExist:
        messages.error(request, "ChatSessionが見つかりませんでした。")
    return redirect("myapp:home")  # 'home'はhomeビューのURL名です。


#新規登録
class  AccountRegistration(TemplateView):

    def __init__(self):
        self.params = {
        "AccountCreate":False,
        "account_form": AccountForm(),
        "add_account_form":AddAccountForm(),
        }

    #Get処理
    def get(self,request):
        self.params["account_form"] = AccountForm()
        self.params["add_account_form"] = AddAccountForm()
        self.params["AccountCreate"] = False
        return render(request,"myapp/register.html",context=self.params)

    #Post処理
    def post(self,request):
        self.params["account_form"] = AccountForm(data=request.POST)
        self.params["add_account_form"] = AddAccountForm(data=request.POST)

        #フォーム入力の有効検証
        if self.params["account_form"].is_valid() and self.params["add_account_form"].is_valid():
            # アカウント情報をDB保存
            account = self.params["account_form"].save()
            # パスワードをハッシュ化
            account.set_password(account.password)
            # ハッシュ化パスワード更新
            account.save()

            # 下記追加情報
            add_account = self.params["add_account_form"].save(commit=False)
            # AccountForm & AddAccountForm 1vs1 紐付け
            add_account.user = account

            # 画像アップロード有無検証
            if 'account_image' in request.FILES:
                add_account.account_image = request.FILES['account_image']

            # モデル保存
            add_account.save()

            # アカウント作成情報更新
            self.params["AccountCreate"] = True

        else:
            # フォームが有効でない場合
            print(self.params["account_form"].errors)

        return render(request,"myapp/register.html",context=self.params)
    

def docs(request):
    return render(request, 'myapp/docsbot.html')