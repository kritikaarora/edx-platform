"""
Static content plugins for templates.
"""
from __future__ import absolute_import

from openedx.core.lib.plugins import PluginManager

# Stevedore extension point namespaces
TEMPLATE_INCLUDES_NAMESPACE = 'openedx.template_includes'


class TemplateIncludesPluginManager(PluginManager):
    """
    Manager for plugins that inject content into template blocks.
    """
    NAMESPACE = TEMPLATE_INCLUDES_NAMESPACE


