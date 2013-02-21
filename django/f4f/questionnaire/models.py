from django.db import models

# Create your models here.
class Title(models.Model):
    TitleType=(('T1','full test'),
               ('T2','dependant test'),
               )
    title = models.CharField(max_length=256,editable=False)
    prelude = models.TextField(default='',editable=False)
    pub_date = models.DateTimeField(auto_now=True,editable=False)
    ttype = models.CharField(max_length=2,choices=TitleType,editable=False)
    def __unicode__(self):
        return self.title

class TitleExinfo(models.Model):
    title = models.ForeignKey(Title)
    attr = models.CharField(max_length=32,editable=False)
    def __unicode__(self):
        return "%d:%s"%(self.title_id,self.attr)

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
    result = models.CharField(max_length=16)
    pub_date = models.DateTimeField(auto_now=True,editable=False)

class LogDetail(models.Model):
    log = models.ForeignKey(Log)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Answer)
