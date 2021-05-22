
from django.http.response import HttpResponse, HttpResponseRedirect
from django.http import Http404, HttpResponseRedirect
from webtest.settings import TEMPLATES
from django.shortcuts import redirect, render
from django.conf import settings
from django.core.mail import send_mail
from ldap3 import *
import ssl
from loginAD.models import UserAD, passwAD
import random


def deleteAllDB():

    UserAD.objects.all().delete()
    passwAD.objects.all().delete()

    return
#  connect to AD


def connect(userAD, passAD):
    LDAP_URL = '192.168.1.11'
    tls_configuration = Tls(validate=ssl.CERT_NONE,
                            version=ssl.PROTOCOL_TLSv1_2)
    ser = Server(LDAP_URL, port=636, use_ssl=True,
                 get_info=ALL, tls=tls_configuration)
    conn = Connection(ser, userAD, passAD)
    conn.start_tls()
    conn.bind()
    # NameAu = conn.extend.standard.who_am_i()
    return conn

# tạo token


def make_token():
    x = 0
    token = ''
    while x < 6:
        token = token + str(random.randint(0, 9))
        x = x + 1
    return token


# insert user pw và token vào khi xác thực thành công


def save_UserPw_token(userAD, passAD, tokenAD):
    try:
        x = UserAD(usernameAD=userAD, tokenAD=tokenAD)
        x.save()
        y = passwAD(pwAD=passAD, tokenAD=tokenAD)
        y.save()
        return x.save()
    except:
        check = 'Failed'
        return check

# send email token


def send_EmailToken(userAD, passAD, tokenAD):
    # send email
    try:
        conn = connect(userAD, passAD)

        LDAP_FILTER = '(cn=' + userAD + ')'
        LDAP_ATTRS = ['mail']
        conn.search('DC=htcglobal,DC=com,DC=vn',
                    LDAP_FILTER, attributes=LDAP_ATTRS)
        x = conn.entries
        # conver list to string
        email = ''.join(map(str, x[0]))
        # email = 'dung2000hl2@gmail.com'
        # conn.unbind()
        subjects = 'check Change password AD'
        messages = ('Input this to input Token authencation: ' + tokenAD)
        email_from = settings.EMAIL_HOST_USER
        recepient = email
        send_mail(subjects, messages, email_from, [
                  recepient], fail_silently=False)
        check = 'True'
        return check
    except:
        check = "False"
        return check
# xác thực token thông qua ng dùng nhập


def Authen_Token(token):
    # lấy token lưu trc đó ra TK
    x = "False"
    try:
        u = UserAD.objects.get(tokenAD=token)
        # u = passwAD.objects.get(tokenAD=token)
        return u
    except:
        raise Http404(x)

    # True neu dung False nếu sai


def test(request):
    # username = 'web'
    # # passw = 'D@kuhebi1108//'  # 'Bf_^$y3TVkbr*LX8'
    # # x = connect(username, passw)
    # # token = make_token()
    # xx = Authen_Token('498569')
    # x = str(xx)
    # if x == username:
    return render(request, 'loginAD/success.html')

    # return HttpResponse("s"+xx)

# change password of user


def ChangePw_AD(userAD, passAD, new_passAD):

    # #  connect
    conn = connect(userAD, passAD)
    enc_pwd = '"{}"'.format(new_passAD).encode('utf-16-le')
    changes = {'unicodePwd': [(MODIFY_REPLACE, [enc_pwd])]}
    try:
        # Change pass
        userADx = 'CN=' + userAD + ',OU=Zimbra,DC=htcglobal,DC=com,DC=vn'
        conn.modify(userADx, changes=changes)
        conn.unbind()
        Check = 'True'
        return Check
    except:
        Check = 'False'
        conn.unbind()
        return Check


def ChangPw(request):
    # userAD = 'web'
    # passAD = 'Bf_^$y3TVkbr*LX8'

    if request.method == 'POST':
        # try:
        # lay opt tu ng nhap
        tokenAD = request.POST["OPT"]
        # lay tokenAD tren dung ham Authen_Token de lay user
        # user = Authen_Token(tokenAD)
        userAD = UserAD.objects.get(tokenAD=tokenAD)

        # check laiOPT luu trong data co trung k nha ra ten user dung la dc
        if str(Authen_Token(tokenAD)) == str(userAD):
            newpassAD = request.POST["password"]
            newpassAD = str(newpassAD)
            passAD = passwAD.objects.get(tokenAD=tokenAD)
            passAD = str(passAD)
            userAD = str(userAD)
            # nhet userAD vo day vi doi pass word phai day du thong tin nhu duoi
            # userADx = 'CN=' + userAD + \
            #     ',OU=Zimbra,DC=htcglobal,DC=com,DC=vn'
            try:

                ChangePw_AD(userAD, passAD, newpassAD)
                deleteAllDB()
                return HttpResponseRedirect('/success/')
            except:
                return Http404('pass no change')

            # return HttpResponse(str(Authen_Token(tokenAD)))
        else:
            raise Http404("OPT does not exist ")
        # raise Http404('pass no change')
    # except:
        # return render(request, 'loginAD/changePw.html')
        # return render(request, 'loginAD/changePw.html')
    return render(request, 'loginAD/changePw.html')
    # return HttpResponse(userADx)

# ham index goi vao login


def Index(request):
    if request.method == 'POST':
        # get user pass
        userAD = request.POST["username"]
        passAD = request.POST["password"]
        # userAD = 'web'
        # passAD = 'Bf_^$y3TVkbr*LX8'
    # try:
        c = connect(userAD, passAD)
        if c.bind() == True:
            # goi ham tao token
            tokenAD = make_token()
            # lưu token
            if save_UserPw_token(userAD, passAD, tokenAD) == None:
                # gửi email
                if send_EmailToken(userAD, passAD, tokenAD) == 'True':
                    # chuyen den trang nhap OPT
                    return HttpResponseRedirect('/changpass/')
                else:
                    raise Http404("No email in user")
            else:
                raise Http404("Saving infor faile ")
        else:
            raise Http404("User does not exist")

    # except:
    #    raise Http404("ERRO user")

    return render(request, 'loginAD/login.html')
