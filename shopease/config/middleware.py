class ScriptNameMiddleware:
    """
    Reads X-Script-Name header set by Nginx and applies it as SCRIPT_NAME.
    This makes Django generate correct prefixed URLs when served under a path prefix
    (e.g., /admin-portal/) via Nginx reverse proxy.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        script_name = request.META.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            request.META['SCRIPT_NAME'] = script_name
        return self.get_response(request)
