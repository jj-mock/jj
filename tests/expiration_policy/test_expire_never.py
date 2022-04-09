import pytest

from jj.expiration_policy import ExpireNever

from .._test_utils.steps import given, then, when


@pytest.mark.asyncio
async def test_expired_never():
    with given:
        expiration_policy = ExpireNever()
        await expiration_policy.is_expired(None)

    with when:
        is_expired = await expiration_policy.is_expired(None)

    with then:
        assert not is_expired
