import argparse
import sys

import keen
from pymongo import MongoClient

import emailer


__author__ = "dkador"


def read_args(args=None):
    parser = argparse.ArgumentParser(description="Monitor mongo replication lag")

    parser.add_argument("--server", default="localhost",
                        help="Mongo host (default: localhost)")
    parser.add_argument("--port", type=int, default=27017,
                        help="Mongo port (default: 27017)")

    parser.add_argument("--maxlag", type=int, default="10",
                        help="Max lag (in seconds) allowed before warning")
    parser.add_argument("--email", type=str, required=True,
                        help="Email address to alert to")

    return parser.parse_args(args=args)


def handle_results(status, options):
    """
    status is a dictionary response from pymongo
    """

    members = status["members"]

    # first find primary
    primary = None
    for member in members:
        if member["state"] == 1:
            primary = member
            break

    if not primary:
        raise Exception("Couldn't find primary!")

    largest_lag = 0
    for member in members:
        if member["_id"] != primary["_id"] and member["stateStr"] not in ["ARBITER", "STARTUP2", "RECOVERY"]:
            member_optime = member["optimeDate"]
            primary_optime = primary["optimeDate"]
            lag = (primary_optime - member_optime).total_seconds()
            if lag > largest_lag:
                largest_lag = lag

    if largest_lag > options.maxlag:
        text = """Mongo replication lag is too high!

<b>Primary</b>: {primary}
<b>Primary optime</b>: {primary_optime}
<b>Largest repl lag</b>: {largest_lag} seconds

        """.format(primary=primary["name"],
                   primary_optime=primary["optimeDate"].isoformat(),
                   largest_lag=largest_lag)

        emailer.Emailer.send_email(addr_to=options.email, subject="Mongo behind alert",
                                   text=text, categories=["mongomon"])

    secondaries = {}

    for member in members:
        if member["stateStr"] == "ARBITER":
            continue

        member_name = member["name"].replace(".", "-")
        secondaries[member_name] = {
            "health": member["health"],
            "optime": member["optimeDate"].isoformat(),
            "lag": (primary["optimeDate"] - member["optimeDate"]).total_seconds(),
            "state": member["stateStr"],
            "uptime": member["uptime"]
        }

    keen.add_event("mongo_lag", {
        "largest_lag": largest_lag,
        "primary": {
            "name": primary["name"],
            "optime": primary["optimeDate"].isoformat()
        },
        "secondaries": secondaries
    })


def main(args=sys.argv):
    options = read_args(args=args)

    client = MongoClient(host=options.server, port=options.port, tz_aware=True)

    try:
        status = client.admin.command("replSetGetStatus")
    except Exception, e:
        print "Failed to process: %s" % str(e)
        return 1

    handle_results(status, options)


if __name__ == "__main__":
    sys.exit(main())