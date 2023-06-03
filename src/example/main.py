import asyncio
import os

from dotenv import load_dotenv

from oekoboilerapi.aylaservice import AylaService, Credentials
from oekoboilerapi.oekoboiler import Oekoboiler


async def main():
    """Example to show how it works. Have fun!"""
    load_dotenv()

    boiler = Oekoboiler(
        AylaService(
            Credentials(
                email=os.getenv("AYLA_EMAIL"),
                password=os.getenv("AYLA_PW"),
                app_secret=os.getenv("AYLA_APP_SECRET"),
            )
        ),
        os.getenv("OEKOBOILER_SN"),
    )

    await boiler.async_update()
    print(f"Current temperature is {boiler.temp_c_current}C°")


asyncio.run(main())
