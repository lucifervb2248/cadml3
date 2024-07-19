from django.urls import path
from . import views

urlpatterns=[
    path('CDSSmain/',views.mainPage, name='mainpage'),
    path('CDSSmain/clientpage/',views.clientPage, name='clientpage'),
    path('CDSSmain/clientpage/details',views.fromFirst, name='clientpage2'),
    path('CDSSmain/clientpage/info',views.contactInfo,name='publicResult'),
    path('CDSSmain/clientpage/info/prescription',views.showPublicPres,name='publicPrescription'),
    path('CDSSmain/clinicalpage/',views.clinicalPage,name='clinicianpage'),
    path('CDSSmain/clinicalpage/info',views.doctorGets,name='clinicianResult'),
    path('CDSSmain/clinicalpage/info/prescription',views.showClinicianPres,name='clinicianPrescription'),
    path('client/contacts/',views.contactInfo,name='contacts')
]