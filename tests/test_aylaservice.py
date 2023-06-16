import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from aioresponses import aioresponses

from oekoboilerapi.aylaservice import (
    AccessToken,
    AylaProperty,
    AylaService,
    LoginFailedError,
    NoAccessError,
)
from tests import utils


class AccessTokenTestcase(unittest.TestCase):
    """Test access token class"""

    def test_access_token_activate(self):
        """test expired function"""

        random_token = "orig_token"
        random_refresh_token = "orig_refresh_token"
        expires_in = 10
        role = "end_user"
        role_tags = []

        sut = AccessToken(
            random_token,
            random_refresh_token,
            expires_in,
            role,
            role_tags,
            None,
        )
        sut.activate()
        self.assertTrue(
            sut.expire_date.replace(microsecond=0),
            (datetime.now() + timedelta(seconds=10)).replace(microsecond=0),
        )

    def test_access_token_expired(self):
        """test expired function (including 3600s threshold)"""

        random_token = "orig_token"
        random_refresh_token = "orig_refresh_token"
        expires_in = 3600
        role = "end_user"
        role_tags = []

        sut = AccessToken(
            random_token,
            random_refresh_token,
            expires_in,
            role,
            role_tags,
            None,
        )
        sut.activate()
        res = sut.is_expired(datetime.now())
        self.assertTrue(res)
        res = sut.is_expired(datetime.now() - timedelta(seconds=1))
        self.assertFalse(res)


class AylaServiceTestcase(unittest.IsolatedAsyncioTestCase):
    """Integration and unit tests for the AylaService class"""

    @aioresponses()
    async def test_refresh_token(self, mocked: aioresponses):
        """Test if token is refreshed"""

        sut = AylaService(MagicMock())
        random_token = "orig_token"
        random_refresh_token = "orig_refresh_token"
        new_token = "new_token"
        new_refresh_token = "new_refresh_token"

        mocked.post(
            url="https://user-field-eu.aylanetworks.com/users/sign_in.json",
            status=200,
            payload=utils.mocked_login_answer(
                random_token, random_refresh_token
            ),
        )
        mocked.post(
            url="https://user-field-eu.aylanetworks.com/users/refresh_token.json",
            status=200,
            payload=utils.mocked_login_answer(new_token, new_refresh_token),
        )

        self.assertIsNone(sut.access_token)
        res = await sut.login()
        mocked.assert_called_once()
        self.assertTrue(res)
        self.assertEqual(random_token, sut.access_token.access_token)
        self.assertEqual(random_refresh_token, sut.access_token.refresh_token)

        current_token = sut.access_token.access_token
        res = await sut.refresh_token()
        self.assertNotEqual(current_token, res)
        self.assertEqual(sut.access_token.access_token, new_token)
        self.assertEqual(sut.access_token.refresh_token, new_refresh_token)

    @aioresponses()
    async def test_login_ok(self, mocked: aioresponses):
        """test login"""

        sut = AylaService(MagicMock())

        random_token = "f5dd0ca57dcf42bb9badd3c86859372d"
        random_refresh_token = "myrefreshtoken"
        mocked.post(
            url="https://user-field-eu.aylanetworks.com/users/sign_in.json",
            status=200,
            payload={
                "access_token": random_token,
                "refresh_token": random_refresh_token,
                "expires_in": 86400,
                "role": "EndUser",
                "role_tags": [],
            },
        )

        self.assertIsNone(sut.access_token)
        res = await sut.login()

        mocked.assert_called_once()

        self.assertTrue(res)
        self.assertEqual(random_token, sut.access_token.access_token)
        self.assertEqual(random_refresh_token, sut.access_token.refresh_token)

    @aioresponses()
    async def test_login_no_access(self, post_mock: aioresponses):
        """test login if connection to ayla is not possible"""

        sut = AylaService(MagicMock())

        self.assertIsNone(sut.access_token)

        post_mock.post(
            url="https://user-field-eu.aylanetworks.com/users/sign_in.json",
            exception=NoAccessError,
        )

        with self.assertRaises(NoAccessError):
            _ = await sut.login()

    @aioresponses()
    async def test_login_failed(self, post_mock):
        """test login if with wrong credentials"""

        sut = AylaService(MagicMock())

        error_msg = {"error": "Invalid email or password."}
        http_status = 401
        post_mock.post(
            url="https://user-field-eu.aylanetworks.com/users/sign_in.json",
            status=http_status,
            payload=error_msg,
        )

        self.assertIsNone(sut.access_token)

        with self.assertRaises(LoginFailedError) as exc:
            _ = await sut.login()
        self.assertEqual(exc.exception.message, error_msg)
        self.assertEqual(exc.exception.http_status, 401)

    @aioresponses()
    async def test_update_ok(self, post_mock):
        """test update"""

        sut = AylaService(MagicMock())
        test_property = AylaProperty(
            name="F103",
            key="123",
            data_updated_at=datetime.now(),
            value="test",
        )

        post_mock.post(
            url="https://user-field-eu.aylanetworks.com/users/sign_in.json",
            status=200,
            payload={
                "access_token": "random_token",
                "refresh_token": "random_refresh_token",
                "expires_in": 86400,
                "role": "EndUser",
                "role_tags": [],
            },
        )

        post_mock.post(
            url=f"https://ads-eu.aylanetworks.com/apiv1/properties/{test_property.key}/datapoints",
            status=201,
            payload={
                "datapoint": {
                    "value": "",
                    "metadata": {"key1": "", "key2": ""},
                }
            },
        )

        self.assertTrue(
            await sut.update_property(test_property.key, test_property.value)
        )
