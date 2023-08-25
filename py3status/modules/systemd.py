r"""
Display status of a service on your system.

Configuration parameters:
    cache_timeout: refresh interval for this module (default 5)
    format: display format for this module (default '\?if=!hide {unit}: {status}')
    hide_extension: suppress extension of the systemd unit (default False)
    hide_if_default: suppress the output if the systemd unit is in default state
        'off' the output is never suppressed
        'on' the output is suppressed if the unit is (enabled and active)
                                                  or (disabled and inactive)
        'active' the output is suppressed if the unit is active
        'inactive' the output is suppressed if the unit is inactive
        (default 'off')
    unit: specify the systemd unit to use (default 'dbus.service')
    user: specify if this is a user service (default False)

Format placeholders:
    {unit} unit name, eg sshd.service
    {status} unit status, eg active, inactive, not-found

Color options:
    color_good: unit active
    color_bad: unit inactive
    color_degraded: unit not-found

Requires:
    dbus-python: to interact with dbus
    pygobject: which in turn requires libcairo2-dev, libgirepository1.0-dev

Examples:
```
# show the status of vpn service
# left click to start, right click to stop
systemd vpn {
    unit = 'vpn.service'
    on_click 1 = 'exec sudo systemctl start vpn'
    on_click 3 = 'exec sudo systemctl stop vpn'
}
```

@author Adrian Lopez <adrianlzt@gmail.com>
@license BSD

SAMPLE OUTPUT
{'color': '#00FF00', 'full_text': 'sshd.service: active'}

inactive
{'color': '#FF0000', 'full_text': 'sshd.service: inactive'}

not-found
{'color': '#FFFF00', 'full_text': 'sshd.service: not-found'}
"""

import dbus


class Py3status:
    """ """

    # available configuration parameters
    cache_timeout = 5
    format = r"\?if=!hide {unit}: {status}"
    hide_extension = False
    hide_if_default = "off"
    unit = "dbus.service"
    user = False

    def post_config_hook(self):
        if self.user:
            bus = dbus.SessionBus()
        else:
            bus = dbus.SystemBus()
        systemd = bus.get_object("org.freedesktop.systemd1", "/org/freedesktop/systemd1")
        systemd_unit = systemd.LoadUnit(
            self.unit, dbus_interface="org.freedesktop.systemd1.Manager"
        )
        unit_proxy = bus.get_object("org.freedesktop.systemd1", systemd_unit)
        self.systemd_interface = dbus.Interface(unit_proxy, "org.freedesktop.DBus.Properties")

    def systemd(self):
        status = self.systemd_interface.Get("org.freedesktop.systemd1.Unit", "ActiveState")
        exists = self.systemd_interface.Get("org.freedesktop.systemd1.Unit", "LoadState")
        state = self.systemd_interface.Get("org.freedesktop.systemd1.Unit", "UnitFileState")

        if exists == "not-found":
            color = self.py3.COLOR_DEGRADED
            status = exists
        elif status == "active":
            color = self.py3.COLOR_GOOD
        elif status == "inactive":
            color = self.py3.COLOR_BAD
        else:
            color = self.py3.COLOR_DEGRADED

        if self.hide_if_default == "on":
            hide = (status == "active" and state == "enabled") or (
                status == "inactive" and state == "disabled"
            )
        else:
            hide = status == self.hide_if_default

        if self.hide_extension and self.unit.endswith(".service"):
            unitPrintName = self.unit[:-8]
        else:
            unitPrintName = self.unit

        return {
            "cached_until": self.py3.time_in(self.cache_timeout),
            "color": color,
            "full_text": self.py3.safe_format(
                self.format, {"hide": hide, "unit": unitPrintName, "status": status}
            ),
        }


if __name__ == "__main__":
    """
    Run module in test mode.
    """
    from py3status.module_test import module_test

    module_test(Py3status)
