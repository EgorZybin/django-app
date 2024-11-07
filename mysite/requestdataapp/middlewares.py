from django.http import HttpRequest, HttpResponse
import time


def set_useragent_on_request_middleware(get_response):
    print("Initializing middleware...")

    def middleware(request: HttpRequest):
        print("Processing request...")
        request.user_agent = request.META["HTTP_USER_AGENT"]
        response = get_response(request)
        print("Processing response...")
        return response

    return middleware


class CountRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.request_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    def __call__(self, request: HttpRequest):
        self.request_count += 1
        print(f"Request counts: {self.request_count}, path: {request.path}")
        response = self.get_response(request)
        self.responses_count += 1
        print(f"Response counts: {self.responses_count}, path: {request.path}")
        return response

    def process_exception(self, request: HttpRequest, exception: Exception):
        self.exceptions_count += 1
        print(f"Exception counts: {self.exceptions_count}, path: {request.path}")


class ThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.throttle_time = 60
        self.throttle_limit = 30
        self.cache = {}

    def __call__(self, request: HttpRequest):
        ip_address = request.META["REMOTE_ADDR"]
        if ip_address in self.cache:
            timestamps = self.cache[ip_address]
            now = time.time()
            timestamps = [timestamp for timestamp in timestamps if timestamp > now - self.throttle_time]
            if len(timestamps) >= self.throttle_limit:
                return HttpResponse('Слишком много запросов. Подождите {} секунд.'.format(self.throttle_time -
                                                                                          (now - timestamps[-1])),
                                    status=429)
            timestamps.append(now)
            self.cache[ip_address] = timestamps
        else:
            self.cache[ip_address] = [time.time()]

        return self.get_response(request)
