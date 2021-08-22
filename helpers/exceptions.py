class MaxRequestsTryError(Exception):
    def __init__(self, nbr_of_try, max_number_of_try):
        p = "tries" if max_number_of_try > 1 else "try"
        self.message = f"Max request try exceeded : {nbr_of_try}/{max_number_of_try} {p}"
        super().__init__(self.message)


class InvalidParamsError(Exception):
    def __init__(self, missing_params: list):
        message = "Missing params: "
        message += ' or '.join(missing_params)
        self.message = message
        super().__init__(self.message)
