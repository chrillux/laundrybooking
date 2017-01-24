# laundrybooking
An easy to use booking app.

I created this application to be used by me and the people in my housing cooperative for laundry bookings,
but it can be used for any kind of bookings.

## Installing laundrybooking

```
Set environment variables:

SITE_NAME=<Name of site>
SITE_DOMAIN=<Domain name>
CLIENT_ID=<Facebook app client_id>
SECRET=<Facebook app secret>
CALENDAR_NAME=<Name on the calendar>
CALENDAR_SLUG=<Calendar slug>

Run:
$ ./manage.py migrate
```

The first person that creates an account automatically becomes admin. So there is a known race condition. When you setup the application, either log in with facebook or create a standard account to become admin and become member of the group "laundryapp".

To make it possible for other people to use the application, they have to login once, to create their account, then admin needs to add them to the group "laundryapp". This is easily done via the django admin interface.

## Contributors
* [chrillux](https://github.com/chrillux)

## Legal

Laundrybooking is a potpourri of different apps, put together to create this unique application. Special thanks to:
* The people at django-allauth: https://github.com/pennersr/django-allauth
* The django-scheduler project: https://github.com/llazzaro/django-scheduler
* The django-datetime-widget: https://github.com/asaglimbeni/django-datetime-widget
* __All trademarks are the property of their respective owners!__
* Everything else is licensed under MIT.
