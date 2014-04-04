import argparse
import os
import sys

import keen

import emailer


__author__ = "dkador"


def read_args(args=None):
    parser = argparse.ArgumentParser(description="Monitor the # of open connections on DRPC servers")

    parser.add_argument("--hosts", type=str, required=True,
                        help="The hosts to SSH into to check for open conns")
    parser.add_argument("--maxconns", type=int, required=True,
                        help="Maximum connections allowed before warning")
    parser.add_argument("--user", default="",
                        help="The user to use with SSH")
    parser.add_argument("--email", type=str, required=True,
                        help="Email address to alert to")

    return parser.parse_args(args=args)


def handle_results(results, options):
    """
    results is a dict that maps from hostname to the # of open conns on that host
    """

    all_under_limit = True
    over_limit_hosts = []
    for (host, num_conns) in results.iteritems():
        if num_conns > options.maxconns:
            all_under_limit = False
            over_limit_hosts.append((host, num_conns))

    if not all_under_limit:
        # one of the hosts was over, alert
        text = "DRPC server's open connections over threshold on the following hosts:\n\n"
        over_limit_hosts = sorted(over_limit_hosts)
        for host in over_limit_hosts:
            text += "{}: {}\n".format(host, results[host])
        emailer.Emailer.send_email(addr_to=options.email, subject="DRPC Server Open Conns Too High",
                                   text=text, categories=["open_drpc_conn_mon"])

    keen.add_event("open_drpc_conn_mon", {
        "maxconns": options.maxconns,
        "over_limit_hosts": over_limit_hosts,
        "all_under_limit": all_under_limit,
        "results": results
    })


def main(args=sys.argv):
    options = read_args(args=args)
    hosts = options.hosts.split(",")

    results = {}

    ssh_command = "ssh "
    if options.user:
        ssh_command += options.user + "@"

    for host in hosts:
        full_command = """{}{} sudo netstat -tpe | grep 3772 | wc -l""".format(ssh_command, host)
        result = os.popen(full_command).read()
        num_conns = int(result)
        results[host] = num_conns

    handle_results(results, options)


if __name__ == "__main__":
    sys.exit(main())