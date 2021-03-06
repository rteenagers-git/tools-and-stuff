# deleteything
# Version: 1.3
# Author: /u/git-commit-die


import praw
import re


try:
    r = praw.Reddit("user") # obtain PRAW instance using credentials stored in praw.ini file
except Exception as e:
    print(e)
    print("ERROR: failed to load credentials ini file, could not initialize PRAW instance")
    exit(1)


def delete_comments(user, delete_distinguished=False, delete_regex=False):
    '''
        Deletes comments made by a user.

        user                 (Redditor) : An authenticated PRAW Redditor instance whose comments are to be deleted.
        delete_distinguished (bool)     : Delete distinguished comments - true/false
    '''

    print("deleting comments...")

    deleted_count = 0

    feeds = [user.comments.new(limit=None), user.comments.hot(limit=None)]

    # testing showed that each of these feeds need to be sorted seperately to ensure that everything's deleted
    for feed_since in ["all", "year", "month", "week", "day", "hour"]:
        feeds.append(user.comments.top(feed_since, limit=None))
        feeds.append(user.comments.controversial(feed_since, limit=None))

    for feed in feeds:
        for comment in feed:
            if not delete_distinguished and comment.distinguished: continue                        # skip distingushed
            if delete_regex and not re.search(delete_regex, comment.body, re.IGNORECASE): continue # skip if comment doesn't match regex

            comment.delete()

            deleted_count += 1

            print(f"deleted {comment.name}")

    print(f"done deleting {str(deleted_count)} comments.")


def delete_submissions(user, delete_distinguished=False, delete_regex=None):
    '''
        Deletes submissions made by a user.

        user                 (Redditor) : An authenticated PRAW Redditor instance whose submissions are to be deleted.
        delete_distinguished (bool)     : Delete distinguished submissions - true/false
    '''
    
    print("deleting submissions...")

    deleted_count = 0

    feeds = [user.submissions.new(limit=None), user.submissions.hot(limit=None)]

    # testing showed that each of these feeds need to be sorted seperately to ensure that everything's deleted
    for feed_since in ["all", "year", "month", "week", "day", "hour"]:
        feeds.append(user.submissions.top(feed_since, limit=None))
        feeds.append(user.submissions.controversial(feed_since, limit=None))

    for feed in feeds:
        for submission in feed:
            if submission.distinguished and not delete_distinguished: continue                               # skip distingushed
            if delete_regex:                                                                                 # skip if submission title and selftext doesn't match regex
                if re.search(delete_regex, submission.title, re.IGNORECASE):                                 #     check title
                    pass
                elif submission.is_self and not re.search(delete_regex, submission.selftext, re.IGNORECASE): #     check selftext
                    continue

            submission.delete()

            deleted_count += 1

            print(f"deleted {submission.name}")
    
    print(f"done deleting {str(deleted_count)} submissions.")


def run():
    print("""--------------------------------------------------------------------------------
NOTICE: Due to reddit's API restrictions this script may not be able to delete
everything you've posted if you've made a very large number of
submissions/comments. It will however delete all of the submissions and comments
that are visible when a user visits your profile.

Be warned that there are public 3rd party services that archive your reddit data
even after it's deleted. The most notable of these services if pushshift.io.
--------------------------------------------------------------------------------
""")

    me = r.user.me()

    mode = input("Select Mode [Submissions/Comments/Both] (default Comments): ")
    mode = mode.lower() if mode else "c"                                         # select comments mode as default

    delete_distinsuished = input("Delete Distinguished Items? [y/n] (default n): ") == "y"
    delete_regex         = input("Delete Items Matching Regex (optional): ")

    if re.match(r"c(omments)?", mode):

        if input(f"This will delete all visible comments for /u/{me.name}, are you sure? [Y/n]: ") == "Y":
            delete_comments(me, delete_distinsuished, delete_regex)

    elif re.match(r"s(ubmissions)?", mode):

        if input(f"This will delete all visible submissions for /u/{me.name}, are you sure? [Y/n]: ") == "Y":
            delete_submissions(me, delete_distinsuished, delete_regex)

    elif re.match(r"b(oth)?", mode):

        if input(f"This will delete all visible submissions and comments for /u/{me.name}, are you sure? [Y/n]: ") == "Y":
            delete_comments(me, delete_distinsuished, delete_regex)
            delete_submissions(me, delete_distinsuished, delete_regex)

    print("exiting...")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print()
        print("aborting...")
        print()
