from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
from menu_app.models import Menu, MenuItem

register = template.Library()

@register.simple_tag(takes_context=True)
def draw_menu(context, menu_name):
    try:
        menu = Menu.objects.prefetch_related('items__children').get(name=menu_name)
    except Menu.DoesNotExist:
        return ''

    current_url = context['request'].path

    def render_menu(items, level=0):
        result = '<ul>'
        for item in items:
            url = item.url if item.url else reverse(item.named_url)
            active = 'active' if url == current_url else ''
            result += f'<li class="{active}"><a href="{url}">{item.title}</a>'
            if item.children.exists() and (active or any(child.url == current_url for child in item.children.all())):
                result += render_menu(item.children.all(), level+1)
            result += '</li>'
        result += '</ul>'
        return result

    menu_items = menu.items.filter(parent__isnull=True)
    return mark_safe(render_menu(menu_items))
