import unittest
from unittest.mock import AsyncMock, MagicMock

from oekoboilerapi.aylaservice import AylaService
from oekoboilerapi.oekoboiler import Oekoboiler
from tests import utils


class OekoboilerTestcase(unittest.IsolatedAsyncioTestCase):
    """Test the oekoboiler API"""

    async def test_update_properties_ok(self):
        """test a"""

        c_temp = 22
        set_temp = 100
        delta_temp = 4
        on_state = 0

        ayla_service = AylaService(MagicMock())
        ayla_service.request = AsyncMock(
            return_value=utils.mocked_water_heater_properties(
                c_temp, set_temp, delta_temp, on_state
            )
        )

        sut = Oekoboiler(ayla_service, "device_id")

        await sut.async_update()
        self.assertEqual(sut.temp_c_current, c_temp)
        self.assertEqual(sut.temp_c_set, set_temp)
        self.assertEqual(sut.temp_k_delta_set, delta_temp)
