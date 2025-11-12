from django import template


register = template.Library()

@register.simple_tag()
def prep_tolerance_str(upper, lower):
    return '+{0}/{1}'.format(upper, lower)

@register.simple_tag()
def prep_id(prefix, dim):
    return '{0}_{1}'.format(prefix, dim)