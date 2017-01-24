from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from schedule.models import Calendar

from laundryapp import views as laundryapp_views

urlpatterns = []

try:
    calendar = Calendar.objects.get(id=1)
except:
    calendar = None
if calendar:
    calendarslug = calendar.slug

if calendar:
    urlpatterns = [
        url(r'^$', RedirectView.as_view(url='/schedule/calendar/month/' + calendarslug)),
        url(r'^schedule/calendar/tri_month/', RedirectView.as_view(url='/schedule/calendar/month/' + calendarslug)),
        url(r'^schedule/calendar/year/', RedirectView.as_view(url='/schedule/calendar/month/' + calendarslug)),
        url(r'^schedule/calendar/week/', RedirectView.as_view(url='/schedule/calendar/month/' + calendarslug)),
        url(r'^schedule/$', RedirectView.as_view(url='/schedule/calendar/month/' + calendarslug)),
    ]

urlpatterns += [
    url(r'^contactadmin/', TemplateView.as_view(template_name='laundryapp/contactadmin.html')),
    url(r'^schedule/event/delete/(?P<event_id>\d+)/$',
        laundryapp_views.LaundryDeleteEventView.as_view(),
        name="delete_event"),
    url(r'^schedule/event/create/(?P<calendar_slug>[-\w]+)/$',
        laundryapp_views.LaundryCreateEventView.as_view(),
        name='calendar_create_event'),
    url(r'^schedule/event/edit/(?P<calendar_slug>[-\w]+)/(?P<event_id>\d+)/$',
        laundryapp_views.LaundryEditEventView.as_view(),
        name='edit_event'),
    url(r'^schedule/mybookings/$',
        laundryapp_views.LaundryMyBookings.as_view(),
        name='mybookings'),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^schedule/', include('schedule.urls')),
]
