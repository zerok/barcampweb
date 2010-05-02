class SimpleLoginMiddleware(object):
    def process_request(self, request):
        simple_login = request.session.get('username', None)
        if simple_login is not None:
            setattr(request, 'username', simple_login)
    
    def process_response(self, request, response):
        simple_login = getattr(request, 'username', None)
        if hasattr(request, 'session'):
            request.session['username'] = simple_login
        return response