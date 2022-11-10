from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('mailing', views.mailing, name='mailing'),
    path('template', views.template, name='template'),
    path('mail', views.mail, name='mail'),
    path('update/<int:id>', views.update, name='update'),
]