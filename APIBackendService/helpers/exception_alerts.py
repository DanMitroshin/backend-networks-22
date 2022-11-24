import functools


# @dataclass
# class ExceptionHandler:
#     e: Exception
#     @staticmethod
#     def context_wrapper(code) -> dict:
#         return {'error_code': code}
# def get_error_response(self) -> Response:
#         if self.e.__class__ == WrongType:
#             data = self.context_wrapper(101)
#         else:
#             data = self.context_wrapper(999)
#         return Response(data, status=status.HTTP_200_OK)


def request_save_errors(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except Exception as e:
            pass

    return wrapper
