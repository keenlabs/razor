import argparse
import os
import sys

import keen

import emailer


__author__ = "dkador"


def read_args(args=None):
    parser = argparse.ArgumentParser(description="Monitor whether or not a process is running")

    parser.add_argument("--process", type=str, required=True,
                        help="The name of the process (i.e. what you grep for)")
    parser.add_argument("--hosts", type=str, required=True,
                        help="The hosts to SSH into to check for the process")
    parser.add_argument("--user", default="",
                        help="The user to use with SSH")
    parser.add_argument("--email", type=str, required=True,
                        help="Email address to alert to")

    return parser.parse_args(args=args)


def handle_results(results, options):
    """
    results is a dict that maps from hostname to whether that host had the proc running
    """

    found_proc_on_all_hosts = True
    missing_hosts = []
    for (host, found_proc) in results.iteritems():
        if not found_proc:
            found_proc_on_all_hosts = False
            missing_hosts.append(host)

    if not found_proc_on_all_hosts:
        # we didn't find the proc, alert
        text = "Can't find process {} on the following hosts:\n\n".format(options.process)
        missing_hosts = sorted(missing_hosts)
        for host in missing_hosts:
            text += host + "\n"
        emailer.Emailer.send_email(addr_to=options.email, subject="Can't find process {}".format(options.process),
                                   text=text, categories=["processmon"])

    keen.add_event("processmon", {
        "process": options.process,
        "missing_hosts": missing_hosts,
        "found_on_all_hosts": found_proc_on_all_hosts
    })


def main(args=sys.argv):
    options = read_args(args=args)
    hosts = options.hosts.split(",")

    results = {}

    ssh_command = "ssh "
    if options.user:
        ssh_command += options.user + "@"

    for host in hosts:
        full_command = """{}{} ps guax | grep {} | grep -v "grep" """.format(ssh_command, host, options.process)
        result = os.popen(full_command).read()
        if result:
            found_proc = True
        else:
            found_proc = False
        results[host] = found_proc

    handle_results(results, options)


if __name__ == "__main__":
    sys.exit(main())