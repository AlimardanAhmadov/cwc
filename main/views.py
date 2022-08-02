from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string

from coach.models import Coach


def index(request):
    return render(request, 'main/base.html')

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def search_coaches(request, q=None, location=None, category=None):
    page = request.GET.get('page', 1)
    if is_ajax(request=request):
        name = request.GET.get('name')
        location = request.GET.get('location')
        category = request.GET.get('category')
        
        if category is None:
            coach_lookup = Q(full_name__icontains=name) & Q(location__iexact=location)
        
        elif name is None:
            coach_lookup = Q(location__iexact=location) & Q(category__icontains=category)
        
        elif location is None:
            coach_lookup = Q(full_name__icontains=name) & Q(category__icontains=category)
        
        elif location == '' and category == '':
            coach_lookup = Q(full_name__icontains=name)

        elif location == '' and name == '':
            coach_lookup = Q(category__icontains=category)
        
        elif (location, name, category).count('') == len((location, name, category)):
            coach_lookup = False

        elif name is None and category is None:
            coach_lookup = Q(location__iexact=location)

        else:
            coach_lookup = Q(full_name__icontains=name) & Q(location__iexact=location) & Q(category__icontains=category)
        

        if coach_lookup is False:
            matching_coaches = Coach.cached_queryset()
            if matching_coaches:
                "Calling cach"
            else:
                matching_coaches = Coach.objects.select_related("user").all()
            paginator = Paginator(matching_coaches, 25)
        else:
            matching_coaches = Coach.objects.filter(coach_lookup) 
            paginator = Paginator(matching_coaches, 25)
     
        try:
            coach_list = paginator.page(page)
        except PageNotAnInteger:
            coach_list = paginator.page(1)
        except EmptyPage:
            coach_list = paginator.page(paginator.num_pages)
        
        html = render_to_string(
            template_name="main/results.html",
            context={"results": coach_list, 'num_pages': paginator.num_pages,}
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)
    else:
        matching_coaches = Coach.cached_queryset()
        if matching_coaches:
            "Calling cach"
        else:
            matching_coaches = Coach.objects.select_related("user").filter(paid=True)
        paginator = Paginator(matching_coaches, 25)
        
        try:
            coach_list = paginator.page(page)
        except PageNotAnInteger:
            coach_list = paginator.page(1)
        except EmptyPage:
            coach_list = paginator.page(paginator.num_pages)
        context = {
            'data': coach_list,
            'num_pages': paginator.num_pages,
        }

    return render(request, 'main/search.html', context)
