Keen Razor

Because razors cut to the quick and that's what we want with monitoring or something.

Usage

Get this bad boy installed to your local environment. You'll probably want to set up a virtualenv but that's up to you.

Then run this. There's one required argument and one optional argument.

Required: run.config

This is a config file in YAML that defines what monitoring job to run. Here's an example file:

```
name: kafkamon
topology: write-event
spoutroot: keen_storm_write_event_dev
maxdelta: 10000000
```

Optional: lib.config

This is a config file in YAML that defines settings like keen and sendgrid credentials. Here's an example file:

```
sendgrid:
    username: my_sendgrid_name
    password: a_thing
keen:
    project_id: project_id_here
    write_key: write_key_here
    read_key: read_key_here
```

That's it. Look at individual jobs to discover what parameters they support for their YAML files. We run this on
various servers by setting up cron jobs.