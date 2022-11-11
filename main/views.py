import os
# import gmail
import openpyxl

from main.models import *
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def handle_uploaded_file(f):
    with open('some/file/' + str(f), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def index(request):
    return render(request, 'index.html')


def main(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    return HttpResponse("Hello, world. You're at the polls index.")
    # return HttpResponse("Hello, world. You're at the polls index.")


def mailing(request):
    template = Template.objects.all()

    return render(request, 'mailing.html', {"template": template})


def template(request):
    template = Template.objects.all()

    return render(request, 'template.html', {"template": template})


def update(request, id=None):
    template = Template.objects.get(id=id)
    template.template_text = request.POST.get('template_text')
    template.save()

    return redirect('template')


def mail(request):
    if os.path.exists('table.xlsx'):
        os.remove('table.xlsx')
    themes = ['Получена корреспонденция для компании ', 'Получена корреспонденция для компании ', 'Истёк договор аренды. Получена корреспонденция для компании ']
    try:
        try:
            mail_template = Template.objects.get(id=request.POST.get('template')).template_text
        except ValueError:
            return HttpResponse('Шаблон не выбран')
        tag_number = int(request.POST.get('template'))

        try:
            data = request.FILES['file']
        except FileNotFoundError:
            return HttpResponse('Файл не выбран')

        default_storage.save('table.xlsx', ContentFile(data.read()))

        wookbook = openpyxl.load_workbook('table.xlsx')

        worksheet = wookbook.active

        if None in [cell.value for cell in list(worksheet['A'])]:
            y = [cell.value for cell in list(worksheet['A'])].index(None) + 1
        else:
            y = len([cell.value for cell in list(worksheet['A'])]) + 1

        x = [cell.value for cell in list(worksheet['1'])].index(None)
        colum_names = [cell.value for cell in list(worksheet['1'])][1:x].copy()

        for i in range(2, y):
            row = [cell.value for cell in list(worksheet[str(i)])][:x]
            mails = row[0].split()
            company = row[1]
            params = row[1:]

            message = mail_template

            if tag_number == 1:
                for p in range(3):
                    if ("'.$" + colum_names[p] + ".'") in message:
                        message = message.replace("'.$" + str(colum_names[p]) + ".'", str(params[p]))
                    else:
                        return HttpResponse('Столбец ' + colum_names[p] + ' не найден в шаблоне ' + str(tag_number))
            else:
                for p in range(2):
                    if ("'.$" + colum_names[p] + ".'") in message:
                        message = message.replace("'.$" + str(colum_names[p]) + ".'", str(params[p]))
                    else:
                        return HttpResponse('Столбец ' + colum_names[p] + ' не найден в шаблоне ' + str(tag_number))

                ots_keys = colum_names[3:]
                ots_values = params[3:]
                ots = []
                for k in range(len(ots_keys)):
                    if not (ots_values[k] is None):
                        ots.append(ots_keys[k] + ' - ' + str(int(ots_values[k])))

                if not (params[2] is None):
                    ots.append(str(params[2]))

                message = message.replace("'.$ot.'", ', '.join(ots) + '.')

            for address in mails:
                subject = themes[tag_number - 1] + company
                # gmail.send_mail(address, subject, message, tag_number)

        if os.path.exists('table.xlsx'):
            os.remove('table.xlsx')

        return HttpResponse('Рассылка проведена успешно !')
    except Exception as error:
        if os.path.exists('table.xlsx'):
            os.remove('table.xlsx')
        print(error)
        return HttpResponse('Неверный формат !\nПроверьте данные и повторите снова')

    # return HttpResponse(request.POST.get('template'))
    # return redirect('mailing')
