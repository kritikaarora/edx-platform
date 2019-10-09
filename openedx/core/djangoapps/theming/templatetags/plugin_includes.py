from django.utils.safestring import mark_safe

from openedx.core.djangoapps.theming.plugins import TemplateIncludesPluginManager
from django.template import Library

register = Library()


def plugin_includes(context, slot):
    """
    Get content to inject into templates from all registered plugins.
    """
    includes = ""
    for plugin in TemplateIncludesPluginManager.get_available_plugins().values():
        instance = plugin()
        content = instance.get_include(slot, context)
        if content:
            includes += content
    return mark_safe(includes)


register.simple_tag(plugin_includes, takes_context=True)
