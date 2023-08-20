import requests

webhook_url = "https://watchdog.servatom.com/add/activity" # currently not operational
def main(event, context):
    requests.post(webhook_url, data = event)
    print(f"IAM Role change detected: {event}")