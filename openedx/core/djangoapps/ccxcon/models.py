"""
Models for the ccxcon
"""

from __future__ import absolute_import

import six
from django.db import models


class CCXCon(models.Model):
    """
    Definition of the CCXCon model.
    Stores the url and the oauth key to access the REST APIs on the CCX Connector.

    .. no_pii:
    """
    url = models.URLField(unique=True, db_index=True)
    oauth_client_id = models.CharField(max_length=255)
    oauth_client_secret = models.CharField(max_length=255)
    title = models.CharField(max_length=255)

    class Meta(object):
        app_label = 'ccxcon'
        verbose_name = 'CCX Connector'
        verbose_name_plural = 'CCX Connectors'

    def __repr__(self):
        return '<CCXCon {}>'.format(self.title)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return six.text_type(self.__str__())
