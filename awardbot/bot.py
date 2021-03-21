import re
import praw

# list of common awards including the award ID and the award's cost in coins
# full list of awards avaliable at https://praw.readthedocs.io/en/latest/code_overview/models/submission.html
awards = {
    "silver": ("gid_1", 100),
    "gold": ("gid_2", "gold", 500),
    "platinum": ("gid_3", 1800),
    "argentium": ("award_4ca5a4e6-8873-4ac5-99b9-71b1d5161a91", 20000),
    "ternion": ("award_2385c499-a1fb-44ec-b9b7-d260f3dc55de", 50000),
    "love": ("award_5eac457f-ebac-449b-93a7-eb17b557f03c", 20),
    "starstruck": ("award_abb865cf-620b-4219-8777-3658cf9091fb", 20),
    "all-seeing-upvote": ("award_b4ff447e-05a5-42dc-9002-63568807cfe6", 30),
    "narwal-salute": ("award_a2506925-fc82-4d6c-ae3b-b7217e09d7f0", 30),
    "wholesome-seal-of-approval": ("award_c4b2e438-16bb-4568-88e7-7893b7662944", 30),
}


# Change these as needed.

subreddit        = "teenagers"         # subreddit to award submissions in, works with multireddits (e.g. redditdev+memes+u_AutoModerator)
anonymous        = True                # show username when awarding item
message          = None                # message sent when awarding item
award            = awards["silver"]    # selected award tuple(id, cost)
ignored_keywords = ["award"]           # ignore submissions containing words/phrases, works with regex
ignored_flairs   = ["serious", "rant"] # ignore submissions with specific flair classes
max_coins_limit  = 1500                # maximum number of coins to spend


# initialize PRAW Reddit instance using credentials stored in praw.ini file
r = praw.Reddit("bot")

coins_spent = 0

def validate_thing(thing):

    if thing.over_18:                                           # check if NSFW
        return False

    for flair in ignored_flairs:                                # check flair
        if thing.link_flair_css_class == flair:
            return False

    for field in ["title", "selftext", "body"]:
        if not hasattr(thing, field):
            continue

        for keyword in ignored_keywords:                        # check for keywords
            if re.search(keyword, thing[field], re.IGNORECASE):
                return False

    return True

# start streaming new submissions
for s in r.subreddit(subreddit).stream.submissions(skip_existing=True):

    # skip submissions flaired as serious, rant, or tagged as NSFW
    if not validate_thing(s):
        continue

    # award the submission
    s.award(gild_type=award[0], is_anonymous=anonymous, message=message)
    coins_spent += award[1]

    print(f"awarded submission {s.name} \"{s.title}\"")

    # exit when maximum number of coins spent
    if coins_spent + award[1] > max_coins_limit:
        break
