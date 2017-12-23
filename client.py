import pytumblr
import json
import vcr
import bs4
import sys


class Dashboard:
    def __init__(self, client):
        self.client = client
        # print(self.dashboard)
        self.indent = 2
        dashboard = self.client.dashboard(limit=50)
        json.dump(dashboard, open("dashboard.json", "w"), indent=self.indent)
        self.dashboard = json.load(open("dashboard.json"))["posts"]
        self.size = len(self.dashboard)
        print(self.size)
        print("ready!")
        print("\n")
        self.current_post = None
        self.current_post_index = -1

    def summary_post(self):
        try:
            post = self.current_post
            post_type = post["type"]
            # post_id = post["id"]
            post_summary = post["summary"]
            print(post_type)
            # print(post_id)
            print(post_summary)
        except KeyError or TypeError:
            print("no post found")
        print()

    def print_post(self):
        if self.current_post is None:
            print("no post found")
            return

        def trail(post):
            trail = post["trail"]
            content = []
            for reply in trail:
                content.append(reply["blog"]["name"])
                raw = [i for i in bs4.BeautifulSoup(reply["content_raw"], "html.parser").text.split("\n")]
                # print(raw)
                content.append(raw)
            return content

        try:
            post = self.current_post
            print(post["blog_name"] + " " * self.indent + post["date"])
            if post["type"] in ["text", "link", "answer", "video", "audio", "photo"]:
                if post["type"] == "photo":
                    for photo in post["photos"]:
                        print(photo["alt_sizes"][2]["url"])
                        print(photo["caption"])
                elif post["type"] == "link":
                    print(post["url"])
                    print(post["title"])
                    print(post["excerpt"])
                elif post["type"] == "audio" or post["type"] == "video":
                    print(post["source_url"])
                    print(post["source_title"])
                elif post["type"] == "answer":
                    print(post["asking_name"] + ": " + post["question"])
                    print()
                caption = trail(post)
                for item in caption:
                    if type(item) == list:
                        for line in item:
                            print(" " * self.indent + line)
                    else:
                        print(item + ":")
            elif post["type"] == "chat":
                for phrase in post["dialogue"]:
                    print(phrase["name"] + ": " + phrase["phrase"])
            else:
                print("unknown type %s" % post["type"])
        except KeyError or TypeError:
            print("no post found")
        print()

    def print_tags(self):
        post = self.current_post
        for tag in post["tags"]:
            print("#" + tag, end=" ")
        print()

    def like_post(self):
        post = self.current_post
        post_id = post["id"]
        reblog_key = post["reblog_key"]
        if post["liked"]:
            choice = input("would you like to unlike this post?\n").lower()
            while choice not in ["yes", "no"]:
                choice = input("would you like to unlike this post?\n").lower()
            if choice == "yes":
                self.client.unlike(post_id, reblog_key)
            else:
                return
        else:
            req = self.client.like(post_id, reblog_key)
            print("liked post %s" % post_id)

    def reblog_post(self):
        post = self.current_post
        post_id = post["id"]
        reblog_key = post["reblog_key"]
        blogs = [blog["name"] for blog in self.client.info()["user"]["blogs"]]
        for blog in blogs:
            print(blog)
        blog = input("reblog to what blog?\n")
        while blog not in blogs:
            for blog in blogs:
                print(blog)
            blog = input("reblog to what blog?\n")
        print("reblogging to %s" % blog)
        comment = input("add a comment?\n")
        if comment == "":
            self.client.reblog("{}.tumblr.com".format(blog), id=post_id, reblog_key=reblog_key)
        else:
            self.client.reblog("{}.tumblr.com".format(blog), id=post_id,
                               reblog_key=reblog_key, comment=comment)
        print("reblogged %s to %s" % (post_id, blog))

    def __iter__(self):
        return self

    def __next__(self):
        self.current_post_index += 1
        if self.current_post_index >= self.size:
            self.current_post = None
            raise StopIteration
        else:
            self.current_post = self.dashboard[self.current_post_index]
            self.summary_post()


class Server:
    def __init__(self):
        config = json.load(open("config.json", "r"))
        self.client = pytumblr.TumblrRestClient(
            config["key"], config["token"],
            config["oauth_token"], config["oauth_key"],
        )
        self.dashboard = Dashboard(self.client)

    @vcr.use_cassette("cassettes/info.yml")
    def client_info(self):
        info = self.client.info()["user"]["blogs"]
        for blog in info:
            print("url        : %s" % blog["url"])
            print("title      : %s" % blog["title"])
            print("description:\n%s" % blog["description"])
            print("total posts: %s" % blog["total_posts"])
            print()

    def choices(self):
        choice = input().lower()
        while choice != "quit":
            if choice == "print":
                self.dashboard.print_post()

            elif choice == "tags":
                self.dashboard.print_tags()

            elif choice == "like":
                self.dashboard.like_post()

            elif choice == "reblog":
                self.dashboard.reblog_post()

            elif choice == "" or choice == "next":
                try:
                    next(self.dashboard)
                except StopIteration:
                    print("no more posts!")
                    choice = input("would you like to reload?\n").lower()
                    while choice not in ["yes", "no"]:
                        choice = input("would you like to reload?\n").lower()
                    if choice == "yes":
                        self.dashboard = Dashboard(self.client)
                    else:
                        return
            else:
                print("unknown command")

            choice = input().lower()

        print("see you later :o")
        sys.exit()


if __name__ == "__main__":
    server = Server()
    # server.client_info()
    server.choices()
