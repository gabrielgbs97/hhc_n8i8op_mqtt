# hhc_n8i8op_mqtt
HHC-N8I8OP MQTT gateway. Publish your relay board as MQTT topic tree. Can support several boards at same time. Connects to MQTT broker at localhost, default server port.
You have to set your HHC-N8I8OP as UDP service, port 5000.
https://es.aliexpress.com/item/4000120026245.html

# Command Line Switch HomeAssistant alternative
MQTT client may not be that reliable. You may also try a simpler solution. Still you need to set your HHC-N8I8OP as UDP service, port 5000.
You will need `sed`, `nc`, `grep`. They will likely be available already on your current Linux platform.

```Shell
switch:
  - platform: command_line
    scan_interval: 10
    switches:
      # Switch relay 1
      relay_1_cmd: # < You may change this entity name
        command_on: 'printf "on1" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off1" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e ".......1" > /dev/null && return 0
      # Switch relay 2
      relay_2_cmd:
        command_on: 'printf "on2" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off2" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e "......1." > /dev/null && return 0
      # Switch relay 3
      relay_3_cmd:
        command_on: 'printf "on3" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off3" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e ".....1.." > /dev/null && return 0
      # Switch relay 4
      relay_4_cmd:
        command_on: 'printf "on4" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off4" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e "....1..." > /dev/null && return 0
      # Switch relay 5
      relay_5_cmd:
        command_on: 'printf "on5" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off5" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e "...1...." > /dev/null && return 0
      # Switch relay 6
      relay_5_cmd:
        command_on: 'printf "on6" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off6" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e "..1....." > /dev/null && return 0
      # Switch relay 7
      relay_5_cmd:
        command_on: 'printf "on7" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off7" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e ".1......" > /dev/null && return 0
      # Switch relay 8
      relay_5_cmd:
        command_on: 'printf "on8" | nc -q 1 -un 192.168.1.30 5000'
        command_off: 'printf "off8" | nc -q 1 -un 192.168.1.30 5000'
        command_state: >
          relay=$(printf "read" | nc -q 1 -un 192.168.1.30 5000 | sed -r "s/relay//"); test ${#relay} == "8" | printf $relay | grep -e "1......." > /dev/null && return 0
```
