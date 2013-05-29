from django.core.urlresolvers import reverse, resolve

from django import template
register = template.Library()

@register.simple_tag
def active(request, name):
	if resolve(request.path).url_name == name:
		return 'active'
	return ''