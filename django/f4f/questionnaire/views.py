# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from questionnaire.models import *

def index(request):
    titles=Title.objects.all()
    del request.session['LASTQINDEX']
    return render_to_response('questionnaire/index.html',{'titles':titles})

def doTest(request,titleid):
    if 'LASTQINDEX' in request.session:
        # 2nd~last question
        choice=Answer.objects.get(question_id=int(request.session['LASTQINDEX']),aindex=request.POST['choice'])
        question=choice.question_next
        request.session['SCORE']+=choice.score
        request.session['SEQ']+="#%s:%s"%(request.session['LASTQINDEX'],request.POST['choice'])
        if choice.question_id==choice.question_next_id :
            # last question
            pass
    else:
        # 1st question
        question=Question.objects.get(title_id=titleid,qindex=1)
        request.session['SEQ']=''
        request.session['SCORE']=0
    request.session['LASTQINDEX']=question.id
    choices=question.current.all()
    c=RequestContext(request,{'question':question,'choices':choices,'titleid':titleid})
    return render_to_response('questionnaire/quiz.html',c)
