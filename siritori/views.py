import random, json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

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

def returnWord(request):
    # body = json.dumps(request.body)
    # post = request.post
    return HttpResponse(json.dumps(request.POST))
    # return HttpResponse("aaaa")
    # [word, command] = request.text.split(" ")
    # return HttpResponse("word:"+word+",command:"+command)

# def validateWord(word):
    # 三文字か、んで終わっていないか、辞書にあるか、もう使われていないか
