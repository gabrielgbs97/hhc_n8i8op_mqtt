#!/bin/bash
mosquitto_pub -t "homie/placa_rele_$1/rele_$2/estado/set" -m "$3"