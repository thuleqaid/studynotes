from django.db import models

# Create your models here.
class Title(models.Model):
    title = models.CharField(max_length=256,editable=False)
    prelude = models.TextField(default='',editable=False)
    pub_date = models.DateTimeField(auto_now=True,editable=False)
    def __unicode__(self):
        return self.title

class Question(models.Model):
    question = models.CharField(max_length=256,editable=False)
    qindex = models.IntegerField(editable=False)
    title = models.ForeignKey(Title)
    def __unicode__(self):
        return unicode(self.qindex)+':'+self.question
    class Meta:
        unique_together=(("title","qindex"),)

class Answer(models.Model):
    answer = models.CharField(max_length=256,editable=False)
    memo = models.TextField(default='',editable=False)
    aindex = models.CharField(max_length=1,editable=False)
    score = models.IntegerField(default=0,editable=False)
    question = models.ForeignKey(Question,related_name='current')
    question_next = models.ForeignKey(Question,related_name='next')
    def __unicode__(self):
        return unicode(self.aindex)+':'+self.answer
    class Meta:
        unique_together=(("question","aindex"),)

class Result(models.Model):
    result = models.TextField(editable=False)
    score_lo = models.IntegerField(editable=False)
    score_hi = models.IntegerField(editable=False)
    title = models.ForeignKey(Title)
    def __unicode__(self):
        return self.result

class Log(models.Model):
    title = models.ForeignKey(Title)
    result = models.ForeignKey(Result)
    pub_date = models.DateTimeField(auto_now=True,editable=False)

class LogDetail(models.Model):
    log = models.ForeignKey(Log)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
