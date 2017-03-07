import datetime
import sys

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.db.models import F
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.http import is_safe_url
from django.views.generic import ListView

from allauth.account.signals import user_signed_up

from schedule.conf.settings import (OCCURRENCE_CANCEL_REDIRECT,
                                    USE_FULLCALENDAR)
from schedule.models import Event
from schedule.utils import coerce_date_dict
from schedule.views import (CreateEventView,
                            CreateView,
                            DeleteEventView,
                            DeleteView,
                            EditEventView,
                            EventEditMixin,
                            UpdateView)

from laundryapp.forms import LaundryEventForm

class LaundryCancelButtonMixin(object):

    def post(self, request, *args, **kwargs):
        try:
            next_url = request.GET['next']
        except:
            next_url = None
        self.success_url = get_next_url(request, next_url)
        if "cancel" in request.POST:
            return HttpResponseRedirect(self.success_url)
        else:
            return super(LaundryCancelButtonMixin, self).post(request, *args, **kwargs)


class LaundryCreateEventView(LaundryCancelButtonMixin, CreateEventView, EventEditMixin, CreateView):

    form_class = LaundryEventForm

    def get_form_kwargs(self):
        kwargs = super(LaundryCreateEventView, self).get_form_kwargs()
        kwargs.update({'event_type': 'create'})
        return kwargs

    def get_initial(self):
        date = coerce_date_dict(self.request.GET)
        initial_data = None
        if date:
            try:
                start = datetime.datetime(**date)
                initial_data = {
                    "start": start,
                    "end": start + datetime.timedelta(minutes=60)
                }
            except TypeError:
                raise Http404
            except ValueError:
                raise Http404
        return initial_data


class LaundryDeleteEventView(DeleteEventView, EventEditMixin, DeleteView):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        event_id = self.kwargs['event_id']

        event = Event.objects.get(id=event_id)
        event_creator_id = event.creator_id
        auth_user = request.user
        auth_user_id = auth_user.id
        if event_creator_id == auth_user_id:
            self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        url_val = 'fullcalendar' if USE_FULLCALENDAR else 'day_calendar'
        next_url = self.kwargs.get('next') or reverse(url_val, args=[self.object.calendar.slug])
        next_url = get_next_url(self.request, next_url)
        return next_url


class LaundryEditEventView(EditEventView, LaundryCancelButtonMixin, EventEditMixin, UpdateView):

    form_class = LaundryEventForm
    template_name = 'schedule/create_event.html'

    def form_valid(self, form):
        event = form.save(commit=False)
        old_event = Event.objects.get(pk=event.pk)
        dts = datetime.timedelta(minutes=
            int((event.start-old_event.start).total_seconds() / 60)
        )
        dte = datetime.timedelta(minutes=
            int((event.end-old_event.end).total_seconds() / 60)
        )
        event.occurrence_set.all().update(
            original_start=F('original_start') + dts,
            original_end=F('original_end') + dte,
        )
        event.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super(LaundryEditEventView, self).get_form_kwargs()
        kwargs.update({'event_type': 'edit'})
        kwargs.update({'event_id': self.kwargs['event_id']})
        return kwargs

    def get_success_url(self):
        url_val = 'fullcalendar' if USE_FULLCALENDAR else 'day_calendar'
        next_url = self.kwargs.get('next') or reverse(url_val, args=[self.object.calendar.slug])
        next_url = get_next_url(self.request, next_url)
        return next_url


class LaundryMyBookings(ListView):

    model = Event

    def get(self, request, *args, **kwargs):

        user = request.user

        now = timezone.now()
        upcoming_bookings = Event.objects.filter(creator_id=user.id, end__gte=now).order_by('start')

        last_bookings = Event.objects.filter(creator_id=user.id, end__lte=now).order_by('-start')[:5]
        return render(request, 'schedule/mybookings.html', {'last_bookings': last_bookings, 'upcoming_bookings': upcoming_bookings})

@receiver(user_signed_up)
def create_admin(sender, **kwargs):
    user = kwargs.pop('user')

    number_of_users = User.objects.all().count()
    if number_of_users == 1:
        user.is_superuser = True
        user.is_staff = True
        group = Group.objects.get(name="laundryapp")
        user.groups.add(group)
        user.save()

def get_next_url(request, default):
    next_url = default
    if not next_url:
        if OCCURRENCE_CANCEL_REDIRECT:
            next_url = OCCURRENCE_CANCEL_REDIRECT
    _next_url = request.GET.get('next') if request.method in ['GET', 'HEAD'] else request.POST.get('next')
    if _next_url and is_safe_url(url=_next_url, host=request.get_host()):
        next_url = _next_url
    return next_url

