from datetime import datetime, timedelta

from oekoboilerapi.aylaservice import AylaService, AylaProperty


class Oekoboiler:
    """represent an oekoboiler and its current state"""

    PROP_NAME_TEMP_CURRENT = "F103"
    PROP_NAME_TEMP_SET = "F11"
    PROP_NAME_TEMP_DELTA = "F12"
    PROP_NAME_ON_STATE = "F104"

    def __init__(self, service: AylaService, device_id: str) -> None:
        self.device_id = device_id
        self.service: AylaService = service
        self.last_update: datetime = None
        self.boiler_data: list[AylaProperty] = []

        self.update_delay_min: timedelta = timedelta(minutes=5)

    async def async_update(self):
        """update current values from Ayla cloud"""

        if (
            self.last_update is None
            or self.last_update + self.update_delay_min < datetime.now()
        ):
            self.boiler_data.clear()
            self.boiler_data: list[
                AylaProperty
            ] = await self.service.get_properties(self.device_id)
            self.last_update = datetime.now()

    async def set_target_temp(self, target_temp_c: int):
        """Sets the target temp in C°"""
        return await self.service.update_property_by_name(
            self.boiler_data, self.PROP_NAME_TEMP_SET, target_temp_c
        )

    @property
    def temp_c_current(self):
        """Returns the current water temp in C°"""
        return self.service.get_property_by_name(
            self.boiler_data, Oekoboiler.PROP_NAME_TEMP_CURRENT
        ).value

    @property
    def temp_c_set(self):
        """Returns the current set temp in C°"""
        return self.service.get_property_by_name(
            self.boiler_data, Oekoboiler.PROP_NAME_TEMP_SET
        ).value
