import argparse
import sys

import keen
from stormkafkamon.processor import process, ProcessorError
from stormkafkamon.zkclient import ZkClient, ZkError

from keenrazor import emailer


__author__ = "dkador"


def read_args(args=None):
    parser = argparse.ArgumentParser(description="Monitor kafka and report, yo!")

    parser.add_argument("--zserver", default="localhost",
                        help="Zookeeper host (default: localhost)")
    parser.add_argument("--zport", type=int, default=2181,
                        help="Zookeeper port (default: 2181)")
    parser.add_argument("--topology", type=str, required=True,
                        help="Storm Topology")
    parser.add_argument("--spoutroot", type=str, required=True,
                        help="Root path for Kafka Spout data in Zookeeper")

    parser.add_argument("--maxdelta", type=int, default="10000",
                        help="Max delta allowed before warning")

    return parser.parse_args(args=args)


def handle_results(summary, options):
    """
    summary is of type PartitionsSummary
    """

    print summary

    if summary.total_delta > options.maxdelta:
        emailer.Emailer.send_email(addr_to="dan@keen.io", subject="Kafka is behind",
                                   text="Oh no kafka is teh shits")

    partitions = {}

    for p in summary.partitions:
        broker_name = p.broker.replace(".", ":")
        name = "{topic}-{broker}-{partition}".format(topic=p.topic,
                                                     broker=broker_name,
                                                     partition=p.partition)
        partitions[name] = {
            "earliest": p.earliest,
            "latest": p.latest,
            "depth": p.depth,
            "spout": p.spout,
            "current": p.current,
            "delta": p.delta
        }

    keen.add_event("kafka_depth-{}".format(options.topology), {
        "total_depth": summary.total_depth,
        "total_delta": summary.total_delta,
        "num_partitions": summary.num_partitions,
        "num_brokers": summary.num_brokers,
        "partitions": partitions
    })


def main(args=sys.argv):
    options = read_args(args=args)

    zc = ZkClient(options.zserver, options.zport)

    try:
        summary = process(zc.spouts(options.spoutroot, options.topology))
    except ZkError, e:
        print "Failed to access Zookeeper: %s" % str(e)
        return 1
    except ProcessorError, e:
        print "Failed to process: %s" % str(e)
        return 1
    else:
        handle_results(summary, options)


if __name__ == "__main__":
    sys.exit(main())