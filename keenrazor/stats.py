import logging
from statsd import statsd

__author__ = 'cwatson'

class Stats(object):

    dd_tag_string = "{key}:{value}"
    dd_metric_string = "razor.{scope}.{stat}"

    def __init__(self, scope):
        self.scope = scope

    def emit(self, stat_name, tags, value):
        # Convert the dictionary of tags into an array of strings separated by a colon
        string_tags = map(lambda (k, v): (self.dd_tag_string.format(key=k, value=v)), tags.iteritems())
        statsd.gauge(self.dd_metric_string.format(
            scope=self.scope,
            stat=stat_name,
            tags=string_tags
        ), value)
