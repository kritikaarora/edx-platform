from django.utils.safestring import mark_safe

from openedx.core.djangoapps.theming.plugins import (
    LmsTemplateIncludesPluginManager,
    StudioTemplateIncludesPluginManager,
)
from django.template import Library

register = Library()


def plugin_includes(context, environment, slot):
    """
    Get content to inject into templates from all registered plugins.
    """
    includes = ""
    if environment == 'lms':
        plugins = LmsTemplateIncludesPluginManager.get_available_plugins().values()
    elif environment == 'studio':
        plugins = StudioTemplateIncludesPluginManager.get_available_plugins().values()
    else:
        plugins = []
    for plugin in plugins:
        instance = plugin()
        content = instance.get_include(slot, context)
        if content:
            includes += content
    return mark_safe(includes)


register.simple_tag(plugin_includes, takes_context=True)
