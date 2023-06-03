from dataclasses import dataclass
from datetime import datetime, timedelta

from aiohttp import ClientConnectorError, ClientSession


@dataclass
class Credentials:
    """holds all needed credential information"""

    email: str
    password: str
    app_secret: str
    app_id: str = "Ob-Ng-id"

    def to_json_str(self):
        """exports the credentials as json"""
        return {
            "user": {
                "email": f"{self.email}",
                "password": f"{self.password}",
                "application": {
                    "app_id": f"{self.app_id}",
                    "app_secret": f"{self.app_secret}",
                },
            }
        }


@dataclass
class AccessToken:
    """holds access token and expire timedate"""

    access_token: str
    refresh_token: str
    expires_in: int
    role: str
    role_tags: str

    expire_date: datetime

    def activate(self):
        """set date expire date"""
        self.expire_date = datetime.now() + timedelta(seconds=self.expires_in)

    def is_expired(self, now: datetime) -> bool:
        """if token is expired"""

        real_date = self.expire_date - timedelta(hours=1)
        return real_date < now


class AylaService:
    """Class to make authenticated requests to Ayla cloud."""

    def __init__(self, credentials: Credentials):
        """Initialize the auth."""
        self.host = "https://user-field-eu.aylanetworks.com"
        self.access_token = None
        self.credentials = credentials

    async def login(self) -> bool:
        """Login to Ayla Cloud"""

        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = self.credentials.to_json_str()

        async with ClientSession() as session:
            try:
                async with session.post(
                    f"{self.host}/users/sign_in.json",
                    json=payload,
                    headers=headers,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.access_token = AccessToken(
                            **data, expire_date=None
                        )
                        self.access_token.activate()
                        return True
                    raise LoginFailedError(await resp.json(), resp.status)

            except ClientConnectorError as exc:
                raise NoAccessError from exc

    async def get_token(self) -> str:
        """get auth token for requests. Refreshs if necessary"""

        if self.access_token is None:
            await self.login()
        elif self.access_token.is_expired(datetime.now()):
            await self.refresh_token()

        return self.access_token.access_token

    async def refresh_token(self) -> bool:
        """send request to refresh token"""
        payload = {
            "user": {
                "refresh_token": self.access_token.refresh_token,
            }
        }

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"auth_token {self.access_token}",
        }

        async with ClientSession() as session:
            async with session.post(
                f"{self.host}/users/refresh_token.json",
                json=payload,
                headers=headers,
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.access_token = AccessToken(**data, expire_date=None)
                    self.access_token.activate()
                    return True

                return False

    async def request(self, target_url):
        """make requst to ayla networks"""

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"auth_token {await self.get_token()}",
            "Accept": "application/json",
        }

        async with ClientSession() as session:
            async with session.get(
                target_url,
                headers=headers,
            ) as resp:
                return await resp.json()

    async def get_devices(self):
        """get devices for current Ayla account"""
        json = await self.request(
            "https://ads-eu.aylanetworks.com/apiv1/devices"
        )
        return json

    async def get_properties(self, dsn: str):
        """get properties for specific device from Ayla cloud"""
        json = await self.request(
            f"https://ads-eu.aylanetworks.com/apiv1/dsns/{dsn}/properties"
        )
        return json


class NoAccessError(Exception):
    """Error for failing connection"""


class LoginFailedError(Exception):
    """Error if login to Ayla Cloud fails"""

    def __init__(self, message: str, http_status: int) -> None:
        self.http_status: int = http_status
        self.message: str = message
        super().__init__()
