# Create your views here.
import random
import logging
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from questionnaire.models import *
logger=logging.getLogger("questionnair")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

def index(request):
    titles=Title.objects.all()
    return render_to_response('questionnaire/index.html',{'titles':titles})

def prelude(request,titleid):
    title=Title.objects.get(id=int(titleid))
    if title.ttype=='T1':
        if TitleExinfo.objects.filter(title=title,attr='QDESC'):
            questions=Question.objects.filter(title=title).order_by('-qindex').values('qindex')
        else:
            questions=Question.objects.filter(title=title).order_by('qindex').values('qindex')
        te=TitleExinfo.objects.filter(title=title,attr__startswith='QMAX')
        if len(te)>0:
            maxcount=int(te[0].attr[4:])
        else:
            maxcount=Question.objects.filter(title=title).count()
        if TitleExinfo.objects.filter(title=title,attr='ARND'):
            request.session['CHOICERANDOM']=1
        else:
            request.session['CHOICERANDOM']=0
        qqueue=[]
        for i in range(maxcount):
            qqueue.append(questions[i]['qindex'])
        if TitleExinfo.objects.filter(title=title,attr='QRND'):
            random.shuffle(qqueue)
        request.session['QQUEUE']=tuple(qqueue)
    if 'LASTQINDEX' in request.session:
        del request.session['LASTQINDEX']
    logger.debug(request.session['QQUEUE'])
    c=RequestContext(request,{'title':title})
    return render_to_response('questionnaire/prelude.html',c)

def doQuiz(request,titletype,titleid):
    flg_last=False
    if titletype=='T1':
        if 'LASTQINDEX' in request.session:
            choice=Answer.objects.get(question_id=int(request.session['LASTQINDEX']),aindex=request.POST['choice'])
            request.session['SCORE']+=choice.score
            request.session['SEQ'].append((request.session['LASTQINDEX'],request.POST['choice']))
        else:
            request.session['SEQ']=[]
            request.session['SCORE']=0
            request.session['QQINDEX']=0
        if request.session['QQINDEX']>=len(request.session['QQUEUE']) :
            # last question
            flg_last=True
        else:
            qqindex=request.session['QQINDEX']
            question=Question.objects.get(title_id=titleid,qindex=request.session['QQUEUE'][qqindex])
            request.session['QQINDEX']+=1
    elif titletype=='T2':
        if 'LASTQINDEX' in request.session:
            # 2nd~last question
            choice=Answer.objects.get(question_id=int(request.session['LASTQINDEX']),aindex=request.POST['choice'])
            question=choice.question_next
            request.session['SCORE']+=choice.score
            request.session['SEQ'].append((request.session['LASTQINDEX'],request.POST['choice']))
            if choice.question_id==choice.question_next_id :
                # last question
                flg_last=True
        else:
            # 1st question
            question=Question.objects.get(title_id=titleid,qindex=1)
            request.session['SEQ']=[]
            request.session['SCORE']=0
    if flg_last:
        score=request.session['SCORE']
        if TitleExinfo.objects.filter(title_id=titleid,attr='CATE'):
            resulttype='Category'
            results=Result.objects.filter(title_id=titleid).order_by('score_lo')
            for res in results:
                if res.score_lo<=score<=res.score_hi:
                    score=res.id
                    break
            else:
                score=results[0].id
        else:
            resulttype='Score'
        log=Log(title_id=titleid,result=str(score))
        log.save()
        for history in request.session['SEQ']:
            hchoice=Answer.objects.get(question_id=history[0],aindex=history[1])
            detail=LogDetail(log=log,question_id=history[0],answer=hchoice)
            detail.save()
        c=RequestContext(request,{'titletype':titletype,'resulttype':resulttype,'score':score})
        return render_to_response('questionnaire/result.html',c)
    else:
        request.session['LASTQINDEX']=question.id
        choices=list(question.current.all())
        if request.session['CHOICERANDOM']>0:
            random.shuffle(choices)
        c=RequestContext(request,{'question':question,'choices':choices})
        return render_to_response('questionnaire/quiz.html',c)
