import subprocess
import yaml
import requests
import json

def load_yaml(yaml_file_name):

    try:
        with open(yaml_file_name, "r") as yaml_file:
            try:
                loaded_data = yaml.safe_load(yaml_file)
            except Exception as yaml_reading_fault:
                print(yaml_reading_fault)
                loaded_data = False
    except Exception as general_fault:
        print(general_fault)
        loaded_data = False

    return loaded_data


def is_class(the_entity, class_name):

    if the_entity.__class__.__name__ == class_name:
        return True

    return False


def is_key_present(the_entity, the_key):

    try:
        if len(the_entity[the_key]) == 0:
            print("No {} configured".format(the_key))
            return False
    except Exception as key_presence_failure:
        print(key_presence_failure)
        print("No {} configured".format(the_key))
        return False

    return True


def test_the_drill(the_drill):

    def test_the_task(the_task):
        """
        - task:  # required at least 1
            name: ""  # required
            args:
                arg_name1: "value"
                arg_nameN: "value"
            action: "bash -c {arg_name1}, {arg_nameN}"
            webhook:
                url: ""
                headers:
                    key: value
                data:
                    key: value

        """

        # Testing if task is loaded as dictionary
        try:
            if not is_class(the_task, "dict"):
                print("        The task configuration is wrong.")
                return False
        except Exception as class_test_exception:
            print("            {}".format(class_test_exception))
            print("            Didn't manage to perform a configuration test")
            return False

        # Test name presence
        if not is_key_present(the_task, "name"):
            print("            A name is required for any task")
            return False

        print("            The task name: {}".format(the_task["name"]))

        # Test args dictionary validity if present
        print("            Testing args")
        try:
            if not is_class(the_task["args"], "dict"):
                print("            args are configured in a wrong way")
                return False
            else:
                for arg, value in the_task["args"].items():
                    if not is_class(value, "str"):
                        print("            The '{}' arg is of a wrong type - must be a string; ignoring the arg."
                              .format(arg))
                        the_task.pop(arg, False)
                    else:
                        print("                {}: {}".format(arg, value))
        except Exception as no_args_exception:
            print("                {}".format(no_args_exception))
            print("                No args specified (ok)")

        # Test action string
        print("            Testing action configuration")
        try:
            if not is_class(the_task["action"], "str"):
                print("                The action is misconfigured.")
                return False
            else:
                if is_key_present(the_task, "args"):
                    for arg, value in the_task["args"].items():
                        the_task["action"] = the_task["action"].replace("{{{}}}".format(arg), value)
                    print("                {}".format(the_task["action"]))
        except Exception as action_presence_exception:
            print("                {}".format(action_presence_exception))
            print("                No action specified (ok)")

        # Test user string
        print("            Testing user configuration")
        try:
            if not is_class(the_task["user"], "str"):
                print("                The user is misconfigured.")
                return False
        except Exception as user_presence_exception:
            print("                {}".format(user_presence_exception))
            print("                No user specified (ok)")

        # Test directory string
        print("            Testing directory configuration")
        try:
            if not is_class(the_task["directory"], "str"):
                print("                The directory is misconfigured.")
                return False
        except Exception as directory_presence_exception:
            print("                {}".format(directory_presence_exception))
            print("                No directory specified (ok)")

        # Test webhooks
        print("            Testing webhook configuration")
        try:
            if not is_class(the_task["webhook"], "dict"):
                print("                The webhook is misconfigured.")
                the_task.pop("webhook", False)
            else:
                # Test the url
                if not is_key_present(the_task["webhook"], "url"):
                    print("                An URL is required for a webhook")
                    return False
                elif not is_class(the_task["webhook"]["url"], "str"):
                    print("                The webhook is misconfigured")
                    return False

                print("                {}".format(the_task["webhook"]["url"]))


                # Test headers
                if is_key_present(the_task["webhook"], "headers"):
                    if not is_class(the_task["webhook"]["headers"], "dict"):
                        print("            Webhook headers are misconfigured")
                        return False

                # Test data
                if is_key_present(the_task["webhook"], "data"):
                    if not is_class(the_task["webhook"]["data"], "dict"):
                        print("            Webhook data is misconfigured")
                        return False

        except Exception as no_webhook_exception:
            print("        {}".format(no_webhook_exception))
            print("        No webhook specified (ok)")

        return True

    # ==========================================================

    # Testing if configuration is loaded as dictionary
    try:
        if not is_class(the_drill, "dict"):
            print("The drill configuration is wrong.")
            return False
    except Exception as class_test_exception:
        print(class_test_exception)
        print("Didn't manage to perform a configuration test")
        return False

    # Test drill name presence
    if not is_key_present(the_drill, "name"):
        print("A name is required for the drill")
        return False

    if not is_class(the_drill["name"], "str"):
        print("The drill name is misconfigured")
        return False

    print("Testing the drill '{}'".format(the_drill["name"]))

    # Test tasks presence
    if not is_key_present(the_drill, "tasks"):
        print("No tasks configured")
        return False

    if not is_class(the_drill["tasks"], "list"):
        print("Tasks are miskonfigured")
        return False

    counter = 1
    print("    Testing tasks: ")
    for the_task in the_drill["tasks"]:
        print()
        print("        Testing task {} configuration".format(counter))
        counter += 1
        if not test_the_task(the_task["task"]):
            return False

    return True


def execute_the_drill(the_drill):

    def execute_the_task(the_task):

        execution_output = "\n Executing task: {} \n".format(the_task["name"])
        if is_key_present(the_task, "action"):
            if is_key_present(the_task, "directory"):
                the_action = "cd {}; " + the_task["action"]
            else:
                the_action = the_task["action"]

            if is_key_present(the_task, "user"):
                execution_result = subprocess.run(
                    ["runuser", "-l", the_task["user"], the_action],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
            else:
                execution_result = subprocess.run(
                    the_action.split(" "),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )

            execution_output += execution_result.stdout.decode()

        if is_key_present(the_task, "webhook"):
            if is_key_present(the_task["webhook"], "data"):
                the_webhook_data = the_task["webhook"]["data"]
            else:
                the_webhook_data = {
                    "content": "pew!"
                }

            if is_key_present(the_task["webhook"], "headers"):
                the_webhook_headers = the_task["webhook"]["headers"]
            else:
                the_webhook_headers = {
                    "From": "boxops"
                }

            try:
                the_webhook_payload = json.dumps(the_webhook_data)
                request_result = requests.request("post",
                                                  the_task["webhook"]["url"],
                                                  data=the_webhook_payload,
                                                  headers=the_webhook_headers)
            except Exception as webhook_exception:
                print(webhook_exception)
                request_result = "Webhook failed: {}".format(webhook_exception)

            execution_output += "\n Webhook ok: {}\n".format(request_result)

            print(execution_output)

        return execution_output

    print("Executing the drill: {}".format(the_drill["name"]))

    the_drill_output = ""

    for the_task in the_drill["tasks"]:
        the_drill_output += execute_the_task(the_task["task"])

    return the_drill_output
