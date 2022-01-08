from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .models import Quiz, Question, Answer
from django.db.models import Exists, OuterRef


@login_required
def index(request):
    """Index view for logged in users. Redirects to user's first quiz or creates demo quiz if not quiz yet."""
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
    quiz_presentation_url = request.build_absolute_uri(reverse('present', args=(quiz.code, )))
    running_questions = Question.objects.filter(quiz=quiz, active=True).order_by('-modified')
    stopped_questions = Question.objects.filter(quiz=quiz, active=False, started_times__gt=0).order_by('-modified')
    nonstarted_questions = Question.objects.filter(quiz=quiz, active=False, started_times=0).order_by('-modified')
    return render(request, 'index.html', locals())


@login_required
def new_question(request, qid):
    """Create and save new question."""
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
    """Completely delete a question and all answers."""
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    question = get_object_or_404(Question, pk=question_id, quiz=quiz)
    question.delete()
    messages.success(request, "Frage erfolgreich gelöscht.")
    return redirect('quiz_index',qid=quiz.id)


@login_required
def delete_answers(request, quiz_id, question_id):
    """Reset a question, delete all answers, stop it and set started_counter to 0"""
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    question = get_object_or_404(Question, pk=question_id, quiz=quiz)
    question.reset()
    messages.success(request, "Antworten erfolgreich gelöscht.")
    return redirect('quiz_index',qid=quiz.id)


@login_required
def start_question(request, qid):
    """Start a non-running question."""
    quiz = get_object_or_404(Quiz, owner=request.user, id=qid)
    question_id = request.GET.get('id', None)
    if question_id:
        question = get_object_or_404(Question, pk=question_id, quiz=quiz)
        question.start()
    return redirect('quiz_index',qid=quiz.id)


@login_required
def stop_question(request, qid):
    """Stop a running question."""
    quiz = get_object_or_404(Quiz, owner=request.user, id=qid)
    question_id = request.GET.get('id', None)
    if question_id:
        question = get_object_or_404(Question, pk=question_id, quiz=quiz)
        question.stop()
    return redirect('quiz_index',qid=quiz.id)


@login_required
def new_quiz(request):
    """Create and save a new, empty quiz."""
    title = request.POST.get('new', None)
    if title and len(title)>0:
        q = Quiz(title=title, owner=request.user)
        q.save()
        messages.success(request, 'Neues Quiz erfolgreich angelegt.')
        return redirect('quiz_index', qid=q.id)


@login_required
def delete_quiz(request, quiz_id):
    """Completely delete a quiz with all questions and answers."""
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    t = quiz.title
    quiz.delete()
    messages.success(request, 'Quiz "{}" gelöscht.'.format(t))
    return redirect('index')


@login_required
def answers(request, quiz_id, question_id):
    """Return a partial HTML document for AJAX update of question results."""
    quiz = get_object_or_404(Quiz, owner=request.user, id=quiz_id)
    q = get_object_or_404(Question, pk=question_id, quiz=quiz)
    return render(request, 'answers.html', locals())


class show(View):
    """The participants view."""

    def get(self, request, quiz_code):
        """Show a question (or a message that there's no question). Request username if none given yet."""
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
        """Save the username or an answer."""
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


class present(View):
    """Presentation of quiz for audience projection"""

    def get(self, request, quiz_code):
        quiz = get_object_or_404(Quiz, code=quiz_code)
        quiz_url = request.build_absolute_uri(reverse('show', args=(quiz.code,)))

        mode = "running"
        # Try first: Are there running questions? If yes, take first.
        question = Question.objects.filter(quiz=quiz, active=True).order_by('-modified').first()
        num_answers = question.answer_set.all().count() if question else 0

        # If not: Take question with answers that was stopped latest
        if not question:
            question = Question.objects.filter(Exists(Answer.objects.filter(question=OuterRef('pk'))), quiz=quiz, active=False).order_by('-modified').first()
            print("question=",question)
            if question: # if there is a stopped question with answers
                mode = "answers"
                num_answers = question.answer_set.all().count()
                answers = Answer.objects.filter(question=question).order_by('username')
                if num_answers > 10:
                    breakpoint = (num_answers+1) // 2
                else:
                    breakpoint = -1
                return render(request, 'present_answers.html', locals())

        return render(request, 'present_question.html', locals())
