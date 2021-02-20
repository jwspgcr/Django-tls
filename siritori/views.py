import random
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from .models import Session, Word, Link

# def returnWord(request):
#     textItems = len(request.text.split(" "))
#     if textItems != 2:
#         return HttpResponse("Parse Error")
#     else:
#         [word, command]=request.text.split(" ")
#         if command=="init":
#             session = Session(key=str(random.randint(1,100000)),lastWord=word)
#             session.save()
#             return HttpResponse("init OK")
#         else:
#             session = get_object_or_404(Session, pk=command)
#             return HttpResponse("continue OK")


def routing(request):
    if request.method == "POST":
        post = request.POST
        if "command" in post:
            response = HttpResponse("hasCommand")
        else:
            response = HttpResponse("hasNotCommand")

        # command=post.__getitem__("command")
        # command = post["command"]
        # if command == "/tls":
        #     response = chain(post)
        # elif command == "/tls-init":
        #     response = init(post)
        # elif command == "/tls-add":
        #     response = add(post)
        # elif command == "/tls-stats":
        #     response = stats(post)
        # elif command == "/tls-help":
        #     response = help(post)
        # else:
        #     response = HttpResponse(post["command"])
    else:
        response = HttpResponse("get")

    # response = JsonResponse({"response_type":"in_channel","text":post["text"]})
    return response


def chain(self, post):
    return HttpResponse()


def init(post):
    session = Session.objects.filter(userID=post["user_id"])
    if session:
        session.delete()
        Session(userID=post["user_id"]).save()
        message = "セッションをリセットしました。"
    else:
        Session(userID=post["user_id"]).save()
        message = "セッションを作成しました。"
    # length=Session.objects.filter(userID=post["user_id"]).length()
    # ret=str(length)
    # except:
    #     ret=post["user_id"]
    return HttpResponse(message)


def add(post):
    word = post["text"]
    if Word.objects.filter(kana=word):
        response = "Exist"
    else:
        response = word
    return HttpResponse(response)


def stats(post):
    return HttpResponse()


def help(post):
    return HttpResponse()

# def validateWord(word):
    # 三文字か、んで終わっていないか、辞書にあるか、もう使われていないか
# curl -X POST -d 'text=hello&command=//tls-init&user_id=taro' -s 127.0.0.1:8000
