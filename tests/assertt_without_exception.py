def assert_without_exception(func, param):
    try:
        func(param)
        return True
    except Exception:
        return False
