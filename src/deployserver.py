from flask import Flask, request, render_template
import subprocess
import os
from rhythmic import Logger
from yaml import safe_load as yaml_load

# deploy_logger = Logger(log_filename_postfix = "deploy", path_to_log = ".")
# deploy_logger.writeDown("=========== Deployer Service Start ==============")

def get_deploy_configuration():

    with open("config.yaml", "r") as config_yaml:
        deploy_configuration = yaml_load(config_yaml)

    return deploy_configuration

deploy_configuration = get_deploy_configuration()

def execute_step(step):
    pass  # TODO: step execution

app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
@app.route("/index", methods=["POST", "GET"])
def index():

    print(request.method)
    context = {
        "stands": []
    }

    for stand in deploy_configuration:
        context["stands"].append(stand["stand"]["name"])

    if request.method == "POST":
        the_stand = request.values["the_stand"]
        the_branch = request.values["the_branch"]

        print(the_stand)
        print(the_branch)

    return render_template("deploy.html", context=context)



# def index():
#
#     os.chdir(local_repo_path)
#     process_result = subprocess.run(["git", "log", "-10"], stdout = subprocess.PIPE, stderr = subprocess.STDOUT);
#
#     git_log = "<h2>git log:</h2>\n{}".format(process_result.stdout.decode());
#
#     return render_text(git_log);

# @app.route("/deploy", methods = ["POST"])
# def deploy():
#
#     deploy_stand = request.values["deploy_stand"];
#     deploy_branch = request.values["deploy_branch"];
#     deploy_path = deploy_paths[deploy_stand];
#
#     deploy_blocker_path = "{}/block.dpl".format(local_log_path);
#
#     if os.path.exists(deploy_blocker_path):
#         deploy_logger.writeDown("Deploy in progress, try later.");
#         return render_text("Deploy in progress, try again 5 minutes later.")
#
#     with open(deploy_blocker_path, "a") as deploy_blocker:
#         deploy_blocker.write("\n");
#
#     deploy_logger.writeDown("Deploy branch: {}".format(deploy_branch));
#     deploy_logger.writeDown("Deploy path: {}".format(deploy_path));
#
#     stdout_text = "Deploy branch: {}\nDeploy path: {}\n\n".format(deploy_branch, deploy_path);
#
#     deploy_steps[0]["call"][2] = deploy_path;
#     deploy_steps[1]["call"][1] = deploy_path;
#     deploy_steps[3]["call"][2] = deploy_branch;
#     deploy_steps[5]["call"][3] = deploy_path;
#     deploy_steps[6]["dir"] = deploy_path;
#     # deploy_steps are defined in config.py
#
#     deploy_logger.writeDown("Proceeding...");
#
#     for info_step in info_steps:
#
#         if info_step["dir"] != None:
#             os.chdir(info_step["dir"]);
#
#         process_result = subprocess.run(info_step["call"], stdout = subprocess.PIPE, stderr = subprocess.STDOUT);
#         op_stdout = process_result.stdout.decode();
#         output_text = "\n{} \n\n{}".format(info_step["name"], op_stdout);
#         deploy_logger.writeDown(output_text);
#         stdout_text += output_text;
#         with open(deploy_blocker_path, "a") as deploy_blocker:
#             deploy_blocker.write(output_text);
#
#     for deploy_step in deploy_steps:
#
#         if deploy_step["dir"] != None:
#             os.chdir(deploy_step["dir"]);
#
#         process_result = subprocess.run(deploy_step["call"], stdout = subprocess.PIPE, stderr = subprocess.STDOUT);
#
#         op_stdout = process_result.stdout.decode();
#         output_text = "{} \n{}".format(deploy_step["name"], op_stdout);
#
#         deploy_logger.writeDown(output_text);
#         with open(deploy_blocker_path, "a") as deploy_blocker:
#             deploy_blocker.write(output_text);
#         stdout_text += output_text;
#
#
#     stdout_text += "\nDone.";
#     deploy_logger.writeDown("Done.");
#
#     os.remove(deploy_blocker_path);
#
#     return render_text(stdout_text);


def main():
    app.run(debug = False, host="0.0.0.0", port = "5100")

if __name__ == "__main__":
    main()
