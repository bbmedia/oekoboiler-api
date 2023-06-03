from datetime import datetime, timedelta

from oekoboilerapi.aylaservice import AylaService


class Oekoboiler:
    """represent an oekoboiler and its current state"""

    def __init__(self, service: AylaService, device_id: str) -> None:
        self.device_id = device_id
        self.service: AylaService = service
        self.temp_c_current: int = None
        self.temp_c_set: int = None
        self.temp_k_delta_set: int = None
        self.on_state: bool = None
        self.last_update: datetime = None

        self.update_delay_min: timedelta = timedelta(minutes=5)

    async def async_update(self):
        """update current values from Ayla cloud"""

        if (
            self.last_update is None
            or self.last_update + self.update_delay_min < datetime.now()
        ):
            boiler_data = await self.service.get_properties(self.device_id)
            self.last_update = datetime.now()

            for prop in boiler_data:
                match prop["property"]["name"]:
                    case "F103":
                        self.temp_c_current = int(prop["property"]["value"])
                    case "F104":
                        self.on_state = bool(prop["property"]["value"])
                    case "F11":
                        self.temp_c_set = int(prop["property"]["value"])
                    case "F12":
                        self.temp_k_delta_set = int(prop["property"]["value"])
