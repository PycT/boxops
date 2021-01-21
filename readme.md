boxops is a simple linux scripted drills automator

* boxops
* boxopsweb

# boxops 

```
usage: python boxops.py [-h] [-t]

optional arguments:
-h, --help  show this help message and exit
-t          test drills configurations
-n N        filename of a drill to run or test. e.g. 'python boxops.py -t -n drill1.yaml'

```

boxops.py when launched executes serially all the drills found
in a `drills` folder near the boxops.

One file - one drill.
If no -n arguments specified, all the drills in a folder are run consecutively.

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

 **Important Note:** for nested or complex commands, like `kill $(ps -aux | grep process_name | awk '$1 ~ \"username\" {print $2; exit;}')`
specify the `user` field, even if it ought to be run on account of boxops process owner (e.g. `root`)

# boxopsweb.py 
boxopsweb is a server launched via WSGI, e.g. [gunicorn](https://gunicorn.org/)

``` gunicorn -w 3 -b 0.0.0.0:5100 boxopsweb:app --timeout 600 ```

boxopsweb collects all the drills in the `webdrills` folder near the script and gives 
a web-ui with selection by drill name and `Run` button.

When a drill is run via boxopsweb, it blocks the launching of another drill from same
folder.

