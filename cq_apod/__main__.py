from apscheduler.schedulers.blocking import BlockingScheduler
import urllib.request
import json
import sys

def load_config():
    with open("config.json") as f:
        return json.load(f)

def is_outdated(new_date):
    with open("last_image_date.txt", "+w") as f:
        content = f.read()
        if content == new_date:
            return False
        else:
            f.write(new_date)
            return True
        
def cq_send_message(api, group, message):
    safe_msg = urllib.parse.quote(message)
    url = "http://" + api + "/send_group_msg?group_id=" + group + "&message=" + safe_msg
    print("Sending message to CQ: " + url)
    result = urllib.request.urlopen(url).read()
    print("Result: " + result.decode("utf-8"))

def image_of_the_day():
    config = load_config()

    print("Fetching image of the day...")
    content = urllib.request \
        .urlopen("https://api.nasa.gov/planetary/apod?api_key=" + config["API_KEY"]).read()
    content_json = json.loads(content)
    print("Received ", content_json)

    if not is_outdated(content_json["date"]):
        print("No new image of the day")
        return
    print("New image of the day! " + content_json["date"])

    cq_send_message(config["CQ_API"], config["CQ_GROUP"], content_json["title"])
    image_msg = "[CQ:image,file=" + content_json["url"] + "]"
    cq_send_message(config["CQ_API"], config["CQ_GROUP"], image_msg)
    cq_send_message(config["CQ_API"], config["CQ_GROUP"], content_json["explanation"])

def main():
    args = sys.argv[1:]
    if args and args[0] == "test":
        image_of_the_day()
        return
    sched = BlockingScheduler()
    # every hour to ensure images delivered on time
    sched.add_job(image_of_the_day, 'cron', minute=0)
    sched.start()


if __name__ == "__main__":
    main()