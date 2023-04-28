from django.http import HttpResponse, HttpResponseRedirect,JsonResponse,HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from django.views import generic
from .models import Choice, Question,Tag
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core import serializers
from django.db.models import Sum
import json
from django.views import View
from django.db.models import Count


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        return Question.objects.order_by("-pub_date")[:5]



# class DetailView(generic.DetailView):
#     model = Question
#     template_name = "polls/details.html"
    
    

# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = "polls/results.html"


# def vote(request, pk):
#     question = get_object_or_404(Question, pk=pk)
#     print(question)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST["choice"])
#     except (KeyError, Choice.DoesNotExist):
#         return render(
#             request,
#             "polls/detail.html",
#             {
#                 "question": question,
#                 "error_message": "You didn't select a choice.",
#             },
#         )
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

@csrf_exempt 
def create_poll(request):
    try:
        if request.method == 'POST':
            jbody = json.loads(request.body)
            print('after jbodu',jbody)
            question_text = jbody["question_text"]
            choices = jbody["choice_text"]
            tags = jbody["tags"]

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

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Missing question or choices'}, status=400)
            
        if request.method == 'GET': 
            return render(request, 'polls/create.html')
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'An error occurred'}, status=500)



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
                'total_votes':total_votes,
                'id':question.id

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
                'total_votes':total_votes,
                'id':question.id
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
            'total_votes': total_votes,
            'id':question.id
        })
    print('alldata:',data)
    return JsonResponse({'data': data})


# def get_allwpk(request,pk):
#     questions = Question.objects.all().distinct()
            
#     data = []
            
#     for question in questions:
#         total_votes = Question.objects.filter(pk=question.id).aggregate(Sum('choice__votes'))['choice__votes__sum']
#         data.append({
#             'question_text': question.question_text,
#             'total_votes': total_votes,
#             'pk':question.id
#         })
#     print('alldatawpk:',data)
#     return JsonResponse({'data': data})


def get_allwpk(request, pk):
    question = Question.objects.filter(pk=pk).first()
    if not question:
        return JsonResponse({'error': 'Question not found'}, status=404)
    
    total_votes = question.choice_set.aggregate(Sum('votes'))['votes__sum'] or 0
    data = [{
        'question_text': question.question_text,
        'total_votes': total_votes,
        'pk': question.pk,
    }]
    
    return JsonResponse({'data': data})



# class DetailView(View):
#     def get(self, request, pk):
#         question = get_object_or_404(Question, pk=pk)
#         choices = question.choice_set.all()
#         tags = question.tag_set.all().values_list('tag_name', flat=True)
        
#         data = {
#             'question': question.question_text,
#             'choices': list(choices.values()),
#             'tags': list(tags),
#         }
#         print('this is from the details dict',data)
        
#         return JsonResponse(data)



class DetailView(View):
    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        choices = question.choice_set.all()
        tags = question.tag_set.all().values_list('tag_name', flat=True)
        
        data = {
            'question': question.question_text,
            'choices': list(choices.values()),
            'tags': list(tags),
        }
        
        if 'application/json' in request.META['HTTP_ACCEPT']:
            return JsonResponse(data)
        else:
            return render(request, 'polls/details.html', {'data': data})

# @csrf_exempt 
# def vote(request, pk):
#     question = get_object_or_404(Question, pk=pk)
#     choices = question.choice_set.all()
#     print(question)
#     print(choices)

#     if request.method == 'PUT':
#         # choice_id=
#         incrementOption = get_object_or_404(Choice, pk=selected_choice_pk, question=question)
#         print(incrementOption)
#         incrementOption.votes += 1
#         incrementOption.save()


#         data = {
#             'success': True,
#             'message': 'Vote added successfully.',
#             'choice': {
#                 'id': incrementOption.pk,
#                 'text': incrementOption.choice_text,
#                 'votes': incrementOption.votes,
#                 'question': {
#                     'id': question.pk,
#                     'text': question.question_text,
#                     'pub_date': question.pub_date.isoformat(),
#                 },
#             },
#         }

#         return JsonResponse(data)

#     return render(request, 'results.html', {'question': question, 'choices': choices})




# @csrf_exempt 
# def vote(request, pk):
#     question = get_object_or_404(Question, pk=pk)
#     choices = question.choice_set.all()
#     data = {
#         'question': question.question_text,
#         'choices': []
#     }
#     for choice in choices:
#         choice_data = {
#             'choice': choice.choice_text,
#             'votes': choice.votes
#         }
#         data['choices'].append(choice_data)
#         print('choice data',choice_data)
#     if request.method == 'PUT':
#         choice_id = request.PUT.get('choice')
#         if choice_id:
#             selected_choice = question.choice_set.get(pk=choice_id)
#             selected_choice.votes += 1
#             selected_choice.save()
#             data['choices'] = [
#                 {'choice': choice.choice_text, 'votes': choice.votes} 
#                 for choice in choices
#             ]
#             print('selected choice',data)
#     return JsonResponse(data)


def results(request, pk):
    question = get_object_or_404(Question, pk=pk)
    context = {'question': question}
    return render(request, 'polls/vote.html', context)


@csrf_exempt
def vote(request, pk):
    question = get_object_or_404(Question, pk=pk)
    choices = question.choice_set.all()
    data = {
        'question': question.question_text,
        'choices': []
    }
    for choice in choices:
        choice_data = {
            'choice': choice.choice_text,
            'votes': choice.votes
        }
        data['choices'].append(choice_data)
        print('choice data', choice_data)
    if request.method in ['PUT', 'POST']:
        request_data = json.loads(request.body.decode('utf-8'))
        choice_text = request_data.get('choice')
        if choice_text:
            selected_choice = question.choice_set.filter(choice_text=choice_text).first()
            if selected_choice:
                selected_choice.votes += 1
                selected_choice.save()
                data['choices'] = [
                    {'choice': choice.choice_text, 'votes': choice.votes} 
                    for choice in choices
                ]
                print('from fe',selected_choice)
                print('selected choice', data)
    return JsonResponse(data)
