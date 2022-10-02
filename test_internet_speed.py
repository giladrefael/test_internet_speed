#!/usr/bin/env python3

import speedtest, datetime, requests, urllib3
from time import sleep
from os import system

def internet_on():
    http = urllib3.PoolManager()
    try:
        http.request('GET', 'www.google.com', retries=2)
        return True

    except urllib3.exceptions.NewConnectionError:
        return False

    except urllib3.exceptions.MaxRetryError:
        print("too many tries - stalling for now")
        sleep(60*30)
        return False

def test_speed():
    s = speedtest.Speedtest()
    s.get_servers([])
    s.get_best_server()
    s.download(threads=None)
    s.upload(threads=None)
    s.results.share()

    results_dict = s.results.dict()
    down = results_dict["download"]//1e6
    up = results_dict["upload"]//1e6
    return down, up

def send_email(subj, body, target_kwargs):
    return requests.post(
        target_kwargs['target'],
        auth=("api", target_kwargs['api']),
        data={"from": f"Home Bot <{target_kwargs['source_addr']}>",
              "to": [target_kwargs['target_addr']],
              "subject": subj,
              "text": body})

internet_error = False
fail_time = ["", ""]
minutes = 10
speed_test_count = 0
system('clear')

with open("args.json") as f:
    target_kwargs = json.read(f)

while True:
    now = str(datetime.datetime.now()).split(".")[0]
    print("[" + now, end="] ")
    if internet_on():
        print("Connection Success!")
        body = fail_str = ""
        if speed_test_count == 5:
            try: 
                print('Testing connection speed...')
                down, up = test_speed()
                body = "Speed now is: " + str(down) + "/" + str(up)
                speed_test_count = 0
            except:
                print("Something is wrong with SpeedTest, will try later")
                sleep(30)
                continue

        if internet_error:
            fail_str = "Intenet was not working from " + fail_time[0] + " to " + fail_time[1] + "\n"
            internet_error = False
            fail_time = ["", ""]
            send_email("HOMEBOT - Internet Problem", fail_str + body, target_kwargs)
        print(fail_str + body)
    else:
        if fail_time[0] == "":
            fail_time[0] = now
            fail_time[1] = now
        else:
            fail_time[1] = now

        internet_error = True
        print('Connection failed at', now)
    speed_test_count += 1
    sleep(minutes * 60)





