from django import template

register = template.Library()


@register.filter
def toggle(value, args):
    """
    Toggles between two values.
    Usage: {{ value|toggle:"asc,desc" }}
    """
    arg_list = [arg.strip() for arg in args.split(',')]
    if value == arg_list[0]:
        return arg_list[1]
    return arg_list[0]


@register.simple_tag(takes_context=True)
def url_with(context, **kwargs):
    """
    Build a querystring using the current request GET parameters,
    overriding any values provided via kwargs. Passing None removes the key.
    """
    request = context.get("request")
    query = request.GET.copy() if request else {}
    for key, value in kwargs.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value
    encoded = query.urlencode()
    return f"?{encoded}" if encoded else "?"
