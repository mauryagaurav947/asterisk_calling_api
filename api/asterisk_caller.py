from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from asterisk.ami import AMIClient, AMIClientAdapter, SimpleAction
# from handler.database_handler import get_db, DatabaseHandler

router = APIRouter(tags=["Asterisk caller"])

client = AMIClient(address='192.168.1.32', port=5038)
client.login(username='asterisk', secret='asterisk')


@router.get('/call')
async def call(mobile_number: str):
    if len(mobile_number) == 10:
        # adapter = AMIClientAdapter(client)

        # future = adapter.Originate(
        #     Channel=f'SIP/192.168.1.50/{mobile_number}',
        #     Exten='1002',
        #     Priority=1,
        #     Context='example',
        #     CallerID='1000',
        #     ORIGINATING_MOBILE=mobile_number
        # )

        action = SimpleAction(
            'Originate',
            Channel=f'SIP/192.168.1.50/{mobile_number}',
            Exten=mobile_number,
            Priority=1,
            Context='example',
            CallerID='1000',
            Async=True,
        )

        client.send(action)

        return {
            "message": "Call initiated"
        }
    else:
        return {
            "message": "Invalid mobile number"
        }


# @router.get('/demo')
# async def call(machine_number: str, db: DatabaseHandler = Depends(get_db)):
#     result = db.get_channel_status(machine_number=machine_number)
#     return {
#         'id': result[0],
#         'queued': result[1],
#         'dialed': result[2],
#         'answered': result[3],
#         'completed': result[4],
#         'rejected': result[5],
#         'congestion': result[6],
#         'machine_number': result[7],
#     }


@router.get('/ami-status')
async def ami_status():
    client.send_action({'Action': 'Command', 'Command': 'core show channels'})
    # client.send_action({
    #     'ActionID': 'CoreShowChannels'
    # })
    return {}
