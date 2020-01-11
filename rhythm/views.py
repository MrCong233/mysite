from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from json import dumps
from pandas import DataFrame
import os.path
from .DivisionMethods import interface_to_methods, process_upload_original, delete_previous_imgs

# Create your views here.


def index(request):
    return render(request, 'rhythm/index.html')


def index_association(request):
    return render(request, 'rhythm/index_association.html')


def index_test(request):
    return render(request, 'rhythm/index_test.html')


def select(request):
    # get method_name
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


def upload_csv(request):
    if "GET" == request.method:
        return HttpResponseRedirect(reverse("rhythm:index"))
    # if not GET, then proceed
    if "csv_file" not in request.FILES:
        result = {
            # 'error': "Please upload file first."
            'error': "请先上传文件."
        }
        return HttpResponse(dumps(result, ensure_ascii=False))
        # return HttpResponse(result['error'])
    csv_file = request.FILES["csv_file"]
    if not csv_file.name.endswith('.csv'):
        result = {
            # 'error': "File is not CSV type"
            'error': "该文件不是CSV格式."
        }
        return HttpResponse(dumps(result, ensure_ascii=False))
        # return HttpResponse(result['error'])
    # if file is too large, return
    file_size = csv_file.size/(10**6)
    if file_size > 40.0:
        result = {
            # 'error': "Uploaded file is too big ({:.2%} MB).".format(file_size)
            'error': "文件的大小不能超过40MB."
        }
        return HttpResponse(dumps(result, ensure_ascii=False))
        # return HttpResponse(result['error'])
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # new_row = DataFrame(chunk)
    file_path = '{}\\DivisionMethods\\dataset\\upload_original.csv'.format(
        current_dir)
    with open(file_path, 'w+') as f:
        for chunk in csv_file.chunks():
            f.write(chunk.decode("utf-8"))
    retn_result = process_upload_original.process_original_csv()
    if retn_result == 1:
        result = {
            'error': "上传的文件不符合规定格式."
        }
        return HttpResponse(dumps(result, ensure_ascii=False))
        # return HttpResponse(result['error'])
    result = {
        'error': ""
    }
    return HttpResponse(dumps(result, ensure_ascii=False))
    # return HttpResponse(result['error'])


def deal_with_first_seven_methods(post, method_name):
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
    # delete previous images
    delete_previous_imgs.delete_pngs()
    # generate img
    _, extra = interface_to_methods.interface_to_generate_img(
        "upload_processed", method_full_name, parameter, False)
    # return img info
    context = {
        # "image_full_name": img_addr,
        "extra_information": extra,
    }
    return dumps(context)
