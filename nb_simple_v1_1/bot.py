# alert bot thing based on NB but also waaaay less complicated
# Version: 1.1
# Author: /u/git-commit-die

# this is incredibly lazy but i had to basically rewrite everything in a couple hours so this is the best i've got
# also i only tested this a couple times but it didn't break soooooo 


import threading
import re
import datetime
import json
import praw

from formatting import *


try:
    r = praw.Reddit("user") # obtain PRAW instance using credentials stored in praw.ini file
except Exception as e:
    print(e)
    print("ERROR: failed to load credentials ini file, could not initialize PRAW instance")
    exit(1)

try:
    with open("config.json", "r") as f: # load config file
        config = json.load(f)
except Exception as e:
    print(e)
    print("failed to load config.json")
    exit(1)


def alert_recipients(item, rule, match):
    '''
    Send alert message to recipients

    item  (Submission | Comment) : PRAW Submission or Comment instance
    rule  (dict)                 : Dictionary rule object
    match (str)                  : Matched string
    '''

    item_type = item.__class__.__name__

    message_title = f"{item_type} Matched Rule: {rule['name']}"

    message_body = ""
    message_body += f"**Match**: *\"{match}\"*"                                                           + "\n\n"
    message_body += f"**{item_type} Fullname:** {('t1_' if item_type == 'Comment' else 't3_') + item.id}" + "\n\n"
    message_body += f"**Author:** /u/{item.author.name}"                                                  + "\n\n"
    message_body += f"**Subreddit:** /r/{item.subreddit.display_name}"                                    + "\n\n"
    if item_type == "Submission":
        message_body += f"**Title:** *\"{format_string(item.title)}\"*"                                   + "\n\n"
        if item.is_self and item.selftext:
            message_body += f"**Selftext:**\n{format_block(item.selftext)}"                               + "\n\n"
        else if item.url:
            message_body += f"**Link URL:** {item.url}"                                                   + "\n\n"
    elif item_type == "Comment":
        message_body += f"**Body:**\n{format_block(item.body)}"                                           + "\n\n"
    message_body += f"**URL:** https://www.reddit.com{item.permalink}"                                    + "\n\n"
    message_body += f"**Time:** {datetime.datetime.fromtimestamp(item.created_utc):%Y-%m-%d %H:%M:%S}"

    message_body += "\n\n---\n\n*This message was sent automatically.*"

    for recipient in config["recipients"]:
        try:
            r.redditor(recipient).message(message_title, message_body)
        except Exception as e:
            print(e)
            print("failed to notify recipient /u/" + recipient)


def check_item(item):
    '''
    Check if item matches rules defined in config.json

    item (Submission | Comment) : PRAW Submission or Comment instance to be checked
    '''

    if item.author.name in config["recipients"]: return False

    for rule in config["rules"]:

        for search_field in rule["search_fields"]:

            if not hasattr(item, search_field): continue

            for search_expression in rule["search_expressions"]:
                search = re.search(search_expression, getattr(item, search_field), re.IGNORECASE)
                if search:
                    print(f"item matched rule \"{rule['name']}\"")
                    alert_recipients(item, rule, search.group(0))
                    return True
                

def watch_submissions(subreddit):
    '''
    Initialise submission stream

    subreddit (str) : Subreddit display name 
    '''

    for submission in r.subreddit(subreddit).stream.submissions(skip_existing=True):
        try:
            check_item(submission)
            print("checked submission " + submission.id)
        except Exception as e:
            print(e)
            print("failed to check submission " + submission.id)


def watch_comments(subreddit):
    '''
    Initialise comment stream

    subreddit (str) : Subreddit display name 
    '''

    for comment in r.subreddit(subreddit).stream.comments(skip_existing=True):
        try:
            check_item(comment)
            print("checked comment " + comment.id)
        except Exception as e:
            print(e)
            print("failed to check comment " + comment.id)


def run():
    stream_threads = []

    # multithreading isn't an ideal solution but it's easy ¯\_(ツ)_/¯
    for subreddit in config["subreddits"]:
        stream_threads.append(threading.Thread(target=watch_submissions, args=(subreddit,)))
        stream_threads.append(threading.Thread(target=watch_comments, args=(subreddit,)))

    for stream_thread in stream_threads:
        stream_thread.start()

    print("started")


if __name__ == "__main__":
    run()
