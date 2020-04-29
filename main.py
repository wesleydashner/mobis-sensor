import config
import RPi.GPIO as GPIO
import time
import requests


def get_distance():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.trigger_pin, GPIO.OUT)
    GPIO.setup(config.echo_pin, GPIO.IN)
    GPIO.output(config.trigger_pin, True)
    time.sleep(0.00001)
    GPIO.output(config.trigger_pin, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(config.echo_pin) == 0:
        start_time = time.time()

    while GPIO.input(config.echo_pin) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time

    distance = (time_elapsed * 34300) / 2
    print(distance)
    return distance


def get_current_availability():
    distance = get_distance()
    print(distance)
    if distance > config.max_distance:
        distance = get_distance()
    return distance > config.min_distance


def get_last_availability():
    with open('availability.txt', 'r') as f:
        return f.read() == 'True'


def write_last_availability(v):
    with open('availability.txt', 'w') as f:
        f.write(f'{v}')


def update_server(v):
    requests.post(config.api_url, json={'lotID': config.lot_id, 'stalls': {f'{config.sensor_id}': v}})


def main():
    true_pings = 0
    false_pings = 0
    ping_requirement = 3
    while True:
        if true_pings == ping_requirement or false_pings == ping_requirement:
            break
        if get_current_availability():
            true_pings += 1
            false_pings = 0
        else:
            false_pings += 1
            true_pings = 0
    current_availability = true_pings == 3
    if current_availability != get_last_availability():
        write_last_availability(current_availability)
        print('about to update server')
        update_server(current_availability)
    GPIO.cleanup()


main()
