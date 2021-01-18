boxops is a simple linux scripted drills automator

* boxops
* boxopsweb

# boxops 

```
usage: boxops.py [-h] [-t]

optional arguments:
-h, --help  show this help message and exit
-t          test drills configurations
```

boxops.py (has a soft link `boxops`) when launched executes serially all the drills found
in a `drills` folder near the boxops.

One file - one drill.

The general structure of a drill yaml is as follows:

```yaml
# * drill - a scenario with tasks
# * task - and end-unit ot execute
# * argument - a variable parameter to use within a task
---
name: "the drill name"  # required
tasks:  # required
    - task:  # required at least 1
        name: "my task"  # required
        args:  # useful for boxopsweb
            arg_name1: "value1"
            arg_nameN: "valueN"
        action: "bash -c {arg_name1}, {arg_nameN}"
        user: ""  # *nix user on who's account to execute the action
        directory: ""  # a directory to navigate to before the action execution
        webhook:  # a post request with following headers (id present) and data (if present) is sent
            url: "url"
            headers:  # html-headers for the webhook
                key1: value1
                keyN: valueN
            data:  # data to send to a webhook url
                key1: value1
                keyN: valueN

```

Also see `example.yaml`

# boxopsweb.py 
boxopsweb is a server launched via WSGI, e.g. [gunicorn](https://gunicorn.org/)

``` gunicorn -w 3 -b 0.0.0.0:5100 boxopsweb:app --timeout 600 ```

boxopsweb collects all the drills in the `webdrills` folder near the script and gives 
a web-ui with selection by drill name and `Run` button.

When a drill is run via boxopsweb, it blocks the launching of another drill from same
folder.

