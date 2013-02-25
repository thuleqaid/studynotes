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
    exinfo=_get_title_attr_(titleid)
    if title.ttype=='T1':
        if 'QDESC' in exinfo:
            questions=Question.objects.filter(title=title).order_by('-qindex').values('qindex')
        else:
            questions=Question.objects.filter(title=title).order_by('qindex').values('qindex')
        if 'QMAX' in exinfo:
            maxcount=exinfo['QMAX']
        else:
            maxcount=Question.objects.filter(title=title).count()
        if 'ARND' in exinfo:
            request.session['CHOICERANDOM']=1
        else:
            request.session['CHOICERANDOM']=0
        qqueue=[]
        for i in range(maxcount):
            qqueue.append(questions[i]['qindex'])
        if 'QRND' in exinfo:
            random.shuffle(qqueue)
        request.session['QQUEUE']=tuple(qqueue)
    if 'LASTQINDEX' in request.session:
        del request.session['LASTQINDEX']
    logger.debug(request.session['QQUEUE'])
    c=RequestContext(request,{'title':title})
    return render_to_response('questionnaire/prelude.html',c)

def _get_title_attr_(titleid):
    exinfo={}
    for tinfo in TitleExinfo.objects.filter(title_id=titleid).values('attr'):
        attr=tinfo['attr'].upper()
        if attr.isalpha():
            exinfo[attr]=1
        else:
            parts=attr.split('=',2)
            if len(parts)>=2:
                exinfo[parts[0]]=int(parts[1])
    return exinfo

def _save_log(titleid,score,details):
    exinfo=_get_title_attr_(titleid)
    if 'CATE' in exinfo:
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
    for history in details:
        hchoice=Answer.objects.get(question_id=history[0],aindex=history[1])
        detail=LogDetail(log=log,question_id=history[0],answer=hchoice)
        detail.save()
    return (resulttype,score)

def doQuiz(request,titletype,titleid):
    ftable={'T1':_doQuiz_T1,
            'T2':_doQuiz_T2,
            }
    if titletype in ftable:
        return ftable[titletype](request,titleid)

def _doQuiz_T1(request,titleid):
    if 'LASTQINDEX' in request.session:
        # 2nd~last question
        choice=Answer.objects.get(question_id=int(request.session['LASTQINDEX']),aindex=request.POST['choice'])
        request.session['SCORE']+=choice.score
        request.session['SEQ'].append((request.session['LASTQINDEX'],request.POST['choice']))
    else:
        # 1st question
        request.session['SEQ']=[]
        request.session['SCORE']=0
        request.session['QQINDEX']=0
    if request.session['QQINDEX']>=len(request.session['QQUEUE']) :
        # last question
        resulttype,score=_save_log(titleid,request.session['SCORE'],request.session['SEQ'])
        c=RequestContext(request,{'titletype':'T1','resulttype':resulttype,'score':score})
        return render_to_response('questionnaire/result.html',c)
    else:
        qqindex=request.session['QQINDEX']
        question=Question.objects.get(title_id=titleid,qindex=request.session['QQUEUE'][qqindex])
        request.session['QQINDEX']+=1
        request.session['LASTQINDEX']=question.id
        choices=list(question.current.all())
        if request.session['CHOICERANDOM']>0:
            random.shuffle(choices)
        c=RequestContext(request,{'question':question,'choices':choices})
        return render_to_response('questionnaire/quiz.html',c)

def _doQuiz_T2(request,titleid):
    if 'LASTQINDEX' in request.session:
        # 2nd~last question
        choice=Answer.objects.get(question_id=int(request.session['LASTQINDEX']),aindex=request.POST['choice'])
        question=choice.question_next
        request.session['SCORE']+=choice.score
        request.session['SEQ'].append((request.session['LASTQINDEX'],request.POST['choice']))
        if choice.question_id==choice.question_next_id :
            # last question
            resulttype,score=_save_log(titleid,request.session['SCORE'],request.session['SEQ'])
            c=RequestContext(request,{'titletype':'T2','resulttype':resulttype,'score':score})
            return render_to_response('questionnaire/result.html',c)
    else:
        # 1st question
        question=Question.objects.get(title_id=titleid,qindex=1)
        request.session['SEQ']=[]
        request.session['SCORE']=0
    request.session['LASTQINDEX']=question.id
    choices=list(question.current.all())
    if request.session['CHOICERANDOM']>0:
        random.shuffle(choices)
    c=RequestContext(request,{'question':question,'choices':choices})
    return render_to_response('questionnaire/quiz.html',c)
