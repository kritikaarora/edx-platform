"""
Cohort API URLs
"""

from django.conf import settings
from django.conf.urls import url

import openedx.core.djangoapps.course_groups.views
import openedx.core.djangoapps.course_groups.api.v1.views


urlpatterns = [
    url(
        r'^v1/settings/{}$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        openedx.core.djangoapps.course_groups.views.api_cohort_settings,
        name='cohort_settings',
    ),
    url(
        r'^v1/courses/{}/cohorts/(?P<cohort_id>[0-9]+)?$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        openedx.core.djangoapps.course_groups.views.api_cohort_handler,
        name='cohort_handler',
    ),
    url(
        r'^v1/courses/{}/cohorts/(?P<cohort_id>[0-9]+)/users/?$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        openedx.core.djangoapps.course_groups.api.v1.views.list_add_user_to_cohort,
        name='list_add_cohort_users',
    ),
    url(
        r'^v1/courses/{}/cohorts/(?P<cohort_id>[0-9]+)/users/(?P<username>.+)$'.format(
            settings.COURSE_KEY_PATTERN,
        ),
        openedx.core.djangoapps.course_groups.api.v1.views.remove_user_from_cohort,
        name='delete_user_from_cohort',
    ),
]
