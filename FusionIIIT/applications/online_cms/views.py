from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from applications.globals.models import *
from applications.academic_procedures.models import *
from applications.academic_information.models import *
from .models import *
from datetime import datetime
from .forms import *
from .helpers import *
from django.conf import settings
import os
import subprocess
from django.core.files.storage import FileSystemStorage


@login_required
def viewcourses(request):
    user=request.user
    extrainfo=ExtraInfo.objects.get(user=user)
    if extrainfo.user_type == 'student':
        student=Student.objects.get(id=extrainfo)

        roll=student.id.id[:4]
        register=Register.objects.filter(student_id=student,semester=semester(roll))
        return render(request,'online_cms/viewcourses.html',{'register':register,'extrainfo':extrainfo})
    else:
        instructor=Instructor.objects.filter(instructor_id=extrainfo)
        return render(request,'online_cms/viewcourses.html',{'instructor':instructor,'extrainfo':extrainfo})


@login_required
def course(request,course_code):
    user=request.user
    extrainfo=ExtraInfo.objects.get(user=user)

    if extrainfo.user_type == 'student':
        student=Student.objects.get(id=extrainfo)
        roll=student.id.id[:4]
        course=Course.objects.filter(course_id=course_code,sem=semester(roll))
        instructor=Instructor.objects.get(course_id=course)

        return render(request,'online_cms/course.html',{'course':course[0],'instructor':instructor,'extrainfo':extrainfo})

    else:
        instructor=Instructor.objects.filter(instructor_id=extrainfo)
        instructor=Instructor.objects.filter(instructor_id=extrainfo)
        for ins in instructor:
            if ins.course_id.course_id is course_code:
                course=ins.course_id
        return render(request,'online_cms/course.html',{'instructor':instructor,'extrainfo':extrainfo})


@login_required
def add_document(request,course_code):
    print("xcxc")
    extrainfo=ExtraInfo.objects.get(user=request.user)
    if(request.method=='POST'):
        print("x")
        form=AddDocuments(request.POST,request.FILES)
        if(form.is_valid()):
            description=request.POST.get('description')
            doc=request.FILES['doc']
            filename, file_extenstion=os.path.splitext(request.FILES['doc'].name)
            full_path=settings.MEDIA_ROOT+"/doc/"+course_code
            url=settings.MEDIA_URL+filename
            if not os.path.isdir(full_path):
                cmd="mkdir "+full_path
                subprocess.call(cmd,shell=True)
            fs = FileSystemStorage(full_path,url)
            file_name = fs.save(doc.name, doc)
            uploaded_file_url = "/media/doc/"+course_code+"/"+doc.name
            instructor=Instructor.objects.filter(instructor_id=extrainfo)
            for ins in instructor:
                if(ins.course_id.course_id == course_code):
                    course=ins.course_id
                    print("YES")
            cd=CourseDocuments.objects.create(
                course_id=course,
                upload_time=datetime.now(),
                description=description,
                document_name=uploaded_file_url
            )
            return HttpResponse("ho gaya")
        elif(form.errors):
            errors=form.errors
    else:
        print("c")
        form=AddDocuments()
        return render(request,'online_cms/add_doc.html',{'form':form,'extrainfo':extrainfo})
