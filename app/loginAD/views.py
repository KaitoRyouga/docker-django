
from django.http.response import  HttpResponseRedirect
from django.http import Http404, HttpResponseRedirect
from webtest.settings import TEMPLATES
from django.shortcuts import redirect, render
from django.conf import settings
from django.core.mail import send_mail
from ldap3 import Connection, Server,Tls, ALL, MODIFY_REPLACE
import ssl
from loginAD.models import UserAD, passwAD, total
import random


def deleteAllDB():

    UserAD.objects.all().delete()
    passwAD.objects.all().delete()

    return
#  connect to AD


def connect(userAD, passAD):
    LDAP_URL = '192.168.2.11'
    tls_configuration = Tls(validate=ssl.CERT_NONE,
                            version=ssl.PROTOCOL_TLSv1_2)
    ser = Server(LDAP_URL, port=636, use_ssl=True,
                 get_info=ALL, tls=tls_configuration)
    conn = Connection(ser, userAD, passAD)
    conn.start_tls()
    conn.bind()
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
        check = 'False'
        return check

# send email token


def send_EmailToken(userADx, passAD, tokenAD):
    # send email
    try:
        email = userADx
        # conn.unbind()
        subjects = 'Change password AD'
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
        return u
    except:
        return x

    # True neu dung False nếu sai



# change password of user


def ChangePw_AD(userAD, passAD, new_passAD):


    # lay username tu email nhap vao
    con = connect(userAD, passAD)
    NameAu = con.extend.standard.who_am_i()
    con.unbind()
    i=0
    xx=''
    while i < len(NameAu):
        if i > 11:
            xx=xx+ str(NameAu[i])
        i=i+1
    userADs = xx
    s = Server('192.168.2.11')
    US='web'
    PW='D@kuhebi1108'
    c = Connection(s, US ,PW)
    c.bind()
    # print(c.result)
    s = "(&(sAMAccountName="+userADs+"))"
    base = "OU=Zimbra,DC=htcglobal,DC=com,DC=vn"
    c.search(search_base=base, search_filter=s,
                    attributes = ["CN"], paged_size = 5)
    # print(c.result)
    x = c.entries
    # conver list to string
    userCN = ''.join(map(str, x[0]))

    # #  connect
    AD = 'CN=web,OU=Zimbra,DC=htcglobal,DC=com,DC=vn'
    conn = connect(AD, PW)
    enc_pwd = '"{}"'.format(new_passAD).encode('utf-16-le')
    changes = {'unicodePwd': [(MODIFY_REPLACE, [enc_pwd])]}
    try:
        # Change pass
        userADx = 'CN='+userCN+',OU=Zimbra,DC=htcglobal,DC=com,DC=vn'
        x=conn.modify(userADx, changes=changes)
        conn.unbind()
        Check = 'True'
        return x
    except:
        Check = 'False'
        conn.unbind()
        return Check

   


def ChangPw(request):
    if request.session.get('name'):
        if request.method == 'POST':
            # try:
            # lay opt tu ng nhap
            tokenAD = request.POST["OPT"]
            # lay tokenAD tren dung ham Authen_Token de lay user
    
            newpassAD = request.POST["password"]
            renewpassAD = request.POST["repassword"]
            if newpassAD != renewpassAD:
                return render(request, 'loginAD/changePw.html')
            try:
                userAD = UserAD.objects.get(tokenAD=tokenAD)
                
            except :
                return render(request, 'loginAD/404.html')

            # check lai OPT luu trong data co trung k nha ra ten user dung la dc
            if str(Authen_Token(tokenAD)) == str(userAD):
                
                newpassAD = str(newpassAD)
                try:
                    passAD = passwAD.objects.get(tokenAD=tokenAD)
                
                except :
                    return render(request, 'loginAD/404.html')

                passAD = str(passAD)
                userAD = str(userAD)
                # nhet userAD vo day vi doi pass word phai day du thong tin nhu duoi

                try:
                    if ChangePw_AD(userAD, passAD, newpassAD) == True:
                        # delete_session(request)
                        del request.session['name']
                        del request.session['password']

                        # numbertotal = total.objects.get(usernameAD=userAD)
                        # numbertotals = numbertotal + 1 
                        # y = total(usernameAD=userAD, totals=numbertotals)
                        # y.save()


                        deleteAllDB()
                        return render(request, 'loginAD/success.html')
                        
                    else:
                        return render(request, 'loginAD/404.html')
                except:
                    x= ChangePw_AD(userAD, passAD, newpassAD) 
                    # raise Http404('pass no change',x)
                    return render(request, 'loginAD/404.html')
                # return HttpResponse(str(Authen_Token(tokenAD)))
            else:
                # raise Http404("OPT does not exist ")
                return render(request, 'loginAD/404.html')

   
        return render(request, 'loginAD/changePw.html')
    return HttpResponseRedirect('/')
    # return render(request, 'loginAD/login.html')

# check username co chua @htcglobal.com k
def check_input_user(username):

    try:
        # neu ng dung nhap username
        s = Server('192.168.2.11')
        # uS= settings.USADs
        uS ='web'
        # pW= settings.PwADs
        pW = 'D@kuhebi1108'
        c = Connection(s, uS,pW)
        c.bind()
        # print(c.result)
        s = "(&(sAMAccountName="+username+"))"
        base = "OU=Zimbra,DC=htcglobal,DC=com,DC=vn"
        c.search(search_base=base, search_filter=s,
                        attributes = ["mail"], paged_size = 5)
        # print(c.result)
        x = c.entries
        # conver list to string
        email_user = ''.join(map(str, x[0]))
        return email_user
    except :

        return username
# ham index goi vao login


def Index(request):
    if request.method == 'POST':
        # get user pass
        userAD = request.POST["username"]
        passAD = request.POST["password"]
        userAD = check_input_user(userAD)
        # connect
        c = connect(userAD, passAD)
        
        if c.bind() == True:
            # # check so lan da doi pass
            # try:
            #     # da tung dang nhap thi
            #     numbertotal = total.objects.get(usernameAD=userAD)
            #     if numbertotal == 4:
            #         return render(request, 'loginAD/outoff.html') 
            #     # numbertotal = total.objects.get(usernameAD=userAD)

            # except :
            #     # neu chua bao gio dang nhap thi
            #     y = total(usernameAD=userAD, totals=1)
            #     y.save()

        
            # create_session(request,userAD,passAD)
            request.session['name'] = userAD
            request.session['password'] = passAD

            tokenAD = make_token()
            # lưu token
            if save_UserPw_token(userAD, passAD, tokenAD) == None:
                # gửi email
                if send_EmailToken(userAD, passAD, tokenAD) == 'True':
                    # chuyen den trang nhap OPT
                    return HttpResponseRedirect('/authen/')
                else:
                    # x=send_EmailToken(userAD, passAD, tokenAD) 
                    # raise Http404("No email in user",x)
                    return render(request, 'loginAD/404.html')
            else:
                # raise Http404("Saving infor faile ")
                return render(request, 'loginAD/404.html')
        else:
            # raise Http404("login f ",userAD)
            return render(request, 'loginAD/404.html')
    return render(request, 'loginAD/login.html')
 