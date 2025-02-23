import asyncio
import os

from dotenv import load_dotenv

from oekoboilerapi.aylaservice import AylaService, Credentials
from oekoboilerapi.oekoboiler import Oekoboiler


async def main():
    """Example to show how it works. Have fun!"""
    load_dotenv()

    service = AylaService(
            Credentials(
                email=os.getenv("AYLA_EMAIL"),
                password=os.getenv("AYLA_PW"),
                app_secret=os.getenv("AYLA_APP_SECRET"),
            )
        )

    b = await service.get_dsns_info(os.getenv("OEKOBOILER_SN"))
    d = await service.get_devices()
    
    boiler = Oekoboiler(service, os.getenv("OEKOBOILER_SN"))
    await boiler.async_update()
    print(boiler.temp_c_current)
    print(boiler.temp_c_set)
    

    print(b)
    print(d)
    # await boiler.async_update()

asyncio.run(main())
