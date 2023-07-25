import socket
from enum import Enum
from datetime import datetime

# Asterisk AMI credentials
AMI_HOST = '192.168.1.32'
AMI_PORT = 5038
AMI_USER = 'asterisk'
AMI_PASS = 'asterisk'


class CallStatus(Enum):
    queued = 1
    dialed = 2
    answered = 3
    completed = 4
    rejected = 5
    congestion = 6


class UnAnsweredCallModel():
    unique_id: str
    mobile_number: str
    call_status: CallStatus = CallStatus.queued

    def __init__(self, unique_id: str = None, mobile_number: str = None):
        self.unique_id = unique_id
        self.mobile_number = mobile_number

    def __str__(self) -> str:
        return f"A(event: {self.event}, unique_id: {self.unique_id}, mobile_number: {self.mobile_number}, call_picked: {self.call_status})"


active_calls: list[UnAnsweredCallModel] = []


# Function to handle AMI events


def handle_ami_event(event: str):
    global active_calls

    event_data = dict(item.split(': ', 1)
                      for item in event.splitlines() if ': ' in item)

    if event_data.get('Event') == 'DialBegin':
        exist = len([item for item in active_calls if item.unique_id ==
                     event_data.get('DestUniqueid')]) >= 1
        if not exist:
            active_calls.append(UnAnsweredCallModel(
                unique_id=event_data.get('Uniqueid'),
                mobile_number=event_data.get('DialString').split('/')[1],
            ))

    if event_data.get('Event') == 'RTCPSent':
        calls = [item for item in active_calls if item.unique_id ==
                 event_data.get('Uniqueid')]

        if len(calls) >= 1 and calls[0].call_status == CallStatus.queued:
            calls[0].call_status = CallStatus.dialed

    if event_data.get('Event') == 'Newstate':
        calls = [item for item in active_calls if item.unique_id ==
                 event_data.get('Uniqueid')]

        if len(calls) == 1 and (calls[0].call_status == CallStatus.dialed or calls[0].call_status == CallStatus.queued):
            calls[0].call_status = CallStatus.answered

    if event_data.get('Event') == 'DialEnd':
        calls = [item for item in active_calls if item.unique_id ==
                 event_data.get('DestUniqueid')]

        if len(calls) == 1 and calls[0].call_status == CallStatus.queued:
            calls[0].call_status = CallStatus.congestion

    # if event_data.get('Event') == 'OriginateResponse':
    #     print(f"Originate response UID {event_data.get('Uniqueid')}")

    if event_data.get('Event') == 'DeviceStateChange':
        calls = [item for item in active_calls if item.unique_id ==
                 event_data.get('Uniqueid')]

        if len(calls) >= 1:
            if calls[0].call_status == CallStatus.answered:
                calls[0].call_status = CallStatus.completed
            elif calls[0].call_status == CallStatus.dialed:
                calls[0].call_status = CallStatus.rejected

    # print(f"{event_data.get('Event')} - {event_data.get('Response')}")
    # if event_data.get('Event') == 'Hangup':
    #     uniqueid = event_data.get('Uniqueid')
    #     cause = event_data.get('Cause')
    #     if cause == '16':  # '16' is the hangup cause code for a rejected call
    #         print(f"Rejected call with uniqueid {uniqueid}")
    queued = len(
        [item for item in active_calls if item.call_status == CallStatus.queued])
    dialed = len(
        [item for item in active_calls if item.call_status == CallStatus.dialed])
    answered = len(
        [item for item in active_calls if item.call_status == CallStatus.answered])
    completed = len(
        [item for item in active_calls if item.call_status == CallStatus.completed])
    rejected = len(
        [item for item in active_calls if item.call_status == CallStatus.rejected])
    congestion = len(
        [item for item in active_calls if item.call_status == CallStatus.congestion])

    print(
        f"Current time ({event_data.get('Event')} - {event_data.get('Uniqueid')}) {datetime.now()}")
    print(f"Queued calls - {queued}")
    print(f"Dialed calls - {dialed}")
    print(f"Answered calls - {answered}")
    print(f"Completed calls - {completed}")
    print(f"Rejected calls - {rejected}")
    print(f"Congestion calls - {congestion}", end="\n\n")


# Function to connect and listen for AMI events


def listen_for_ami_events():
    try:
        # Connect to Asterisk AMI
        ami_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ami_socket.connect((AMI_HOST, AMI_PORT))

        # Log in to AMI
        login_data = f"Action: Login\r\nUsername: {AMI_USER}\r\nSecret: {AMI_PASS}\r\n\r\n"
        ami_socket.sendall(login_data.encode())

        # Listen for events
        while True:
            ami_data = ami_socket.recv(4096).decode()
            if 'Event: ' in ami_data:
                handle_ami_event(ami_data)

    except socket.error as err:
        print(f"Socket Error: {err}")

    finally:
        # Log off from AMI when the script exits
        logoff_data = "Action: Logoff\r\n\r\n"
        ami_socket.sendall(logoff_data.encode())
        ami_socket.close()


# Call the function to listen for AMI events
# listen_for_ami_events()

if __name__ == "__main__":
    listen_for_ami_events()
