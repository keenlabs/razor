import argparse
import os
import socket
import sys

import keen

import emailer


__author__ = "dkador"


def read_args(args=None):
    parser = argparse.ArgumentParser(description="Monitor whether or not a process is running")

    parser.add_argument("--process", type=str, required=True,
                        help="The name of the process (i.e. what you grep for)")
    parser.add_argument("--email", type=str, required=True,
                        help="Email address to alert to")

    return parser.parse_args(args=args)


def handle_results(result, options):
    """
    result is a string that represents the output of the grepped `ps` command
    """

    found_proc = False
    if result:
        # we found the proc
        found_proc = True
        print "Found proc"
    else:
        # we didn't find the proc, alert
        text = """Can't find process {} on host {}""".format(options.process, socket.gethostname())
        emailer.Emailer.send_email(addr_to=options.email, subject=text,
                                   text=text, categories=["processmon"])

    keen.add_event("processmon", {
        "process": options.process,
        "host": socket.gethostname(),
        "found_proc": found_proc
    })


def main(args=sys.argv):
    options = read_args(args=args)

    result = os.popen("""ps guax | grep {} | grep -v "grep" """.format(options.process)).read()
    handle_results(result, options)


if __name__ == "__main__":
    sys.exit(main())