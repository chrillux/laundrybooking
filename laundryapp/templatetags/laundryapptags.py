from schedule.conf.settings import CHECK_EVENT_PERM_FUNC, CHECK_CALENDAR_PERM_FUNC
from schedule.templatetags.scheduletags import querystring_for_date

from django import template
from django.core.urlresolvers import reverse

register = template.Library()

from django.conf import settings

from pytz import timezone

import datetime
import sys

@register.inclusion_tag("schedule/_daily_table.html", takes_context=True)
def laundryapp_daily_table(context, day, start=6, end=23, increment=60):
    user = context['request'].user
    addable = CHECK_EVENT_PERM_FUNC(None, user)
    if 'calendar' in context:
        addable &= CHECK_CALENDAR_PERM_FUNC(context['calendar'], user)
    context['addable'] = addable

    day_part = day.get_time_slot(day.start + datetime.timedelta(hours=start), day.start + datetime.timedelta(hours=end))
    # get slots to display on the left
    slots = _cook_slots(day_part, increment)
    context['slots'] = slots
    return context

def _cook_slots(period, increment):
    """
        Prepare slots to be displayed on the left hand side
        calculate dimensions (in px) for each slot.
        Arguments:
        period - time period for the whole series
        increment - slot size in minutes
    """
    tdiff = datetime.timedelta(minutes=increment)
    num = int((period.end - period.start).total_seconds()) // int(tdiff.total_seconds())
    s = period.start
    slots = []
    for i in range(num):
        sl = period.get_time_slot(s, s + tdiff)
        slots.append(sl)
        s = s + tdiff
    return slots

@register.inclusion_tag("schedule/_create_event_options.html", takes_context=True)
def laundryapp_create_event_url(context, calendar, slot):
    print >> sys.stderr, "In laundryapp templatetags!"
    context.update({
        'calendar': calendar,
        'MEDIA_URL': getattr(settings, "MEDIA_URL"),
    })
    lookup_context = {
        'calendar_slug': calendar.slug,
    }

    settings_timezone = timezone(settings.TIME_ZONE)
    slot = slot.astimezone(settings_timezone)

    context['laundryapp_create_event_url'] = "%s%s" % (
        reverse("calendar_create_event", kwargs=lookup_context),
        querystring_for_date(slot))
    return context

