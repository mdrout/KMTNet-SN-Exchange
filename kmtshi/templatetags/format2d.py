from django import template
register = template.Library()

@register.filter
def format2d(value):
    return '%.2f'%(float(value))