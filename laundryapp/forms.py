import datetime
import sys

from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from schedule.forms import EventForm
from schedule.models import Event

from datetimewidget.widgets import DateTimeWidget, TimeWidget

class LaundryEventForm(EventForm):

    dateTimeOptions = {
    'minuteStep': '30',
    'minView': '0',
    'maxView': '1',
    'startView': 1,
    'clearBtn': 'false',
    }
    start = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3, options = dateTimeOptions))
    end = forms.DateTimeField(widget=DateTimeWidget(usel10n=True, bootstrap_version=3, options = dateTimeOptions))

    class Meta:
        model = Event
        fields = ['start', 'end', 'title']

    def __init__(self, *args, **kwargs):

        self.event_type = kwargs.pop("event_type")
        if self.event_type == 'edit':
            self.event_id = kwargs.pop("event_id")
        super(LaundryEventForm, self).__init__(*args, **kwargs)

    def clean(self):
        self.date_passed()
        self.event_between()
        self.max_hours_booking()

    def date_passed(self):
        form_start = self.cleaned_data.get('start')
        now = timezone.now()

        if now > form_start:
            raise forms.ValidationError("The date you chose has already passed. Please choose another date.")
        super(LaundryEventForm, self).clean()

    def event_between(self):
        form_start = self.cleaned_data.get('start')
        form_end = self.cleaned_data.get('end')
        has_entries_between = False
        end_time_minus_one_second = form_end - datetime.timedelta(seconds=1)
        start_time_plus_one_second = form_start + datetime.timedelta(seconds=1)

        events_between = Event.objects.filter(start__range=(form_start, end_time_minus_one_second))
        if events_between:
            if self.event_type == 'edit':
                for event_between in events_between:
                    if int(event_between.id) != int(self.event_id):
                        has_entries_between = True
            else:
                has_entries_between = True

        events_between = Event.objects.filter(end__range=(start_time_plus_one_second, form_end))
        if events_between:
            if self.event_type == 'edit':
                for event_between in events_between:
                    if int(event_between.id) != int(self.event_id):
                        has_entries_between = True
            else:
                has_entries_between = True

        if has_entries_between:
            raise forms.ValidationError("There is another booking within the times you chose, please change.")
        super(LaundryEventForm, self).clean()

    def max_hours_booking(self):
        form_start = self.cleaned_data.get('start')
        form_end = self.cleaned_data.get('end')

        max_hours = 6
        max_minutes = max_hours * 60

        booking_time = form_end - form_start
        booking_time_minutes = booking_time.seconds / 60

        if booking_time_minutes > max_minutes:
            raise forms.ValidationError("Maximum booking time is 6 hours.")
        super(LaundryEventForm, self).clean()

class SignupForm(forms.Form):

    first_name = forms.CharField(max_length=30, label="First name", required=True)
    last_name = forms.CharField(max_length=30, label='Last name', required=True)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
