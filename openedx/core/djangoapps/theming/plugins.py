"""
Static content plugins for templates.
"""
from __future__ import absolute_import

from openedx.core.lib.plugins import PluginManager

# Stevedore extension point namespaces
LMS_TEMPLATE_INCLUDES_NAMESPACE = 'lms.template_includes'
STUDIO_TEMPLATE_INCLUDES_NAMESPACE = 'studio.template_includes'


class LmsTemplateIncludesPluginManager(PluginManager):
    """
    Manager for plugins that inject content into template blocks in the LMS.
    """
    NAMESPACE = LMS_TEMPLATE_INCLUDES_NAMESPACE


class StudioTemplateIncludesPluginManager(PluginManager):
    """
    Manager for plugins that inject content into template blocks in Studio.
    """
    NAMESPACE = STUDIO_TEMPLATE_INCLUDES_NAMESPACE


