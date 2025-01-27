from attrs import define
import cattrs
import logging

log = logging.getLogger(__name__)


class FiltersError(Exception):
    pass


def structure(data, cls):

    log.debug("Structuring data")
    log.debug(f"cls={cls}")
    log.debug(f"data={data}")
    try:
        r = cattrs.structure(data, cls)
        log.debug(f"result={r}")
        return r
    except cattrs.errors.ClassValidationError as err:
        log.error(f"ClassValidationError: {err.args}")
        raise


@define
class VisomaResponse:
    """Represents a response from the Visoma API."""

    Success: bool
    Id: int
    Message: str

    @classmethod
    def from_dict(cls, data):
        if not data.get("Success"):
            # Invalidate data to fail the struct
            # TODO: Find a better way
            del data["Success"]
        return cattrs.structure(data, cls)


def visoma_params_from_filters_with_limit(filters, limit):
    filters = filters if filters else {}
    limit = limit if limit else 2

    if not isinstance(filters, dict):
        raise FiltersError(f"Filters must be a dictionary: {filters}")

    if not isinstance(limit, int):
        raise FiltersError(f"Limit must be an integer: {limit}")

    # Normalize keys and values for better caching
    params = {f"params[{k}]".casefold(): f"{v}".casefold() for k, v in filters.items()}

    # Add limit. This param is case sensitive.
    params["params[QueryLimit]"] = limit

    log.debug(f"Visoma params: {params}")
    return params
