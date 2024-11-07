from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse, FileResponse
from django.shortcuts import render
from django.conf import settings
from .forms import UserBioForm, UploadFileForm


def procces_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", "")
    b = request.GET.get("b", "")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result": result,
    }
    return render(request, "requestdataapp/request-query-params.html", context=context)


def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, "requestdataapp/user-bio-form.html", context=context)


def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            myfile = form.cleaned_data["file"]
            if myfile.size > settings.MAX_FILE_SIZE:
                return HttpResponse(
                    'Файл слишком большой. Максимальный размер файла: {} МБ'.format(settings.MAX_FILE_SIZE / (1024 * 1024)),
                    status=400)
            fs = FileSystemStorage()
            file_name = fs.save(myfile.name, myfile)
            print("Saved file", file_name)
    else:
        form = UploadFileForm()

    context = {
        "form": form,
    }
    return render(request, "requestdataapp/file-upload.html", context=context)







