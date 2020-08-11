#!/usr/bin/python3
# Following subset of Homie
#  https://homieiot.github.io/
#
#
import paho.mqtt.client as mqtt
import time, re, socket, yaml
from _thread import start_new_thread

POLLING_WAIT=5
SOCKET_TIMEOUT= 3#seconds
UDP_PORT=5000
INVENTORY_FILE="./inventory.yaml"
ON="ON"
OFF="OFF"
BASE_TOPIC="homie/" # I only support a 1-level base topic (NOT homie/whatever)
BASE_RELAY_NAME="rele_" #example, rele_3
STATE_TOPIC_NAME="estado"
RE_INT=re.compile("[0-9]+")
READ_CMD="read"
inventory={}
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    global inventory
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    ################git pull
    # ### 
    ## Placa relés X ## 
    ###################
    # Cada relé podrá operarse (placa 1, relé 1) con:
    # homie/placa_reles_1/rele_1/estado/set -> ("ON" o "OFF")
    # Luego, la RBPi transmitirá el feedback al cambiar el estado del relé:
    # homie/placa_reles_1/rele_1/estado <- "ON" o "OFF"
    if not inventory:
        inventory=load_inventory()
    # Subscribe or resub to relay boards topics
    for relay_board in inventory['relay_boards']:
        topic_str=BASE_TOPIC+relay_board['name']+"/+/estado/set"
        client.subscribe(topic_str)
        print("SUBSCRIBED TO: ", topic_str)
    # example: client.subscribe("homie/+/+/estado/set")

# Sends ascii comand, returns str received response from board.
# Otherwise it returns False
def send_ascii_cmd(relay_board_ip, ascii_cmd):
    result = False
    ascii_cmd_bytes= bytes(ascii_cmd, "ascii")
    k = socket.socket (socket.AF_INET, socket.SOCK_DGRAM)
    k.settimeout(SOCKET_TIMEOUT)
    try:
        k.connect((relay_board_ip, UDP_PORT))
        k.send(ascii_cmd_bytes)
        if ascii_cmd == READ_CMD:
            buffer_len = 13
        else:
            buffer_len=len(ascii_cmd_bytes)
        response = k.recv(buffer_len)
        response=response.decode("ascii")
        # Result evaluated to response from relay board
        if response:
            result=response
    except socket.timeout:
        pass
    except Exception as e:
        print("An error ocurred when contacting relay board, IP: ",\
            relay_board_ip)
        print("Exception: "+ str(e))
    finally:
        k.close()
        return result

# Sends ascii command to relay board and checks
# that what had been sended was also pinged back
# Return False if operation was not successful,
# True otherwise
def send_ascii_cmd_checked(relay_board_ip, ascii_cmd):

    response=send_ascii_cmd(relay_board_ip, ascii_cmd)
    if(response == ascii_cmd):
        return True
    else:
        return False


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global inventory
    topic_str=msg.topic
    msg_str=str(msg.payload.decode())
    print("Received message on "+topic_str+" "+msg_str)
    splitted_topic = str(msg.topic).split("/")
    # Find relay of topic in inventory and send command
    for relay_board in inventory['relay_boards']:
        if relay_board['name']==splitted_topic[1]:
            board_ip=relay_board['ip']
            relay_number=RE_INT.search(splitted_topic[2]).group(0)
            ascii_cmd=""
            if ON == msg_str:
                # Send TCP ascii cmd to board_ip -> 'onX'
                # and, if successful, send ON to feedback topic
                ascii_cmd = "on"+relay_number

            elif OFF==msg_str:
                # Send TCP ascii cmd to board_ip -> 'offX'
                # and, if successful, send OFF to feedback topic
                ascii_cmd = "off"+relay_number
            if ascii_cmd:
                # Send command to relay board
                operation_success=\
                    send_ascii_cmd_checked(board_ip, ascii_cmd)
                # Publish to feedback topic (mqtt)
                if operation_success:
                    print("Command successfully sent to",relay_board['name'],board_ip)
                    topic_str= "homie/"+splitted_topic[1]+\
                        "/"+splitted_topic[2]+\
                        "/estado"
                    client.publish(topic_str, msg_str)
                else:
                    print("Could not send command to",relay_board['name'],board_ip)
            

def exit_gracefully():
    print("EXITING GRACEFULLY...")
    exit()

def load_inventory():
    inventory={}
    try:
        with open(INVENTORY_FILE, "r") as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python dictionary format
            inventory = yaml.load(file, Loader=yaml.FullLoader)
            print("Inventory loaded successfully: ",INVENTORY_FILE)
    except:
        print("Could not load inventory, check file ",INVENTORY_FILE," or its format")
    finally:
        if not inventory:
            print("Inventory has no values")
            exit_gracefully()
        return inventory

def get_relay_topic(relay_board_name, relay_num):
    return BASE_TOPIC+ \
        relay_board_name+ \
        "/"+BASE_RELAY_NAME+str(relay_num)

def update_topics(reading, relay_board_name):
    # Reversing reading string
    # This way, relay 1 will be at beginning of it
    reading = reading[::-1]
    for position in range(8):
        client.loop(0.2)
        topic_str=get_relay_topic(relay_board_name, position+1)+"/"+STATE_TOPIC_NAME
        msg_str=""
        if str(reading[position]) == "1":
            msg_str=ON
        elif str(reading[position]) == "0":
            msg_str=OFF
        # Update mqtt topic
        if msg_str:
            client.publish(topic_str, msg_str)

def read_boards():
    global inventory
    # Ask every relay board for its state  
    for relay_board in inventory['relay_boards']:
        board_ip=relay_board['ip']
        client.loop(0.1)
        response=send_ascii_cmd(board_ip, READ_CMD)
        # For example, we should receive a response like "relay00100001"
        # if relays 1 and 6 are ON
        if response:
            searched=RE_INT.search(response)
            if searched:
                reading = searched.group(0)
                update_topics(reading, relay_board["name"])

client = mqtt.Client(client_id = "hhc_n8i9op_gateway")
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost")
print("Starting HHC-8I8OP MQTT gateway")
client.loop_start()
# Polling  relay status and publishing its state (every X seconds)
try:
    time.sleep(5)
    while 1:
        read_boards()
        # Waiting
        polling_divisor=5
        for time_slice in range(polling_divisor):
            client.loop(0.1)
            time.sleep(POLLING_WAIT/polling_divisor)


except Exception as e:
    client.disconnect()
    client.loop_stop()
    print("Finished with EXCEPTION:", str(e))
