#! python3
import yaml
import os
import engine
from rhythmic import Logger    # to exclude this dependency search through for Logger() and .writeDown()
from flask import Flask, request, render_template
import json


def get_boxops_configuration():

    try:
        with open("config.yaml", "r") as configuration_file:
            boxops_configuration = yaml.safe_load(configuration_file)
    except Exception as configuration_load_exception:
        print(configuration_load_exception)
        print("Failed to load configuration, using defaults")
        boxops_configuration = {
            "drills_directory": "drills",
            "web_ui_triggered_drills_directory": "webdrills"
        }

    return boxops_configuration


def collect_drills(boxops_configuration):
    drill_files = []
    cwd = os.getcwd()

    drills_path = "{}/{}".format(cwd, boxops_configuration["web_ui_triggered_drills_directory"])

    drills_folder_list = os.listdir(drills_path)
    for item in drills_folder_list:
        if os.path.isfile(drills_path+"/"+item):
            drill_files.append(drills_path+"/"+item)

    drills = []

    for the_drill_file in drill_files:
        the_drill = engine.load_yaml(the_drill_file)
        if engine.test_the_drill(the_drill):
            drills.append(the_drill)

    return drills


def get_the_drill_by_name(all_the_drills, the_drill_name):

    for the_drill in all_the_drills:
        if the_drill["name"] == the_drill_name:
            return the_drill

    return False


app = Flask(__name__)
log_path = os.getcwd() + "/log"
blocker = log_path + "/drill.blk"
boxops_logger = Logger(log_filename_postfix="boxopsweb", path_to_log=log_path)
boxops_logger.writeDown("Starting boxopsweb webservice")
boxops_configuration = get_boxops_configuration()
all_the_drills = collect_drills(boxops_configuration)
blocking_message = """
<html>
<body>
    <h2>The drill is in progress, try 15 minutes later.</h2>
</body>
</html>
"""


def args_to_html_inputs(the_drill):
    args_inputs = ""
    task_counter = 0

    for the_task in the_drill["tasks"]:
        task_counter += 1
        if engine.is_key_present(the_task["task"], "args"):
            for the_arg in the_task["task"]["args"]:
                args_inputs += "<br><b>{0}</b>:<br><input type=\"text\" name=\"task{1}_{0}\" value=\"{2}\"><br>" \
                    .format(the_arg, task_counter, the_task["task"]["args"][the_arg])

    return args_inputs


@app.route("/", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def index():
    global all_the_drills
    global boxops_configuration

    if os.path.exists(blocker):
        return blocking_message

    context = {
        "drills": all_the_drills
    }

    if request.method == "POST":
        the_data = request.form
        drill_arguments = {}
        for key, value in the_data.items():
            print("{}: {}".format(key, value))
            if key !="the_drill":
                drill_arguments[key] = value

        the_drill_name = the_data["the_drill"]
        context["the_selected_drill"] = the_drill_name

        the_drill_template = get_the_drill_by_name(all_the_drills, the_drill_name)

        if len(the_data) > 1:
            the_drill = engine.update_drill_arguments(the_drill_template, drill_arguments)
            context["args"] = args_to_html_inputs(the_drill)
        else:
            the_drill = the_drill_template

        with open(blocker, "w") as blocking_flag:
                blocking_flag.write(the_drill_name)

        context["execution_output"] = engine.execute_the_drill(the_drill)
        boxops_logger.writeDown(context["execution_output"])

        try:
            os.remove(blocker)
        except Exception as no_blocker_exception:
            print(no_blocker_exception)

    return render_template("boxopsweb.html", context=context)


@app.route("/args", methods=["POST"])
def get_drill_args():
    global all_the_drills

    if request.method == "POST":
        the_data = json.loads(request.data)

        the_drill_name = the_data["the_drill"]

        if the_drill_name == "-none-":
            return ""

        the_drill = get_the_drill_by_name(all_the_drills, the_drill_name)

        args_inputs = args_to_html_inputs(the_drill)

    else:
        args_inputs = "wrong method"

    return args_inputs


def main():
    app.run(debug=False, host="0.0.0.0", port="5100")


if __name__ == "__main__":
    main()
