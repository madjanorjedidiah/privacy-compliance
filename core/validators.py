from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class ListOfChoices:
    """Validator ensuring a JSONField list contains only codes from a choices iterable."""

    def __init__(self, choices):
        # Accept raw choices iterable; store as a sorted tuple for stable migrations.
        self.allowed = tuple(sorted({c[0] for c in choices}))

    def __call__(self, value):
        if value is None:
            return
        if not isinstance(value, list):
            raise ValidationError('Expected a list.')
        bad = [v for v in value if v not in self.allowed]
        if bad:
            raise ValidationError(
                f'Invalid value(s): {bad!r}. Allowed: {list(self.allowed)!r}.'
            )

    def __eq__(self, other):
        return isinstance(other, ListOfChoices) and self.allowed == other.allowed


@deconstructible
class ListOfStrings:
    """Validator ensuring a JSONField value is a list of strings."""

    def __call__(self, value):
        if value is None:
            return
        if not isinstance(value, list):
            raise ValidationError('Expected a list.')
        bad = [v for v in value if not isinstance(v, str)]
        if bad:
            raise ValidationError(f'All entries must be strings; got {bad!r}.')

    def __eq__(self, other):
        return isinstance(other, ListOfStrings)


# Backwards-compatible function-style helpers (used where validators are
# declared inline rather than as a model-field list).
def list_of_choices(choices):
    return ListOfChoices(choices)


list_of_strings = ListOfStrings()
