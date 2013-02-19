# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from questionnaire.models import *

def index(request):
    titles=Title.objects.all()
    return render_to_response('questionnaire/index.html',{'titles':titles})

def doTest(request,titleid):
    quiz={}
    print(request)
    if 'LASTQINDEX' in request.COOKIES:
        question=Question.objects.get(title_id=titleid,qindex=int(request.COOKIES['LASTQINDEX'])+1)
    else:
        question=Question.objects.get(title_id=titleid,qindex=1)
    qindex=question.qindex
    choices=question.current.all()
    request.COOKIES['LASTQINDEX']=qindex
    rc=RequestContext(request,{'LASTQINDEX':qindex})
    print(rc)
    return render_to_response('questionnaire/quiz.html',{'question':question,'choices':choices,'titleid':titleid},context_instance=rc)
