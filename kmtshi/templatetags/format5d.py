from django import template
register = template.Library()

@register.filter
def format5d(value):
    return '%.5f'%(float(value))