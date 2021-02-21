from django.db import models


class Session(models.Model):
    userID = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.userID


class Word(models.Model):
    session = models.ManyToManyField(Session, through="Link")
    kana = models.CharField(max_length=50)
    kanji = models.CharField(max_length=50)

    def __str__(self):
        return self.kana


class Link(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    whenCreated = models.DateTimeField()

    def __str__(self):
        return self.word.kana
