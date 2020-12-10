from flask import Flask, request, render_template
import subprocess
import os
from rhythmic import Logger
from yaml import safe_load as yaml_load
import requests
import json

path_to_log = os.getcwd()
blocker = path_to_log + "/deploy.blk"


deploy_logger = Logger(log_filename_postfix = "deploy", path_to_log = path_to_log)
deploy_logger.writeDown("=========== Deployer Service Start ==============")

def get_deploy_configuration():

    with open("config.yaml", "r") as config_yaml:
        deploy_configuration = yaml_load(config_yaml)

    return deploy_configuration

def get_steps(deploy_configuration, the_stand):

    steps = {}
    for stand in deploy_configuration:
        if stand["stand"]["name"] == the_stand:
            steps = stand["stand"]["steps"]
            break

    return steps

def get_webhooks(deploy_configuration, the_stand):

    webhooks = {}
    for stand in deploy_configuration:
        if stand["stand"]["name"] == the_stand:

            # Dicord:
            try:
                webhooks["discord"] = stand["stand"]["webhooks"]["discord"]
            except Exception as e:
                print(e)

            break

    return webhooks

def execute_step(step):
    """
        - step:
              description: "Cleaning"
              path: "/var/www"
              user: ""
              command: "rm -rf mydir"
    """
    operation_output = ""

    try:
        if len(step["description"]) > 0:
            deploy_logger.writeDown(step["description"])
            operation_output += step["description"] + "\n\n"
        else:
            deploy_logger.writeDown("step")
            operation_output += " step\n "
    except Exception as e:
        print(e)
#         operation_output += repr(e) + "\n\n"

    the_user = ""

    try:
        the_user = step["user"]
    except Exception as e:
        print(e)
        # operation_output += repr(e) + "\n\n"


    user_path = ""

    try:
        if len(step["path"]) > 0:
            if len(the_user)== 0:
                os.chdir(step["path"])
            else:
                user_path = step["path"]
    except Exception as e:
        print(e)
        # operation_output += repr(e) + "\n\n"

    try:
        if len(step["command"]) > 0:
            execution_output = ""
            if len(the_user) > 0:
                if len(user_path) > 0:
                    user_command = "cd {}; ".format(user_path) + step["command"]
                else:
                    user_command = step["command"]
		
                process_result = subprocess.run(\
                                    ["runuser", "-l", the_user, "-c", user_command],\
                                    stdout = subprocess.PIPE, stderr = subprocess.STDOUT\
                                 )
            else:
                process_result = subprocess.run(\
                                    step["command"].split(" "),\
                                    stdout = subprocess.PIPE, stderr = subprocess.STDOUT\
                                 )
            execution_output += process_result.stdout.decode()
            deploy_logger.writeDown(execution_output)
            operation_output += execution_output + "\n<br>\n"

    except Exception as e:
        print(e)
        # operation_output += repr(e) + "\n\n"

    return operation_output + "\n --- \n"


def execute_webhooks(webhooks, the_stand, the_branch):

    # Discord
    the_url = webhooks["discord"]
    the_headers = {
        "Content-Type": "application/json"
    }
    webhook_data = {
        "content": """@here Deploy in progress. 
        \n The stand: ```{}``` \n The branch: ```{}```""".format(the_stand, the_branch)
    }

    the_payload = json.dumps(webhook_data)

    request_result = requests.request("post", the_url, data=the_payload, headers=the_headers)

    return request_result


deploy_configuration = get_deploy_configuration()

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def index():

    deploy_logger.writeDown(request.method)
    context = {
        "stands": [],
        "deploy_in_progress": False
    }

    for stand in deploy_configuration:
        context["stands"].append(stand["stand"]["name"])

    if os.path.exists(blocker):
        context["deploy_in_progress"] = True
        return render_template("deploy.html", context=context)

    if request.method == "POST":

        with open(blocker, "w") as blockerfile:
            blockerfile.write(".")

        the_stand = request.values["the_stand"]
        the_branch = request.values["the_branch"]

        deploy_logger.writeDown(the_stand)
        deploy_logger.writeDown(the_branch)

        webhooks = get_webhooks(deploy_configuration, the_stand)
        if len(webhooks) > 0:
            execute_webhooks(webhooks, the_stand, the_branch)


        scenario = get_steps(deploy_configuration, the_stand)
        scenario_output = ""

        for the_step in scenario:
            if the_step["step"]["description"] == "Git branch":
                the_step["step"]["command"] = "git checkout {}".format(the_branch)

            scenario_output += execute_step(the_step["step"])

        context["the_stand"] = the_stand
        context["the_branch"] = the_branch
        context["scenario_output"] = scenario_output.replace("\n","<br>")

        os.remove(blocker)

    return render_template("deploy.html", context=context)


def main():
    app.run(debug = False, host="0.0.0.0", port = "5100")

if __name__ == "__main__":
    main()
