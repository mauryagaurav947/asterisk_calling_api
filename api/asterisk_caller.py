from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from asterisk.ami import AMIClient, AMIClientAdapter, SimpleAction

router = APIRouter(tags=["Asterisk caller"])

client = AMIClient(address='192.168.1.32', port=5038)
client.login(username='asterisk', secret='asterisk')


def event_listener(event, **kwargs):
    print(kwargs)
    print(event)


client.add_event_listener(event_listener)


# client.add_event_listener('Hangup', event_listener)


class DtmfResponseSchema(BaseModel):
    mobile_number: str
    exten: str
    dtmf_response: str


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


@router.post('/demo')
async def call(dtmf_response: DtmfResponseSchema):
    print(dtmf_response.exten)
    print(dtmf_response.dtmf_response)
    print(dtmf_response.mobile_number)
    return {"data": ""}


@router.get('/ami-status')
async def ami_status():
    client.send_action({'Action': 'Command', 'Command': 'core show channels'})
    # client.send_action({
    #     'ActionID': 'CoreShowChannels'
    # })
    return {}
