import random
import json
import re
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import Session, Word, Link


def routing(request):
    if request.method == "POST":
        post = request.POST
        if "user_id" in post:
            command = post["command"]
            if command == "/tls":
                message = chain(post)
            elif command == "/tls-init":
                message = init(post)
            elif command == "/tls-add":
                message = add(post)
            elif command == "/tls-stats":
                message = stats(post)
            elif command == "/tls-help":
                message = help(post)
            else:
                message = post["command"]
        else:
            message = "hasNotUserID"
    else:
        message = "get"

    # response = JsonResponse({"response_type":"in_channel","text":post["text"]})
    response = HttpResponse(message)
    return response


def chain(post):
    session = Session.objects.filter(userID=post["user_id"])
    if session:
        items = len(post["text"].split("　"))
        if items == 0:
            message = "三文字のひらがなの単語を入力してください。"
        else:
            kana = kanaWorkaraound(post["text"])
            if isThreeLetterKana(kana):
                if isThreeLetterKanaNotEndingWithN(kana):
                    sessionGlossary = Word.objects.filter(
                        session__userID=post["user_id"])
                    if sessionGlossary.filter(kana=kana):
                        session.delete()
                        message = """既に使われた単語です。あなたの負けです。
            セッションを削除します。"""
                    else:
                        if Word.objects.filter(kana=kana):
                            previousLastLetter = sessionGlossary.order_by(
                                "dateAdded").last().kana[2]
                            if kana.startswith(previousLastLetter):
                                # 単語のヴァリデーションOK。応答の検索。
                                lastLetter = kana[2]
                                usableVocabulary = vocabularyMayContainTailingN.exclude(
                                    kana__endswith="ん")
                                vocabularyMayContainTailingN = Word.objects.filter(
                                    kana__startswith=lastLetter).exclude(session__userID=post["user_id"])
                                if usableVocabulary:
                                    retWordQuery = random.choice(
                                        list(usableVocabulary))
                                    Link.objects.create(
                                        session=session, word=retWordQuery, dateAdded=timezone.now())
                                    message = f'{retWordQuer.kanji}({retWordQuery.kana})'
                                elif vocabularyMayContainTailingN:
                                    retWordQuery = random.choice(
                                        list(vocabularyMayContainTailingN))
                                    message = f'{retWordQuery.kanji}({retWordQuery.kana})\n「ん」で終わる単語を使ってしまいました。\nあなたの勝ちです。'
                                else:
                                    message = "もう使える単語が思い浮かびません。\nあなたの勝ちです。"
                            else:
                                message = """前の単語につながる単語ではありません。
                別の単語を入力してください。"""
                        else:
                            message = """辞書にない単語です。
              よろしければ/tls-addで辞書に追加してください。"""
                else:
                    session.delete()
                    message = """「ん」で終わる単語です。あなたの負けです。
          セッションを削除します。"""
            else:
                message = "単語は三文字のひらがなにしてください。"
    else:
        message = "/tls-initで新しいしりとりを始めてください。"

    return message


def init(post):
    session = Session.objects.filter(userID=post["user_id"])
    session.delete()
    Session(userID=post["user_id"]).save()
    usableVocabulary = Word.objects.exclude(kana__endswith="ん")
    retWordQuery = random.choice(list(usableVocabulary))
    if session:
        messageFirst = "セッションをリセットしました。"
    else:
        messageFirst = "セッションを作成しました。"
    message = messageFirst+f'\n{retWordQuery.kanji}({retWordQuery.kana})'
    return message


def add(post):
    items = len(post["text"].split("　"))
    if items == 0:
        return "単語の読みと表記を入力してください。"
    elif items == 1:
        kana = post["text"]
        kanji = kana
    elif items == 2:
        kana, kanji = post["text"].split("　")
    else:
        kana = post["text"].split("　")[0]
        kanji = post["text"][4:]

    kana=kanaWorkaround(kana)
    print(kana)
    if isThreeLetterKana(kana):
        if Word.objects.filter(kana=kana):
            message = "その単語は既に登録されています。"
            print("Already exists")
        else:
            Word(kana=kana, kanji=kanji).save()
            message = kanji + "(" + kana + ")を登録しました。"
            print("registered")
    else:
        message = "読みは三文字のひらがなにしてください。"
    return message


kanaList = ['あ', 'い', 'う', 'え', 'お', 'か', 'き', 'く', 'け', 'こ', 'さ', 'し', 'す', 'せ', 'そ', 'た', 'ち', 'つ', 'て', 'と', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ひ', 'ふ', 'へ', 'ほ', 'ま', 'み', 'む', 'め', 'も', 'や', 'ゆ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'わ', 'を', 'ん', 'が', 'ぎ', 'ぐ', 'げ', 'ご', 'ざ', 'じ', 'ず', 'ぜ', 'ぞ', 'だ', 'ぢ', 'づ', 'で', 'ど', 'ば', 'び',
            'ぶ', 'べ', 'ぼ', 'ぱ', 'ぴ', 'ぷ', 'ぺ', 'ぽ', 'ゃ', 'ゅ', 'ょ']
asciiList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
             'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '#', '(', ')', '*', '+', '-', '<', '>', '?', '@', '^']


def kanaWorkaround(word):
    if word[0] in asciiList:
        return asciiToKana(word)
    else:
        return word


def asciiToKana(ascii):
    letters = list(ascii)
    retVal = ""
    for letter in letters:
        retVal = retVal + kanaList[asciiList.index(letter)]
    return retVal


def isThreeLetterKanaNotEndingWithN(word):
    threeKanaRegex = '[\u3041-\u309F]{2}[\u3041-\u3092\u3094-\u309F]'
    if re.compile(threeKanaRegex).fullmatch(word):
        return True
    else:
        return False


def isThreeLetterKana(word):
    threeKanaRegex = '[\u3041-\u309F]{3}'
    if re.compile(threeKanaRegex).fullmatch(word):
        return True
    else:
        return False


def stats(post):
    return ""


def help(post):
    return """三文字しりとり Ver.1.0.0"""

# curl -X POST -d 'text=hello&command=//tls-init&user_id=taro' -s 127.0.0.1:8000
