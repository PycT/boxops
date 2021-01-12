from flask import Flask, request, render_template
import subprocess
import os
from rhythmic import Logger
from yaml import safe_load as yaml_load
import requests
import json

working_dir = os.getcwd()
blocker = working_dir + "/deploy.blk"
path_to_config = working_dir + "/stands-enabled"


deploy_logger = Logger(log_filename_postfix="deploy", path_to_log=working_dir)
deploy_logger.writeDown("=========== Deployer Service Start ==============")


def test_stand_configuration(stand_configuration):

    def is_class(the_entity, class_name):

        if the_entity.__class__.__name__ == class_name:
            return True
        else:
            return False

    def test_step(step):

        if not is_class(step, "dict"):
            print("Step configuration wrong")
            return False

        try:
            if not is_class(step["description"], "str"):
                print("Step description configuration is wrong")
                return False
        except Exception as e:
            print("{} not set but it is ok.".format(e))

        try:
            if not is_class(step["path"], "str"):
                print("Step path configuration is wrong")
                return False
        except Exception as e:
            print("{} not set but it is ok.".format(e))

        try:
            if not is_class(step["user"], "str"):
                print("Step user configuration is wrong")
                return False
        except Exception as e:
            print("{} not set but it is ok.".format(e))

        try:
            if not is_class(step["command"], "str"):
                print("Step command configuration is wrong")
                return False
        except Exception as e:
            print(e)
            print("The step has to have a command")
            return False

        return True

    def test_webhooks(stand):

        try:
            if not is_class(stand["webhooks"], "dict"):
                print("Webhooks configuration is wrong")
                return False
        except Exception as e:
            print("{} not set but it is ok.".format(e))

        try:
            if not is_class(stand["webhooks"]["discord"], "str"):
                print("Discord webhook configuration is wrong")
                return False
        except Exception as e:
            print("{} not set but it is ok.".format(e))

        return True

    # Test for stand in yaml
    try:
        if not is_class(stand_configuration, "dict"):
            print("Stand configuration is wrong")
            return False
    except Exception as e:
        print(e)
        print("Stand not found")
        return False

    # test for stand name presence
    try:
        if not is_class(stand_configuration["name"], "str"):
            print("Stand has to have a name")
    except Exception as e:
        print(e)
        print("Stand has to have a name")
        return False

    # test webhooks if present
    if not test_webhooks(stand_configuration):
        print("Webhooks configuration is wrong")
        return False

    # test info steps
    try:
        if is_class(stand_configuration["info"], "list"):
            step_counter = 0
            for the_step in stand_configuration["info"]:
                step_counter += 1
                print("Testing info step {}".format(step_counter))
                if not test_step(the_step["step"]):
                    print("Info step {} is misconfigured".format(step_counter))
                    return False
    except Exception as e:
        print("{} is not set and it is ok".format(e))

    # test steps
    try:
        if not is_class(stand_configuration["steps"], "list"):
            print("Stand steps configuration is wrong")
            return False
    except Exception as e:
        print(e)
        print("Stand must have steps to be configured")
        return False

    step_counter = 0
    for the_step in stand_configuration["steps"]:
        step_counter += 1
        print("Testing scenario step {}".format(step_counter))
        if not test_step(the_step["step"]):
            print("Step {} is misconfigured".format(step_counter))
            return False

    return True

def get_deploy_configuration(path_to_config=path_to_config):

    deploy_configuration = []

    config_dir_content = os.listdir(path_to_config)
    for an_item in config_dir_content:
        the_loadable = "{}/{}".format(path_to_config, an_item)
        if os.path.isfile(the_loadable):
            print("----------------------")
            print(an_item)
            try:
                with open(the_loadable, "r") as config_yaml:
                    deploy_configuration_candidate = yaml_load(config_yaml)
                    if test_stand_configuration(deploy_configuration_candidate):
                        print("{} is added to deployer configuration".format(an_item))
                        deploy_configuration.append(deploy_configuration_candidate)
            except Exception as e:
                print(e)

    return deploy_configuration


def get_steps(deploy_configuration, the_stand):

    steps = {}
    for stand in deploy_configuration:
        if stand["name"] == the_stand:
            steps = stand["steps"]
            break

    return steps


def get_webhooks(deploy_configuration, the_stand):

    webhooks = {}
    for stand in deploy_configuration:
        if stand["name"] == the_stand:

            # Dicord:
            try:
                webhooks["discord"] = stand["webhooks"]["discord"]
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
        operation_output += repr(e) + "\n\n"

    the_user = ""

    try:
        the_user = step["user"]
    except Exception as e:
        print(e)
        operation_output += repr(e) + "\n\n"

    user_path = ""

    try:
        if len(step["path"]) > 0:
            if len(the_user) == 0:
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

                process_result = subprocess.run(
                                    ["runuser", "-l", the_user, "-c", user_command],
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                                 )
            else:
                process_result = subprocess.run(
                                    step["command"].split(" "),
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                                 )
            execution_output += process_result.stdout.decode()
            deploy_logger.writeDown(execution_output)
            operation_output += execution_output + "\n<br>\n"

    except Exception as e:
        print(e)
        # operation_output += repr(e) + "\n\n"

    return operation_output + "\n --- \n"


def execute_webhooks(webhooks, the_message):

    # Discord
    the_url = webhooks["discord"]
    if the_url == "":
        return False

    the_headers = {
        "Content-Type": "application/json"
    }
    webhook_data = {
        "content": the_message
    }

    the_payload = json.dumps(webhook_data)

    try:
        request_result = requests.request("post", the_url, data=the_payload, headers=the_headers)
    except Exception as e:
        print(e)

    return request_result


deploy_configuration = get_deploy_configuration()

app = Flask(__name__)


@app.route("/", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def index():

    deploy_logger.writeDown(request.method)
    context = {
        "stands": [],
        "deploy_in_progress": False,
        "the_stand": ""
    }

    for stand in deploy_configuration:
        context["stands"].append(stand["name"])

    if os.path.exists(blocker):
        context["deploy_in_progress"] = True
        return render_template("deploy.html", context=context)

    if request.method == "POST":

        with open(blocker, "w") as blockerfile:
            blockerfile.write(".")

        the_stand = request.values["the_stand"]
        the_branch = request.values["the_branch"]
        context["the_stand"] = the_stand
        context["the_branch"] = the_branch

        deploy_logger.writeDown(the_stand)
        deploy_logger.writeDown(the_branch)

        webhooks = get_webhooks(deploy_configuration, the_stand)
        if len(webhooks) > 0:
            the_start_message = """Deploy in progress. 
            \n The stand: ```{}``` \n The branch: ```{}```""".format(the_stand, the_branch)
            execute_webhooks(webhooks, the_start_message)

        scenario = get_steps(deploy_configuration, the_stand)
        scenario_output = ""

        for the_step in scenario:
            if the_step["step"]["description"] == "Git branch":
                the_step["step"]["command"] = "git checkout {}".format(the_branch)

            scenario_output += execute_step(the_step["step"])

        context["the_stand"] = the_stand
        context["the_branch"] = the_branch
        context["scenario_output"] = scenario_output.replace("\n", "<br>")

        os.remove(blocker)

        if len(webhooks) > 0:
            the_end_message = """\n---\n Deploy complete. 
            \n The stand: ```{}``` \n The branch: ```{}```""".format(the_stand, the_branch)
            execute_webhooks(webhooks, the_end_message)

    return render_template("deploy.html", context=context)


def main():
    app.run(debug=False, host="0.0.0.0", port="5100")


if __name__ == "__main__":
    main()
