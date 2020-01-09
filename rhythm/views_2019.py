from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

import json

from .models import Image
from .algorithm import re_gui21
from .algorithm import re_kdtree
# Create your views here.


def index(request):
    return render(request, 'rhythm/index.html')


def index_association(request):
    return render(request, 'rhythm/index_association.html')


def index_to_generate_image(request):
    context = {
        'dataset': '',
        'method_name': ''
    }
    return render(request, 'rhythm/index_to_generate_image.html', context)


def results(request, dataset_name, method_name, parameter):
    context = {
        'image_name': None,
    }
    # return HttpResponse(method_name + str(parameter))
    return render(request, 'rhythm/index.html', context)


def select(request):
    # get method_full_name
    post_ = request.POST
    method_name = post_['method']
    # first seven methods names
    first_seven_methods = [
        'method1',
        'method2',
        'method3',
        'method4',
        'method5',
        'method6',
        'method7'
    ]
    if method_name in first_seven_methods:
        content = deal_with_first_seven_methods(post_, method_name)
        return HttpResponse(content)
    # else:
    #     if method_name == 'trip_times_network':
    #         content = deal_with_trip_times_network(post_)
    #         return HttpResponse(content)


def deal_with_first_seven_methods(post, method_name):
    # get dataset_name
    dataset_name = post['dataset']
    if method_name == "method1":
        method_full_name = "2d_equal_grid"
    if method_name == "method2":
        method_full_name = "2d_kdtree"
    if method_name == "method3":
        method_full_name = "3d_equal_grid"
    if method_name == "method4":
        method_full_name = "3d_kdtree"
    if method_name == "method5":
        method_full_name = "3d_slice_merge"
    if method_name == "method6":
        method_full_name = "time_space"
    if method_name == "method7":
        method_full_name = "space_time"
    # get parameter
    parameter = list()
    if method_name != "method6" and method_name != "method7":
        parameter.append(int(post[method_name]))
    else:
        parameter.append(int(post[method_name + "_1"]))
        parameter.append(int(post[method_name + "_2"]))
    # get image and context
    img_full_name = dataset_name + "-" + method_full_name
    for parameter_ in parameter:
        img_full_name += "-" + str(parameter_)
    img_full_name += ".png"
    image = Image.objects.filter(
        image_full_name=img_full_name
    )
    if not image:
        img_full_name_, extra_information = re_gui21.figure_to_img(
            dataset_name, method_full_name, parameter)
        temp_image = Image(image_full_name=img_full_name_,
                           extra_information=json.dumps(extra_information),
                           upload_time=timezone.now())
        temp_image.save()
    else:
        temp_image = image[0]
    context = {
        "image_full_name": temp_image.image_full_name,
        "extra_information": temp_image.extra_information,
    }
    return json.dumps(context)


def select_to_generate_image(request):
    dataset_ = request.POST['file_name']
    method_name_ = request.POST['choice']
    method_args = {
        "2d_equal_grid": [5, 30, 5],
        "2d_kdtree": [2, 10, 1],
        "3d_equal_grid": [2, 20, 1],
        "3d_kdtree": [2, 10, 1],
        "3d_slice_merge": [5, 30, 5],
        "time_space": [[2, 24, 1], [2, 10, 1]],
        "space_time": [[3, 10, 1], [3, 10, 1]]
    }
    args_ = method_args[method_name_]
    if method_name_ == "time_space" or method_name_ == "space_time":
        for i in range(args_[0][0], args_[0][1] + args_[0][2], args_[0][2]):
            for j in range(args_[1][0], args_[1][1] + args_[1][2], args_[1][2]):
                img_full_name_, extra_information = re_gui21.figure_to_img(
                    dataset_, method_name_, list([i, j]))
                temp_image = Image(image_full_name=img_full_name_,
                                   extra_information=json.dumps(
                                       extra_information),
                                   upload_time=timezone.now())
                temp_image.save()  
    else:
        for i in range(args_[0], args_[1] + args_[2], args_[2]):
            img_full_name_, extra_information = re_gui21.figure_to_img(dataset_, method_name_, list([i]))
            temp_image = Image(image_full_name=img_full_name_,
                    extra_information=json.dumps(extra_information),
                    upload_time=timezone.now())
            temp_image.save()
    context = {
        'dataset': dataset_,
        'method_name': method_name_
    }
    # return 
    return render(request, 'rhythm/index_to_generate_image.html', context)