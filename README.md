simple, light tumblr client for the python console.

## usage
1. install requirements with `pip install -r requirements.txt` in the installed directory
2. create a 'config.json' file like the following:
  ```json {
  "key": <your key here>,
  "secret": <your key here>,
  "oauth_token": <your key here>,
  "oauth_secret": <your key here>
}
```
to get these keys, head over to [the application page on tumblr](https://www.tumblr.com/oauth/apps) and register an application. use [the api console](https://api.tumblr.com/console/calls/user/info) to get the oauth information.
3. run the program and have fun or whatever.

## commands:
* reblog
    * reblogs post to the blog of the user's choice
* like
    * likes or unlikes the post (if already liked)
* next (or empty return¡)
    * goes to the next post in the dashboard buffer
* quit
    * exits the program

