from django.urls import path
from products import views

urlpatterns = [

    #   Products urls

    path('<str:object>/all/', views.all_objects, name='all_objects'),
    path('<str:object>/<int:id>/', views.objects, name='objects'),
    path('<str:object>/search/', views.search_objects, name='search_objects'),
    path('<str:object>/add/', views.add_objects, name='add_objects'),
    path('<str:object>/update/<int:id>/',
         views.update_objects, name='update_objects'),
    #     path('<str:object>/batch-add/',
    #          views.batch_add_objects, name='batch_add_objects'),
    #     path('<str:object>/batch-update/<int:id>/', views.batch_update_objects,
    #          name='batch_update_objects'),
    path('<str:object>/list/', views.list_objects, name='list_objects'),

]
