from questionnaire.models import *
from django.db import transaction
def parseFile(filename):
    level=0
    info={}
    info['title']=''
    info['prelude']=''
    info['questions']=[]
    fh=open(filename,'rU')
    for line in fh.readlines():
        line=line.decode('UTF8')
        if line.startswith('#'):
            level+=1
        else:
            if level==1:
                #title
                info['title']+=line
            elif level==2:
                #prelude
                info['prelude']+=line
            elif level==3:
                #questions
                line=line.rstrip()
                parts=line.split(',')
                if len(parts)>6:
                    qindex=parts[0]
                    question=parts[1]
                    memo=parts[-1]
                    aindex=parts[-2]
                    #question-index,question,array of choices
                    info['questions'].append([qindex,question,[]])
                    for i in range((len(parts)-4)/2):
                        if parts[i*2+2]==aindex:
                            score=1
                            amemo=''
                        else:
                            score=0
                            amemo=memo
                        #choice-index,choice,score,next-question,memo answer
                        info['questions'][-1][2].append([parts[i*2+2],parts[i*2+3],score,qindex,amemo])
    for i in range(len(info['questions'])-1):
        for j in range(len(info['questions'][i][2])):
            info['questions'][i][2][j][3]=info['questions'][i+1][0]
    info['title']=info['title'].rstrip()
    info['prelude']=info['prelude'].rstrip()
    return info

@transaction.commit_manually
def insertDB(info):
    # begin transaction
    try:
        # insert title and prelude, get title-id
        t=Title(title=info['title'].encode('UTF8'),prelude=info['prelude'].encode('UTF8'),ttype='T1')
        t.save()
        # insert question-index and question, get question-id, generate a dict{question-index=>question-id}
        iid={}
        for i in range(len(info['questions'])):
            q=Question(question=info['questions'][i][1].encode('UTF8'),qindex=int(info['questions'][i][0]),title_id=t.id)
            q.save()
            iid[info['questions'][i][0]]=q.id
        # insert answer
        for i in range(len(info['questions'])):
            for j in range(len(info['questions'][i][2])):
                a=Answer(answer=info['questions'][i][2][j][1].encode('UTF8'),aindex=info['questions'][i][2][j][0].encode('UTF8'),score=int(info['questions'][i][2][j][2]),memo=info['questions'][i][2][j][4].encode('UTF8'),question_id=iid[info['questions'][i][0]],question_next_id=iid[info['questions'][i][2][j][3]])
                a.save()
    except:
        print('Transaction failed')
        transaction.rollback()
    else:
        print('Transaction successed')
        transaction.commit()
    # commit transaction

def main():
    info=parseFile('type1.txt')
    insertDB(info)

if __name__=='__main__':
    main()
