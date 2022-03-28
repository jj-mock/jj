from jj.expiration_policy import ExpireAfterRequests

from .._test_utils.steps import given, then, when


def test_pack_expire_after_requests():
    with given:
        expiration_policy = ExpireAfterRequests(2)

    with when:
        actual = expiration_policy.__packed__()

    with then:
        assert actual == {
            "max_requests_count": 2,
        }
