import inspect


def is_invalid_params(func, *args, **kwargs):
    """
    Method:
        Validate pre-defined criteria, if any is True - function is invalid
        0. func should be callable
        1. kwargs should not have unexpected keywords
        2. remove kwargs.keys from func.parameters
        3. number of args should be <= remaining func.parameters
        4. number of args should be >= remaining func.parameters less default
    """
    # For builtin functions inspect.getargspec(funct) return error. If builtin
    # function generates TypeError, it is because of wrong parameters.
    if not inspect.isfunction(func):
        return True

    signature = inspect.signature(func)
    parameters = signature.parameters

    unexpected = set(kwargs.keys()) - set(parameters.keys())
    if len(unexpected) > 0:
        return True

    params = [
        parameter for name, parameter in parameters.items()
        if name not in kwargs
    ]
    params_required = [
        param for param in params
        if param.default is param.empty
    ]

    return not (len(params_required) <= len(args) <= len(params))
