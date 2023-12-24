class Field(object):
    def __init__(
        self,
        name,
        column_type=str,
        default_value=str(),
        call="func",
        callback_func=lambda x: x
    ):
        self.name = name
        self.column_type = column_type
        self.callback_func = callback_func
        self.default_value = default_value
        self.call = call
        self.call_func = {
            "func": self.callback_func
        }

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)
