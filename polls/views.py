from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.views import generic
from .models import Choice, Question
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core import serializers


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:7]

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

@csrf_exempt 
def create_poll(request):
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        choices = request.POST.getlist('choice_text')
        if question_text and choices:
            question = Question(question_text=question_text, pub_date=timezone.now())
            question.save()
            for choice_text in choices:
                if choice_text:
                    choice = Choice(question=question, choice_text=choice_text, votes=0)
                    choice.save()
            
            return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))
    return render(request, 'polls/create.html')

@csrf_exempt 
def edit_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'PUT':
        question_text = request.POST.get('question_text')
        choices = request.POST.getlist('choice_text')
        if question_text and choices:
            question.question_text = question_text
            question.save()
            for i in range(len(choices)):
                choice_text = choices[i]
                if choice_text:
                    if i < question.choice_set.count():
                        
                        choice = question.choice_set.all()[i]
                        choice.choice_text = choice_text
                    else:
                        
                        choice = Choice(question=question, choice_text=choice_text, votes=0)
                    choice.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({'error':'Invalid request method'})
    
@csrf_exempt 
def delete_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'DELETE':
        question.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error':'Invalid request method'}) 

