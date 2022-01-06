from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .models import Quiz, Question, Answer
from django.db.models import Exists, OuterRef


@login_required
def index(request):
    num_quizzes = Quiz.objects.filter(owner=request.user).count()

    # create a quiz if user has none
    if num_quizzes == 0:
        quiz = Quiz(title="Demoquiz", owner=request.user)
        quiz.save()
        question = Question(text="Was schätzen Sie: Wie viele Grundschulen gibt es in Niedersachsen?", quiz=quiz, active=True, started_times=1)
        question.save()
        Answer(username="Kain Ahnung", answer="50", question=question).save()
        Answer(username="Volker Durchblick", answer="1806", question=question).save()

    # show first quiz
    first_quiz_id = Quiz.objects.filter(owner=request.user).first()
    return redirect('quiz_index', first_quiz_id.id)


@login_required
def quiz_index(request, qid):
    """Show quizmaster index page for a quiz"""
    quiz = get_object_or_404(Quiz, owner=request.user, id=qid)
    quizzes = Quiz.objects.filter(owner=request.user)
    quiz_url = request.build_absolute_uri(reverse('show', args=(quiz.code, )))
    running_questions = Question.objects.filter(quiz=quiz, active=True).order_by('-modified')
    stopped_questions = Question.objects.filter(quiz=quiz, active=False, started_times__gt=0).order_by('-modified')
    nonstarted_questions = Question.objects.filter(quiz=quiz, active=False, started_times=0).order_by('-modified')
    return render(request, 'index.html', locals())


@login_required
def new_question(request, qid):
    quiz = get_object_or_404(Quiz, owner=request.user, id=qid)
    question_text = request.POST.get('q', None)
    if not question_text:
        return redirect('index')
    question = Question(text=question_text, quiz=quiz)
    question.save()
    messages.success(request, "Frage erfolgreich angelegt.")
    return redirect('quiz_index',qid=quiz.id)


@login_required
def delete_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    quiz_url = request.build_absolute_uri(reverse('show', args=(quiz.code, )))
    question = get_object_or_404(Question, pk=question_id, quiz=quiz)
    question.delete()
    messages.success(request, "Frage erfolgreich gelöscht.")
    return redirect('quiz_index',qid=quiz.id)


@login_required
def delete_answers(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    quiz_url = request.build_absolute_uri(reverse('show', args=(quiz.code, )))
    question = get_object_or_404(Question, pk=question_id, quiz=quiz)
    question.answer_set.all().delete()
    question.started_times = 0
    question.save()
    messages.success(request, "Antworten erfolgreich gelöscht.")
    return redirect('quiz_index',qid=quiz.id)

@login_required
def start_question(request, qid):
    quiz = get_object_or_404(Quiz, owner=request.user, id=qid)
    question_id = request.GET.get('id', None)
    if question_id:
        question = get_object_or_404(Question, pk=question_id, quiz=quiz)
        question.active = True
        question.started_times += 1
        question.save()
    return redirect('quiz_index',qid=quiz.id)


@login_required
def stop_question(request, qid):
    quiz = get_object_or_404(Quiz, owner=request.user, id=qid)
    question_id = request.GET.get('id', None)
    if question_id:
        question = get_object_or_404(Question, pk=question_id, quiz=quiz)
        question.active = False
        question.save()
    return redirect('quiz_index',qid=quiz.id)


@login_required
def new_quiz(request):
    title = request.POST.get('new', None)
    if title and len(title)>0:
        q = Quiz(title=title, owner=request.user)
        q.save()
        messages.success(request, 'Neues Quiz erfolgreich angelegt.')
        return redirect('quiz_index', qid=q.id)


@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    t = quiz.title
    quiz.delete()
    messages.success(request, 'Quiz "{}" gelöscht.'.format(t))
    return redirect('index')


@login_required
def answers(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    q = get_object_or_404(Question, pk=question_id, quiz=quiz)
    return render(request, 'answers.html', locals())


class show(View):

    def get(self, request, quiz_code):
        quiz = get_object_or_404(Quiz, code=quiz_code)
        if request.GET.get('forget', 0) == '1':
            name = None
        else:
            name = request.session.get('name', None)
        if not name:
            return render(request, 'show_entername.html', locals())
        else:
            q = Question.objects.filter(~Exists(Answer.objects.filter(username=name, question=OuterRef('pk'))), quiz=quiz, active=True).first()
            return render(request, 'show_show.html', locals())

    def post(self, request, quiz_code):
        quiz = get_object_or_404(Quiz, code=quiz_code)
        if 'name' in request.POST:  # save name
            name = request.POST.get('name', None)
            if len(name) > 0:
                request.session['name'] = name
        elif 'answer' in request.POST:  # save answer
            question_id = request.POST.get('id', None)
            if question_id:
                question = get_object_or_404(Question, pk=question_id, quiz=quiz)
                answer = request.POST.get('answer', None)
                if len(answer) > 0:
                    a = Answer(question=question, username=request.session['name'], answer=answer)
                    a.save()
                    messages.success(request, "Antwort '{}' erfolgreich abgegeben.".format(answer))
                else:
                    messages.warning(request, "Ungültige Antwort.")
        return redirect('show', quiz_code=quiz.code)
