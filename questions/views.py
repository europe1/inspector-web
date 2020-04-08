from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.utils.translation import gettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone, html

from .models import *
from .forms import CreateQuestionForm, CreateAnswerForm, EditQuestionForm
from listings.helper_functions import resize_image

def index(request):
    search = request.GET.get('search')
    if search:
        search = html.escape(search)
        questions = Question.objects.filter(text__contains=search).order_by('-date_added')
    else:
        questions = Question.objects.order_by('-date_added')

    return render(request, 'questions/index.htm', {
        'username': request.user.get_username(),
        'questions': questions
    })

def redirect_to_index(request):
    return HttpResponseRedirect(reverse('question_list'))

def question(request, question_id):
    selected_question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(target_question=selected_question).order_by('-rating')

    if selected_question.selected_answer:
        answers = answers.exclude(pk=selected_question.selected_answer.id)

    # Counts views from authenticated users
    authenticated = request.user.is_authenticated
    if authenticated:
        QuestionView.objects.get_or_create(question=selected_question, user=request.user)
    view_count = QuestionView.objects.filter(question=selected_question).count()

    try:
        user_answer = answers.get(username=request.user.get_username())
    except ObjectDoesNotExist:
        # User hasn't answered this question
        user_answer = None

    if request.method == 'POST':
        if selected_question.username == request.user.get_username():
            return HttpResponse('You can\'t answer your own question')

        answer_form = CreateAnswerForm(request.POST)
        if answer_form.is_valid():
            if len(answer_form.cleaned_data['answer_text']) < 5:
                answer_form.add_error('answer_text', _('The answer is too short'))
            elif len(answer_form.cleaned_data['answer_text']) > 500:
                answer_form.add_error('answer_text', _('The answer is too long'))
            if user_answer:
                answer_form.add_error(None, _('You have already answered this question'))
            if len(answer_form.errors) == 0:
                new_answer = Answer(
                    target_question = selected_question,
                    username = request.user.get_username(),
                    text = answer_form.cleaned_data['answer_text']
                )
                new_answer.save()
                return HttpResponseRedirect(reverse('question', args=[question_id]))
    else:
        answer_form = CreateAnswerForm()
    return render(request, 'questions/question.htm', {
        'question': selected_question,
        'answers': answers,
        'answer_form': answer_form,
        'user_answer': user_answer,
        'views': view_count,
        'self_question': selected_question.username == request.user.get_username(),
        'authenticated': authenticated
    })

def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    answers = Answer.objects.filter(target_question=question)
    same_user = request.user.get_username() == question.username
    has_answers = len(answers) > 0
    if not same_user:
        return HttpResponseRedirect(reverse('question', args=[question_id]))
    elif has_answers:
        return HttpResponse(_('You cannot delete question that already has answers'))
    if request.method == 'POST' and same_user and not has_answers:
        question.delete()
        return HttpResponseRedirect(reverse('question_list'))
    return render(request, 'questions/delete.htm', {'question': question})

# Duplicate code (answer_edit)
def question_edit(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if question.username != request.user.get_username():
        return HttpResponseRedirect(reverse('question', args=[
            question.id
        ]))
    elif question.selected_answer:
        return HttpResponse('You have already chosen the correct answer')
    elif question.date_edited:
        return HttpResponse('You have already edited your question')

    if request.method == 'POST':
        question_form = EditQuestionForm(request.POST, request.FILES, instance=question)
        if question_form.is_valid():
            if len(question_form.cleaned_data['text']) < 6:
                question_form.add_error('text', 'The text is too short')
            else:
                question.date_edited = timezone.now()
                question_form.save()
                if question.attached_image:
                    resize_image(question.attached_image.path, 640)
                return HttpResponseRedirect(reverse('question', args=[
                    question.id
                ]))
    else:
        question_form = EditQuestionForm(instance=question)
    return render(request, 'questions/edit.htm', {
        'answer': False,
        'id': question.id,
        'form': question_form
    })

@login_required
def question_create(request):
    if request.method == 'POST':
        question_form = CreateQuestionForm(request.POST, request.FILES)
        today_questions = Question.objects.filter(username=request.user.get_username(),
            date_added__date=timezone.now().date())
        if len(today_questions) >= 10:
            question_form.add_error(None, _('You have reached your daily limit'))
        if question_form.is_valid():
            question_text = question_form.cleaned_data['question_text']
            # Checks if question with the same text have already been created today
            for today_question in today_questions:
                if question_text.lower()[2:-2] in today_question.text.lower():
                    question_form.add_error(None, _('Same question already exists'))
                    break
            if len(question_text) < 15:
                question_form.add_error('question_text', _('The question is too short'))
            elif len(question_text) > 255:
                question_form.add_error('question_text', _('The question is too long'))
            if len(question_form.errors) == 0:
                new_question = Question(
                    text = question_form.cleaned_data['question_text'],
                    attached_image = question_form.cleaned_data['image'],
                    tags = question_form.cleaned_data['tags'],
                    username = request.user.get_username()
                )
                new_question.save()
                if new_question.attached_image:
                    resize_image(new_question.attached_image.path, 640)
                return HttpResponseRedirect(reverse('question', args=[
                    new_question.id
                ]))
    else:
        question_form = CreateQuestionForm()
    return render(request, 'questions/create.htm', {'form': question_form})

def answer_edit(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if answer.username != request.user.get_username():
        return HttpResponseRedirect(reverse('question', args=[
            answer.target_question.id
        ]))

    is_selected = Question.objects.filter(selected_answer=answer).exists()
    if is_selected:
        return HttpResponse('Answer is already a solution')
    elif answer.date_edited:
        return HttpResponse('You have already edited your answer')

    if request.method == 'POST':
        edit_text = request.POST.get('edit_text').strip()
        if len(edit_text) < 6:
            return HttpResponse('The text is too short')
        else:
            answer.text = edit_text
            answer.date_edited = timezone.now()
            answer.save()
            return HttpResponseRedirect(reverse('question', args=[
                answer.target_question.id
            ]))
    return render(request, 'questions/edit.htm', {
        'answer': True,
        'id': answer.id,
        'text': answer.text
    })

@login_required
def answer_rating(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if answer.username == request.user.get_username():
        return HttpResponse('You can\'t vote on your own answers')
    get_upvote = request.GET.get('upvote')
    if get_upvote:
        if int(get_upvote) == 1:
            upvote = True
        elif int(get_upvote) == 0:
            upvote = False
        else:
            return HttpResponse('Invalid parameter')

        try:
            user_rating = AnswerRating.objects.get(answer=answer, user=request.user)
            rated = True
        except ObjectDoesNotExist:
            user_rating = AnswerRating(answer=answer, user=request.user, plus=upvote)
            user_rating.save()
            rated = False
        if rated:
            return HttpResponse('You have already voted on this answer')
        else:
            if upvote:
                answer.rating += 1
            else:
                answer.rating -= 1
            answer.save()
    return HttpResponseRedirect(reverse('question', args=[
        answer.target_question.id
    ]))

def answer_delete(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if answer.username == request.user.get_username():
        if answer.rating < 5:
            is_selected = Question.objects.filter(selected_answer=answer).exists()
            if is_selected:
                return HttpResponse('Answer is already a solution')
            else:
                answer.delete()
        else:
            return HttpResponse('You can\'t delete answer which is rated higher than 4')
    return HttpResponseRedirect(reverse('question', args=[
        answer.target_question.id
    ]))

def answer_select(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    question = answer.target_question
    if question.username == request.user.get_username():
        if not question.selected_answer:
            question.selected_answer = answer
            question.save()
        else:
            return HttpResponse('Question already has a solution')
    return HttpResponseRedirect(reverse('question', args=[
        question.id
    ]))
