from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.template.loader import render_to_string

from leaflet.admin import LeafletGeoAdmin

from .models import School, SchoolProfile


def send_survey(modeladmin, request, queryset):
    for school in queryset:
        subject = 'Durham School Navigator Survey: {:s}'.format(school.name)
        if school.principal_email is None:
            school.principal_email = ''
        to = [school.principal_email]
        from_email = settings.FROM_EMAIL

        school_profile = school.new_profile()
        school_profile.save()
        school_profile_url = request.build_absolute_uri(school_profile.get_absolute_url())

        context = {
            'principal_name': school_profile.principal_name,
            'due_date': school_profile.due_date(),
            'school_profile_url': school_profile_url,
        }
        body = render_to_string('survey_email.txt', context)

        EmailMessage(subject, body, to=to, from_email=from_email).send()
    message = "Tried to send {0!s} email(s)".format(queryset.count())
    messages.info(request, message)


class SchoolAdmin(LeafletGeoAdmin):
    list_display = ('name', 'photo', 'type')
    ordering = ('name',)
    list_filter = ('type', )
    actions = [send_survey]

admin.site.register(School, SchoolAdmin)
admin.site.disable_action('delete_selected')

class SchoolProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'due_date', 'created_at', 'submitted_at')
    ordering = ('created_at', )
admin.site.register(SchoolProfile, SchoolProfileAdmin)
