## Event 

from github import Github
import requests
import time 
import pika 
import json

## Watches https://api.github.com/events for new pushEvents, forwards new events to rabbitmq
def handle_push_event(event):
    try:
        json_event = {}
        json_event['id'] = event.id
        json_event['actor'] = event.actor.name
        json_event['repo_name'] = event.repo.name
        json_event['repo_url'] = event.repo.clone_url
        json_event['created_at'] = str(event.created_at)
        json_event['payload'] = event.payload
        
        channel.basic_publish(exchange='ssp', routing_key='Push', body=json.dumps(json_event))
        print("[+] Event published")
    except Exception as err:
        print(f"[!] Unable to push event to rabbitmq: {err}")


def check_rate_limit():
    rate_limit = g.get_rate_limit().raw_data
    if rate_limit['core']['remaining'] > 10:
        return ("continue", 0)
    else:
        current_time = time.time()
        rl_reset_time = rate_limit['core']['reset']
        # if (wait_time := (rl_reset_time - current_time)) > 0:
        #     print(f"Rate limit is reached, sleeping for: {wait_time:.2f}s")
        #     time.sleep(rl_reset_time)
        return ("wait", (rl_reset_time - current_time))

def get_poll_limit():
    try:
        return int(requests.get(base_api_url + '/events').headers['x-poll-interval'])
    except KeyError as err:
        return 60

def watch_event_api():
    stop_watching = False
    while stop_watching != True:
        current_pol_time = get_poll_limit()
        try:
            for event in g.get_events().get_page(1):
                if event.type == "PushEvent":
                    print("[~] Handling PushEvent")
                    handle_push_event(event)
                else:
                    print("[!] Non push event")
        except Exception as err:
            print(err)
            stop_watching = True
        print("[~] Waiting for next poll")
        time.sleep(current_pol_time)
    


if __name__=="__main__":
    
    g = Github(login_or_token='5eeb2d768fb754b00f81',password='b58eddd24f4394a069b9d16a4efb681c25699930', per_page=100)
    base_api_url = 'https://api.github.com'
    
    rate_limit = check_rate_limit()
    if rate_limit[0] == 'continue':

        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('guest', 'guest')))
            channel = connection.channel()
            watch_event_api()
        except Exception as err:
            print(f'[!] Error caught in main loop: {err}')
        finally:
            connection.close()
    else:
        print(f'[!] Rate limit is exceeded please wait {rate_limit[1]:.2f}s')