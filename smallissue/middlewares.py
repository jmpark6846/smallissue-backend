def csrf_middleware(get_response):

    def middleware(request):
        csrftoken = request.COOKIES.get('csrftoken')
        if csrftoken:
            request.META['HTTP_X_CSRFTOKEN'] = csrftoken

        response = get_response(request)

        return response

    return middleware
