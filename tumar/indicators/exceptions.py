class QueryImageryFromEgisticError(Exception):
    def __init__(self, message=None, cadastre_pk=None):
        if cadastre_pk and message:
            message += (
                "\nImage processing result for cadastre_pk {}"
                " was not found in the database or not finished"
            ).format(cadastre_pk)
        elif cadastre_pk and not message:
            message = (
                "Image processing result for cadastre_pk {}"
                " was not found in the database or not finished"
            ).format(cadastre_pk)

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.cadastre_pk = cadastre_pk


class FreeRequestsExpiredError(Exception):
    def __init__(self, message=None, farm_pk=None):
        if farm_pk and message:
            message += "\nFree requests of {} farm have expired.".format(farm_pk)
        elif farm_pk and not message:
            message = "Free requests of {} farm have expired.".format(farm_pk)

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.farm_pk = farm_pk


class CadastreNotInEgisticError(Exception):
    def __init__(self, message=None, cadastre_pk=None):
        if cadastre_pk and message:
            message += (
                "\nCadastre number {} was not found in the egistic db."
                "Or imagery for custom cadastres is not supported yet."
            ).format(cadastre_pk)
        elif cadastre_pk and not message:
            message = (
                "Cadastre number {} was not found in the egistic db."
                "Or imagery for custom cadastres is not supported yet."
            ).format(cadastre_pk)

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.cadastre_pk = cadastre_pk


class ImageryRequestAlreadyExistsError(Exception):
    def __init__(self, message=None, cadastre_pk=None):
        if cadastre_pk and message:
            message += (
                "\nThe cadastre {} is already in the queue for image processing."
            ).format(cadastre_pk)
        elif cadastre_pk and not message:
            message = (
                "The cadastre {} is already in the queue for image processing."
            ).format(cadastre_pk)

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.cadastre_pk = cadastre_pk
