from django.shortcuts import render_to_response
from django.template import RequestContext

def render(request, tmpl, vars_, current_app):
    ctx = RequestContext(request, current_app)
    return render_to_response(tmpl, vars_, context_instance=ctx)
