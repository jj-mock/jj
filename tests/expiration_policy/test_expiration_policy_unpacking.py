from jj.expiration_policy import ExpireAfterRequests

from .._test_utils.steps import given, then, when


def test_unpack_expire_after_requests():
    with given:
        packed = {
            "max_requests_count": 2
        }

    with when:
        expiration_policy = ExpireAfterRequests.__unpacked__(**packed)

    with then:
        assert expiration_policy.__packed__() == packed
