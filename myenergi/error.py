"""Define error responses."""


from stuff.const import MyEnergiResponse


class MyEnergiError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ResponseError(MyEnergiError):
    def __init__(self, error):
        super().__init__("myenergi nonzero response: {}".format(MyEnergiResponse[error]))


class ParameterError(MyEnergiError):
    def __init__(self, error):
        super().__init__("myenergi parameter error: {}".format(error))
