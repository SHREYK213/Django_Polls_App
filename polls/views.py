from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.views import generic
from .models import Choice, Question,Tag
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core import serializers
from django.db.models import Sum
import json
from django.db.models import Count


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.order_by("-pub_date")[:5]



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
    try:
        if request.method == 'POST':
            jbody = json.loads(request.body)
            question_text = jbody["question_text"]
            choices = jbody["choice_text"]
            tags = jbody["tags"]

            # question_text = request.POST.get('question_text')
            # choices = request.POST.getlist('choice_text')
            # tags = request.POST.getlist('tags')
            print(question_text)
            print(choices)
            print(tags)
            if question_text and choices:
                question = Question(question_text=question_text, pub_date=timezone.now())
                question.save()
                for choice_text in choices:
                    if choice_text:
                        choice = Choice(question=question, choice_text=choice_text, votes=0)
                        choice.save()
                for tag_name in tags:
                    if tag_name:
                        tags = Tag(question=question,tag_name=tag_name)                        
                        tags.save()

                return HttpResponseRedirect(reverse('polls:detail', args=(question.id,)))
        return render(request, 'polls/create.html')
    except Exception as e:
        print(e)

@csrf_exempt 
def edit_poll(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    
    if request.method == 'PUT':
        request_data = json.loads(request.body)
        question_text = request_data.get('question_text')
        choices = request_data.get('choice_text')
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
        return JsonResponse({'error':'Invalid request data'})
    return JsonResponse({'error':'Invalid request method'})


# class IndexView(generic.ListView):
#     template_name = "polls/index.html"
#     context_object_name = "latest_question_list"

#     def get_queryset(self):
#         tags = self.request.GET.getlist('tags')
#         if tags:
#             return Question.objects.filter(tag__tag_name__in=tags).distinct().order_by('-pub_date')[:7]
#         else: 
#             return Question.objects.order_by('-pub_date')[:7]

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         tags = Tag.objects.all()
#         context['tags'] = tags
#         return context

 
def get_tag(request):
    tags = Tag.objects.all()
    tag_list = [{'id': tag.id, 'tag_name': tag.tag_name} for tag in tags]
    return JsonResponse({'tags': tag_list})



class TagListView(generic.ListView):
    template_name = "polls/tags_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.all()



def get_questions(request):
    tag_names = request.GET.get('tags', '')
    if tag_names:
        if ',' in tag_names:
            tag_names = tag_names.split(',')
        else:
            tag_names = [tag_names]
        
        print(tag_names)
        tags = Tag.objects.filter(tag_name__in=tag_names).select_related('question')
        question_ids = [] 
        questionIdTagsMap={} 
        
        for tag in tags:
            print(tag.tag_name)
            question_ids.append(tag.question.id)    
        print(questionIdTagsMap)
        question_ids = list(set(question_ids))
        print("qid",question_ids)
        
        for each_id in question_ids:
            tags = Tag.objects.filter(question_id=each_id).values_list('tag_name', flat=True)
            tag_list = list(tags)
            print('taglist:',tag_list)
            questionIdTagsMap[each_id] = tag_list
        print(questionIdTagsMap)
        questions = Question.objects.filter(id__in=question_ids)
        print(questions)

        data = []
        print(questionIdTagsMap)
        
        for question in questions:
            print('ID:',question.id)
            total_votes = Question.objects.filter(id=question.id).aggregate(Sum('choice__votes'))['choice__votes__sum']
            qtag=questionIdTagsMap.get(question.id)
            print('qtag',qtag)
            data.append({

                'question_text': question.question_text,
                'tag_name': qtag,
                'total_votes':total_votes
            })
        print(data)
        return JsonResponse({'data': data})

    else:

        questions=Question.objects.all()
        
        data=[]
        
        
        print(questions)
        for question in questions:
            total_votes = Question.objects.filter(id=question.id).aggregate(Sum('choice__votes'))['choice__votes__sum']
            tags = Tag.objects.filter(question_id=question.id).values_list('tag_name', flat=True)
            tag_list = list(tags)
            print('taglist from else:',tag_list)
            data.append({
                'question_text':question.question_text,
                'tag_name':tag_list,
                'total_votes':total_votes
            })
        print(data)
        return JsonResponse({'data': data})


def get_all(request):
    questions = Question.objects.all().distinct()
            
    data = []
            
    for question in questions:
        total_votes = Question.objects.filter(id=question.id).aggregate(Sum('choice__votes'))['choice__votes__sum']
        tags = Tag.objects.filter(question_id=question.id).values_list('tag_name', flat=True)
        tag_list = list(tags)
        data.append({
            'question_text': question.question_text,
            'tag_name': tag_list,
            'total_votes': total_votes
        })
    return JsonResponse({'data': data})
