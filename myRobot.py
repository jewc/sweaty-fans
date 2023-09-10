# James Chin, 9 September 2023

import asyncio
from twilio.rest import Client  # Import the Twilio client
from decouple import config 
# ... other imports ...

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
TWILIO_SID = config('TWILIO_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = config('TWILIO_PHONE_NUMBER')
DESTINATION_PHONE_NUMBER = config('DESTINATION_PHONE_NUMBER')

#client = Client(account_sid, auth_token)

# set GPIO pin numbers
# moisture_pin = 36 #Chage this to the actual GPIO pin number connected to the moisture sensor
# relay_pin = 8 # Change this tot he actual GPIO pin number connected to the relay
MOISTURE_PIN = '36'
RELAY_PIN = '8'


async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload='3rn6lwpqwh5xzra3sy33x8ul94b5s20zf66ghe6v9bny577z')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('robot9-main.wkhwbmlw2g.viam.cloud', opts)

async def moisture_loop(board, relay_pin):
    '''
    moisture_pin value:
    - high: no moisture (True)
    - low: means there is moisture (False)
    '''
    # Main program loop, with relay pin
    moisture_pin = False

    moisture_pin = await board.gpio_pin_by_name(MOISTURE_PIN)
    relay_pin = await board.gpio_pin_by_name(RELAY_PIN)
    detect_moisture = await moisture_pin.get()

    #debug
    print(f'moisture_loop:{MOISTURE_PIN}:{detect_moisture}')

    if detect_moisture == True:
        # Turn on the relay
        await relay_pin.set(False)
        # Turn on the fan (assuming it's Motor-controlled)

    else:
        # stop the relay
        await relay_pin.set(True)
        # Stop the Fan
    
    # return await relay_pin.get(1)   # set Fan speeed to 1, or an appropriate value

async def main():
    robot = await connect()
    print('Resources:')
    print(robot.resource_names)

    # Note that the pin supplied is a placeholder. Please change this to a valid pin you are using.
    # local
    local = Board.from_robot(robot, "local")

    relay_pin = await local.gpio_pin_by_name(RELAY_PIN)
    print("relay_pin is:{relay_pin}")

    local_return_value = await local.gpio_pin_by_name("8")
    print(f"local gpio_pin_by_name return value: {await local_return_value.get()}")
  
    # fan
    fan = Motor.from_robot(robot, "fan")
    fan_return_value = await fan.is_moving()

    #print(f"fan is_moving return value: {await fan_return_value.get()}")

    # change the sync based on longer times
    watering_sleep = 3


    while True:
        running = await moisture_loop(local, relay_pin)
        if running:
            # you can sleep for 5 seconds (depending on size of pot)
            print ('relay running')
        else:
            print('relay not running')
            await asyncio.sleep(watering_sleep)
            
    # Close the robot when you're done!
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
