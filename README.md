# oekoboiler-api

oekoboiler-api is a Python library to read out properties like current temperature from your Oekoboiler water heater.

Use at your own risk! You can damage your boiler by setting wrong parameters!

Home Assistant integration based on this library is coming soon.

## Disclaimer
- Use at your own risk! You can damage your boiler by setting wrong parameters!
- This project is fully private and not affiliated with Oekoboiler or Ayla. 

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install oekoboiler-api.

```bash
pip install oekoboiler-api
```

## Usage (see src/example/main.py)

1. Update .example_env with your data and rename it to .env
2. Run src/example/main.py to see if the connection to your Oekoboiler works. The current water temperature should be printed to console.

```cfg
#Insert your credentials and rename this file to ".env" (remove "example_env"). 
#Now you can execute main.py to run the example.

#The email used to create an account in your Oekoboiler app
AYLA_EMAIL=your_oekoboiler_account@mail.com

#The password used to create an account in your Oekoboiler app
AYLA_PW=oekoboiler_app_pw

#The app secret for Oekoboiler. If your not able to find it somewhere, ask Oekoboiler!
AYLA_APP_SECRET=ayla_secret_for_oekoboiler

#The device id for your Oekoboiler (Revealed in Oekobiler App). 
OEKOBOILER_SN=YOUR_DEVICE_ID 
```

```python
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

```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Credits
This project was influenced by [@johnrichard](https://github.com/johannrichard)'s work.
