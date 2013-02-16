from melange import api

import acpi

@api.register('org.cream.melange.BatteryWidget')
class BatteryWidget(api.API):

    def __init__(self):

        api.API.__init__(self)

    @api.expose
    def get_state(self):

        battery_status = acpi.battery_status()
        battery_remaining_capacity = acpi.battery_remaining_capacity(float)

        if battery_remaining_capacity == 'N/A': # you most likely don't have a battery
            battery_remaining_capacity = 0.0

        battery_level = 'N/A'

        if battery_remaining_capacity <= 100.0 and battery_remaining_capacity >= 85.0:
            battery_level = 'full'

        elif battery_remaining_capacity < 85.0 and battery_remaining_capacity >= 60.0:
            battery_level = 'full-soon'

        elif battery_remaining_capacity < 60.0 and battery_remaining_capacity >= 40.0:
            battery_level = 'full-half'

        elif battery_remaining_capacity < 40.0 and battery_remaining_capacity >= 21.0:
            battery_level = 'empty-soon'

        elif battery_remaining_capacity < 21.0 and battery_remaining_capacity >= 0.0:
            battery_level = 'empty-critical'

        battery_remaining_capacity = str(round(battery_remaining_capacity, 2))

        return {
            'status' : battery_status,
            'level' : battery_level,
            'remaining_capacity' : battery_remaining_capacity
        }
