#!/usr/bin/python
# -*- coding: utf-8 -*-
# acpi.py
#   
# Copyright (C) 2004 Daniel Mueller <da_mueller@gmx.net>
# Modified (C) 2010 Immanuel Peratoner <immanuel.peratoner@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os

ACPI_PATH = '/proc/acpi'

def ac_adapter_status():
    ac_state_filename = os.path.join(ACPI_PATH, 'ac_adapter/AC/state')

    if os.path.exists(ac_state_filename):
        # Read contents of ac adapter state file
        ac_state_file_handle = open(ac_state_filename)
        ac_state = ac_state_file_handle.read()
        ac_state_file_handler.close()

        ac_state = ac_state.split(":")

        # That's the actual state
        ac_state = ac_state[1]

        ac_state = ac_state.strip()

        return ac_state
    else:
        return "N/A"

def battery_status():
    battery_state_filename = os.path.join(ACPI_PATH, 'battery/BAT0/state')

    if os.path.exists(battery_state_filename):
        # Read contents of battery status file
        battery_state_file_handle = open(battery_state_filename)
        battery_state = battery_state_file_handle.read()
        battery_state_file_handle.close()

        battery_state = battery_state.replace('\n',':')
        battery_state = battery_state.split(':')
        
        # That's the actual status
        battery_state = battery_state[5]

        battery_state = battery_state.strip()

        if battery_state == "unknown":
            return "charged"
        else:
            return battery_state
    else:
        return "N/A"


def battery_remaining_capacity(return_type=str):
    battery_info_filename = os.path.join(ACPI_PATH, 'battery/BAT0/info')
    battery_state_filename = os.path.join(ACPI_PATH, 'battery/BAT0/state')

    if os.path.exists(battery_info_filename) and os.path.exists(battery_state_filename):
        # Read the maximum capacity of the battery
        battery_info_file_handle = open(battery_info_filename)
        battery_info = battery_info_file_handle.read()
        battery_info_file_handle.close()
        
        # Read the remaining capacity file
        battery_state_file_handle = open(battery_state_filename)
        battery_state = battery_state_file_handle.read()
        battery_state_file_handle.close()
        

        # Begin extracting the maximum charge value
        battery_info = battery_info.strip()
        battery_info = battery_info.replace("\n",":")
        battery_info = battery_info.split(":")

        # design capacity
        battery_max_capacity = battery_info[5]
        battery_max_capacity = battery_max_capacity.strip()

        # Split at whitespace to remove the unit (mWh)
        battery_max_capacity = battery_max_capacity.split()
        battery_max_capacity = battery_max_capacity[0]


        # Begin extracting remaining capacity and status
        battery_state = battery_state.strip()
        battery_state = battery_state.replace("\n",":")
        battery_state = battery_state.split(":")
    
        # That's the status (charging / discharging / whatever)
        battery_status = battery_state[5]
        battery_status = battery_status.strip()
        
        # That's the remaining capacity
        battery_rem_capacity = battery_state[9]
        battery_rem_capacity = battery_rem_capacity.strip()
        battery_rem_capacity = battery_rem_capacity.split()
        battery_rem_capacity = battery_rem_capacity[0]


        if battery_status == "unknown":
            return '100%'
        else:
            # calculate the battery level; something between 0 and 1
            battery_level = float(battery_rem_capacity) / float(battery_max_capacity)

            # convert battery level into percentage
            battery_capacity_percent = round(battery_level * 100, 2)
            
            if return_type == str:
                return str(battery_capacity_percent) + '%'
            elif return_type == int:
                return int(battery_capacity_percent)
            elif return_type == float:
                return battery_capacity_percent
    else:
        return "N/A"


def cpu_temperature():
    cpu_temperature_filename = os.path.join(ACPI_PATH, 'thermal_zone/THM0/temperature')

    if os.path.exists(cpu_temperature_filename):
        cpu_temperature_file_handle = open(cpu_temperature_filename)
        cpu_temperature = cpu_temperature_file_handle.read()
        cpu_temperature_file_handle.close()

        cpu_temperature = cpu_temperature.strip()
        cpu_temperature = cpu_temperature.split()
        cpu_temperature = cpu_temperature[1]

        return cpu_temperature + ' °C'
    else:
        return "N/A"
