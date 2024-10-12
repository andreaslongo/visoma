import pytest

from visoma.lib import FiltersError
from visoma.lib import visoma_params_from_filters_with_limit


def test_non_dict_filter_is_error():
    with pytest.raises(FiltersError, match="Filters must be a dictionary"):
        visoma_params_from_filters_with_limit("str", 1)


def test_non_int_limit_is_error():
    with pytest.raises(FiltersError, match="Limit must be an integer"):
        visoma_params_from_filters_with_limit({}, "str")


def test_detault_filter_and_limit():
    params = visoma_params_from_filters_with_limit(None, None)
    assert params == {"params[QueryLimit]": 2}
