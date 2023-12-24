from neo4jmodels.base.fields import Field


class ModelMetaclass(type):
    def __new__(cls, name, base, attrs):
        if name == "Model":
            return type.__new__(cls, name, base, attrs)
        mappings = dict()

        for k, v in attrs.items():
            # FIXME. Improve implement.
            if isinstance(v, Field):
                mappings[k] = v

        for k in mappings.keys():
            attrs.pop(k)
            attrs['__mappings__'] = mappings
            attrs['__table__'] = name

        return type.__new__(cls, name, base, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                r"'Model' object has no attribute '%s'" % key
            )

    def __setattr__(self, key, value):
        self.__mappings__[key] = value

    def to_json(self):

        rsp = dict()
        for key, value in self.__mappings__.items():
            rsp[value.name] = value.callback_func(
                getattr(self, key, value.default_value)
            )
        return rsp

    def convert(self):
        rsp = dict()
        for key, value in self.__mappings__.items():
            # FIXME. Improve implement.
            if isinstance(value, Field):
                rsp[value.name] = value.callback_func(
                    getattr(self, key, value.default_value)
                )

        return rsp
