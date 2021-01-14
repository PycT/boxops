#! python3
import argparse
import yaml
import os
import engine
from rhythmic import Logger  # to exclude this dependency search through for Logger() and .writeDown()


def cli_parser_setup(cli_parser):

    cli_parser.add_argument("-t", help="test drills configurations", action="store_true")

    return True


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
    drills = []
    webdrills = []
    cwd = os.getcwd()

    drills_path = "{}/{}".format(cwd, boxops_configuration["drills_directory"])
    webdrills_path = "{}/{}".format(cwd, boxops_configuration["web_ui_triggered_drills_directory"])

    drills_folder_list = os.listdir(drills_path)
    for item in drills_folder_list:
        if os.path.isfile(drills_path+"/"+item):
            drills.append(drills_path+"/"+item)

    webdrills_folder_list = os.listdir(webdrills_path)
    for item in webdrills_folder_list:
        if os.path.isfile(webdrills_path+"/"+item):
            webdrills.append(webdrills_path+"/"+item)

    return drills, webdrills


def process_drills(drills_list, test_only=False):
    run_drills = not test_only

    process_output = ""

    for the_drill_file in drills_list:
        print()
        print("============ {} ============".format(the_drill_file))
        process_output += "============ {} ============\n".format(the_drill_file)
        print("============ Testing configuration =============")
        process_output += "============ Testing configuration =============\n\n"
        the_drill = engine.load_yaml(the_drill_file)
        if engine.test_the_drill(the_drill) and run_drills:
            print()
            print("============ Executing the drill =============")
            the_drill_output = engine.execute_the_drill(the_drill)
            process_output += the_drill_output
        else:
            process_output += "A drill from {} was not executed".format(the_drill_file)

    return process_output


def main():
    cli_parser = argparse.ArgumentParser()
    cli_parser_setup(cli_parser)
    cli_args = cli_parser.parse_args()
    boxops_configuration = get_boxops_configuration()
    all_the_drills = collect_drills(boxops_configuration)

    log_path = os.getcwd() + "/log"
    boxops_logger = Logger(log_filename_postfix="boxops", path_to_log=log_path)

    if cli_args.t:
        process_drills(all_the_drills[0], True)
        process_drills(all_the_drills[1], True)
    else:
        process_output = process_drills(all_the_drills[0], False)
        boxops_logger.writeDown(process_output)

if __name__ == "__main__":
    main()