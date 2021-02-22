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
        if "command" in post:
            command = post["command"]
            if command == "/tls":
                message = chain(post)
            elif command == "/tls-init":
                message = init(post)
            elif command == "/tls-add":
                message = add(post)
            elif command == "/tls-history":
                message = history(post)
            elif command == "/tls-help":
                message = help(post)
            else:
                message = post["command"]
        else:
            message = "No command included."
    else:
        message = "POST only."

    response = JsonResponse({"response_type":"in_channel","text":message})
    # response = HttpResponse(message)
    return response


def chain(post):
    session = Session.objects.filter(userID=post["user_id"])
    if session:
        items = len(post["text"].split("　"))
        if items == 0:
            message = "三文字のひらがなの単語を入力してください。"
        else:
            kana = kanaWorkaround(post["text"])
            if isThreeLetterKana(kana):
                if isThreeLetterKanaNotEndingWithN(kana):
                    sessionGlossary = Word.objects.filter(
                        session__userID=post["user_id"])
                    if sessionGlossary.filter(kana=kana):
                        session.delete()
                        message = "既に使われた単語です。あなたの負けです。"
                    else:
                        if Word.objects.filter(kana=kana):
                            previousLastLetter = Link.objects.filter(session__userID=post["user_id"]).order_by("whenCreated").last().word.kana[2]
                            bigPreviousLastLetter = toBigKana(previousLastLetter)
                            if kana.startswith(bigPreviousLastLetter):
                                # 単語のヴァリデーションOK。リンクの登録。応答の検索。
                                Link.objects.create(session=session[0], word=Word.objects.get(kana=kana),whenCreated=timezone.now())
                                bigLastLetter = toBigKana(kana[2])
                                vocabularyMayContainTailingN = Word.objects.filter(
                                    kana__startswith=bigLastLetter).exclude(session__userID=post["user_id"])
                                usableVocabulary = vocabularyMayContainTailingN.exclude(
                                    kana__endswith="ん")
                                if usableVocabulary:
                                    retWord = random.choice(
                                        list(usableVocabulary))
                                    Link.objects.create(
                                        session=session[0], word=retWord, whenCreated=timezone.now())
                                    message = f'{retWord.kanji}({retWord.kana})'
                                elif vocabularyMayContainTailingN:
                                    session.delete()
                                    retWord = random.choice(
                                        list(vocabularyMayContainTailingN))
                                    message = f'{retWord.kanji}({retWord.kana})\n「ん」で終わる単語を使ってしまいました。\nあなたの勝ちです。'
                                else:
                                    session.delete()
                                    message = "もう使える単語が思い浮かびません。\nあなたの勝ちです。"
                            else:
                                message = """前の単語につながる単語ではありません。\n別の単語を入力してください。"""
                        else:
                            message = """辞書にない単語です。\n/tls-addで辞書に追加できます。"""
                else:
                    session.delete()
                    message = "「ん」で終わる単語です。あなたの負けです。"
            else:
                message = "単語は三文字のひらがなにしてください。"
    else:
        message = "/tls-initで新しいしりとりを始めてください。"
    print(message)
    return message


def init(post):
    oldSession = Session.objects.filter(userID=post["user_id"])
    if oldSession:
        messageFirst = "新しいしりとりを始めます。"
    else:
        messageFirst = "しりとりを始めます。"
    oldSession.delete()
    session = Session(userID=post["user_id"])
    session.save()
    usableVocabulary = Word.objects.exclude(kana__endswith="ん")
    retWord = random.choice(list(usableVocabulary))
    Link(session=session,word=retWord,whenCreated=timezone.now()).save()
    message = messageFirst+f'\n{retWord.kanji}({retWord.kana})'
    print(message)
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
smallKanaList = ["ぁ","ぃ","ぅ","ぇ","ぉ","ゃ","ゅ","ょ","ゎ",]
bigKanaList = ["あ","い","う","え","お","や","ゆ","よ","わ",]

def toBigKana(word):
    retWord = ""
    for letter in list(word):
        if letter in smallKanaList:
            retWord += bigKanaList[smallKanaList.index(letter)]
        else:
            retWord += letter
    return retWord

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


def history(post):
    session = Session.objects.filter(userID=post["user_id"])
    if session:
        links=Link.objects.filter(session__userID=post["user_id"]).order_by("whenCreated")
        if len(links) == 0:
            message = "まだ履歴はありません。"
        else:
            message="→".join(list(map((lambda x:x.word.kanji), links)))
    else:
        message = "まだセッションがありません。\n/tls-initで新しいしりとりを始めてください。"
    print(message)
    return message



def help(post):
    return """三文字しりとり Ver.1.0.0"""

# curl -X POST -d 'text=hello&command=//tls-init&user_id=taro' -s 127.0.0.1:8000
# curl "127.0.0.1:8000" --data "command=/tls-init&user_id=hoge&text=aac"
