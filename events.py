import socket

# Asterisk AMI credentials
AMI_HOST = '192.168.1.32'
AMI_PORT = 5038
AMI_USER = 'asterisk'
AMI_PASS = 'asterisk'


class UnAnsweredCallModel:
    event: str
    unique_id: str
    mobile_number: str

    def __init__(self, event: str = None, unique_id: str = None, mobile_number: str = None):
        self.event = event
        self.unique_id = unique_id
        self.mobile_number = mobile_number

    def __str__(self) -> str:
        return f"A(event: {self.event}, unique_id: {self.unique_id}, mobile_number: {self.mobile_number})"


active_calls: list[UnAnsweredCallModel] = []


# Function to handle AMI events


def handle_ami_event(event):
    global active_calls

    event_data = dict(item.split(': ', 1)
                      for item in event.splitlines() if ': ' in item)

    print(event_data)

    if event_data.get('Event') == 'DialBegin':
        print(
            f"DialBegin with UID {event_data.get('DestUniqueid')} and mobile number {event_data.get('DialString').split('/')[1]}")

    if event_data.get('Event') == 'Newstate':
        print(f"Call answered with UID {event_data.get('Uniqueid')}")
        active_calls = active_calls + 1

    # if event_data.get('Event') == 'OriginateResponse':
    #     print(f"Originate response UID {event_data.get('Uniqueid')}")

    if event_data.get('Event') == 'DeviceStateChange':
        print(f"Call ended with UID {event_data.get('Uniqueid')}")

    # print(f"{event_data.get('Event')} - {event_data.get('Response')}")
    if event_data.get('Event') == 'Hangup':
        uniqueid = event_data.get('Uniqueid')
        cause = event_data.get('Cause')
        if cause == '16':  # '16' is the hangup cause code for a rejected call
            print(f"Rejected call with uniqueid {uniqueid}")


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


# 1690180746.22
# 1690180746.22
