import sys
import argparse
import keen
import yaml
import emailer
import kafkamon
import processmon
import mongomon
import open_drpc_conn_mon

__author__ = 'dkador'


def read_args():
    parser = argparse.ArgumentParser(description="Keen razor - monitor a thing?")

    parser.add_argument("--run-config", type=str, required=True,
                        help="Path to a config file for this run")
    parser.add_argument("--lib-config", type=str, default="",
                        help="Path to a config file with lib settings for this run")

    return parser.parse_args()


def load_yaml(filename):
    with open(filename) as f:
        return yaml.load(f)


def apply_lib_configs(lib_config):
    if "sendgrid" in lib_config:
        emailer.Emailer.username = lib_config["sendgrid"]["username"]
        emailer.Emailer.password = lib_config["sendgrid"]["password"]

    if "keen" in lib_config:
        keen.project_id = lib_config["keen"]["project_id"]
        keen.write_key = lib_config["keen"]["write_key"]
        keen.read_key = lib_config["keen"]["read_key"]


def run(run_config):
    def inject_args_into_config():
        # inject config into args
        args = []
        for (key, value) in run_config.iteritems():
            if key == "name":
                continue

            args.append("--{}".format(key))
            args.append(str(value))
        return args

    args = inject_args_into_config()

    if run_config["name"] == "kafkamon":
        return kafkamon.main(args=args)
    elif run_config["name"] == "mongomon":
        return mongomon.main(args=args)
    elif run_config["name"] == "processmon":
        return processmon.main(args=args)
    elif run_config["name"] == "open_drpc_conn_mon":
        return open_drpc_conn_mon.main(args=args)

    else:
        raise Exception("I don't know how to run '{}'.".format(run_config["name"]))


def main():
    options = read_args()

    run_config = load_yaml(options.run_config)
    lib_config = {}
    if options.lib_config:
        lib_config = load_yaml(options.lib_config)

    apply_lib_configs(lib_config)

    return run(run_config)


if __name__ == "__main__":
    sys.exit(main())
