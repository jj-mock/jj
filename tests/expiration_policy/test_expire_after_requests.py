import pytest
from pytest import raises

from jj.expiration_policy import ExpireAfterRequests

from .._test_utils.steps import given, then, when


def test_not_expired_after_requests():
    with given:
        expiration_policy = ExpireAfterRequests(1)

    with when:
        is_expired = expiration_policy.is_expired(None)

    with then:
        assert not is_expired


def test_expired_after_requests():
    with given:
        expiration_policy = ExpireAfterRequests(1)
        expiration_policy.is_expired(None)

    with when:
        is_expired = expiration_policy.is_expired(None)

    with then:
        assert is_expired


@pytest.mark.parametrize("count_requests", [0, -1])
def test_expired_after_requests_with_invalid_count_requests(count_requests: int):
    with when:
        with raises(Exception) as exception:
            ExpireAfterRequests(count_requests)
        assert exception.type is AssertionError
