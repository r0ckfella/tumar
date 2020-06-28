class ExceededLinksCountError(Exception):
    def __init__(self, message=None, post_pk=None):
        if post_pk and message:
            message += (
                "\nThere can be only one YouTube link and"
                " one general link for post {}."
            ).format(post_pk)
        elif post_pk and not message:
            message = (
                "\nThere can be only one YouTube link and"
                " one general link for post {}."
            ).format(post_pk)

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        self.post_pk = post_pk
