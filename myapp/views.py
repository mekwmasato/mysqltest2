from django.shortcuts import render
from django.views.generic import TemplateView #テンプレートタグ
from .forms import AccountForm, AddAccountForm, ChatGPTTemplateForm #ユーザーアカウントフォーム
from django.views import View
from .utils import chat_with_gpt


# ログイン・ログアウト処理に利用
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

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
    #POST
    if request.method == 'POST':
        # 画面に入力した文章を取得
        input_text= request.POST['input_text']
        if input_text:
            # Chat-GPTへリクエストを投げる
            response = chat_with_gpt(input_text)
            # 辞書型データを作成する
            context = {
                'input_text': input_text,
                'response': response,
                }

            # テンプレートにデータを渡す
            return render(request, 'myapp/home.html', context)
        else:
            return render(request, 'myapp/home.html')
    #GET
    else:
        params = {"UserID":request.user,}
        return render(request, "myapp/home.html",context=params)

# Create your views here.
class GrammarCorrectionView(View):
    
    def get(self, request):
        
        return render(request, 'myapp/talkchatgpt.html')
    
    def post(self, request):
        
        # 画面に入力した文章を取得
        input_text= request.POST['input_text']
        if input_text:
            # Chat-GPTに投げる命令文を生成
            #prompt = create_prompt(input_text, "GPTidol.txt") #txtデータ内の[input]を置き換えているのかも。流れの調整で連続した会話ができる可能性mekw
            # Chat-GPTへリクエストを投げる
            response = chat_with_gpt(input_text)
            # 辞書型データを作成する
            context = {
                'input_text': input_text,
                'response': response,
                }

            # テンプレートにデータを渡す
            return render(request, 'myapp/talkcha.html', context)
        else:
            return render(request, 'proofreading/grammar_correction.html')

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
            # 下記操作のため、コミットなし
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
    