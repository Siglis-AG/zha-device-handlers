"""zigfred device handler."""
import logging

from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zigpy.zcl.clusters.general import (
    Basic,
    Identify,
    OnOff,
    LevelControl,
    Groups,
    Scenes,
    GreenPowerProxy,
)

from zigpy.zcl.clusters.lighting import Color
import zigpy.types as t

from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
    BUTTON,
    BUTTON_1,
    BUTTON_2,
    BUTTON_3,
    BUTTON_4,
    PRESS_TYPE,
    SHORT_PRESS,
    DOUBLE_PRESS,
    LONG_PRESS,
    LONG_RELEASE,
    ZHA_SEND_EVENT,
)

_LOGGER = logging.getLogger(__name__)

# Siglis zigfred specific clusters
SIGLIS_MANUFACTURER_CODE = 0x129C
ZIGFRED_CLUSTER_ID = 0xFC42
ZIGFRED_CLUSTER_BUTTONS_ATTRIBUTE_ID = 0x0008

# Siglis zigfred cluster implementation
class ZigfredCluster(CustomCluster):
    """Siglis manufacturer specific cluster for zigfred."""

    name = "Siglis Manufacturer Specific"
    cluster_id = ZIGFRED_CLUSTER_ID
    buttons_attribute_id = ZIGFRED_CLUSTER_BUTTONS_ATTRIBUTE_ID

    manufacturer_server_commands = {}
    manufacturer_attributes = {
        buttons_attribute_id: ("buttons", t.uint32_t),
    }

    async def configure_reporting(
        self,
        attribute,
        min_interval,
        max_interval,
        reportable_change,
        manufacturer=None,
    ):
        _LOGGER.info("Configuring reporting on zigfred cluster")
        result = await super().configure_reporting(
            self.buttons_attribute_id,
            0,
            0,
            0,
            manufacturer = SIGLIS_MANUFACTURER_CODE
        )
        return result

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        if attrid == ZIGFRED_CLUSTER_BUTTONS_ATTRIBUTE_ID and value is not None:
            button_lookup = {
                0: BUTTON_1,
                1: BUTTON_2,
                2: BUTTON_3,
                3: BUTTON_4,
            }

            press_type_lookup = {
                0: LONG_RELEASE,
                1: SHORT_PRESS,
                2: DOUBLE_PRESS,
                3: LONG_PRESS,
            }

            button = value & 0xff
            press_type = (value >> 8) & 0xff

            button = button_lookup[button]
            press_type = press_type_lookup[press_type]

            event_args = {
                BUTTON: button,
                PRESS_TYPE: press_type,
            }

            _LOGGER.info(f"Got button press on zigfred cluster: {button}_{press_type}")

            if button and press_type:
                self.listener_event(ZHA_SEND_EVENT, f"{button}_{press_type}", event_args)

class ZigfredUno(CustomDevice):
    """zigfred uno device handler."""

    def __init__(self, *args, **kwargs):
        """Init."""
        _LOGGER.info("Initializing zigfred uno")
        super().__init__(*args, **kwargs)

    signature = {
        MODELS_INFO: [("Siglis", "zigfred uno")],
        ENDPOINTS: {
            5: {
                # Front Module LED
                # SizePrefixedSimpleDescriptor(endpoint=5,
                # profile=260, device_type=258,
                # device_version=1,
                # input_clusters=[0, 3, 4, 5, 6, 8, 768, 837],
                # output_clusters=[])
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.COLOR_DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
                    Color.cluster_id,
                    ZigfredCluster.cluster_id,
                ],
                OUTPUT_CLUSTERS: [],
            },
            6: {
                # Relay
                # SizePrefixedSimpleDescriptor(endpoint=6,
                # profile=260, device_type=256,
                # device_version=1,
                # input_clusters=[0, 3, 4, 5, 6],
                # output_clusters=[])
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                ],
                OUTPUT_CLUSTERS: [],
            },
            7: {
                # Relay
                # SizePrefixedSimpleDescriptor(endpoint=7,
                # profile=260, device_type=257,
                # device_version=1,
                # input_clusters=[0, 3, 5, 4, 6, 8],
                # output_clusters=[])
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
                ],
                OUTPUT_CLUSTERS: [],
            },
            242: {
                # SizePrefixedSimpleDescriptor(endpoint=242,
                # profile=41440, device_type=97,
                # device_version=0,
                # input_clusters=[],
                # output_clusters=[33])
                PROFILE_ID: 41440,
                DEVICE_TYPE: 97,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            },
        },
    }

    replacement = {
        ENDPOINTS: {
            5: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.COLOR_DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
                    Color.cluster_id,
                    ZigfredCluster,
                ],
                OUTPUT_CLUSTERS: [],
            },
            6: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.ON_OFF_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                ],
            },
            7: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: zha.DeviceType.DIMMABLE_LIGHT,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    Identify.cluster_id,
                    Groups.cluster_id,
                    Scenes.cluster_id,
                    OnOff.cluster_id,
                    LevelControl.cluster_id,
                ],
            },
            242: {
                PROFILE_ID: 41440,
                DEVICE_TYPE: 97,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            },
        },
    }
