import subprocess
import os
from rhythmic import Logger
from yaml import safe_load as yaml_load
import requests
import json

# working_dir = os.getcwd()
# blocker = working_dir + "/deploy.blk"
# path_to_config = working_dir + "/stands-enabled"


# deploy_logger = Logger(log_filename_postfix="deploy", path_to_log=working_dir)

def load_yaml(yaml_file_name):

    try:
        with open(yaml_file_name, "r") as yaml_file:
            try:
                loaded_data = yaml_load(yaml_file)
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
            print("{} is a required parameter".format(the_key))
            return False
    except Exception as key_presence_failure:
        print("Exception: {}".format(key_presence_failure))
        print("{} is a required parameter".format(the_key))
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
            print(class_test_exception)
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
                        print("            The '{}' arg is of a wrong type - must be a string; ignoring the arg.".format(arg))
                        the_task.pop(arg, False)
        except Exception as no_args_exception:
            print(no_args_exception)
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
            print(action_presence_exception)
            print("                No action specified (ok)")

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
            print(no_webhook_exception)
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
