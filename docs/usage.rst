=====
Usage
=====

To begin, create a new directory and environment::

    $ mkdir rte
    $ cd rte
    $ python3 -m venv ./
    $ pip install routeros_telegraf_exporter
    $ curl https://raw.githubusercontent.com/kepsic/routeros_telegraf_exporter/master/example_config.ini -o config.ini
    $ curl https://raw.githubusercontent.com/kepsic/routeros_telegraf_exporter/master/hosts_config_example.yaml -o hosts_config.yaml

To use RouterOS Telegraf metrics exporter you have following options:

- Web service
    Update replace routers from hosts_config.yaml with your router names

    Execute::

    $ export ROUTEROS_EXPORTER_PATH=$(pwd);
    $ export ROUTEROS_API_USERNAME=api_read_user;
    $ export ROUTEROS_API_PASSWORD=mysecretapiuserpassword
    $ pserve config.ini

    influx.conf for web service::

        [[inputs.http]]
        ## One or more URLs from which to read formatted metrics
        urls = [
            "http://localhost:6544/metrics"
        ]
        data_format = "influx"
        interval = "60s"
        timeout="30s"
- Run in daemon mode

    Execute::

    $ export ROUTEROS_EXPORTER_PATH=$(pwd);
    $ export ROUTEROS_API_USERNAME=api_read_user;
    $ export ROUTEROS_API_PASSWORD=mysecretapiuserpassword
    $ rte --hosts-config-file hosts_config.yaml -D --logfile /var/mymetrics.out

    influx.conf for daemon mode::

        # Stream a log file, like the tail -f command
        [[inputs.tail]]
        ## files to tail.
        ## These accept standard unix glob matching rules, but with the addition of
        ## ** as a "super asterisk". ie:
        ##   "/var/log/**.log"  -> recursively find all .log files in /var/log
        ##   "/var/log/*/*.log" -> find all .log files with a parent dir in /var/log
        ##   "/var/log/apache.log" -> just tail the apache log file
        ##
        ## See https://github.com/gobwas/glob for more examples
        ##
        files = ["/var/mymetrics.out"]
        ## Read file from beginning.
        from_beginning = false
        ## Whether file is a named pipe
        pipe = false

        ## Method used to watch for file updates.  Can be either "inotify" or "poll".
        # watch_method = "inotify"

        ## Data format to consume.
        ## Each data format has its own unique set of configuration options, read
        ## more about them here:
        ## https://github.com/influxdata/telegraf/blob/master/docs/DATA_FORMATS_INPUT.md
        data_format = "influx"

- Run in interactive mode

    Execute::

    $ export ROUTEROS_EXPORTER_PATH=$(pwd);
    $ export ROUTEROS_API_USERNAME=api_read_user;
    $ export ROUTEROS_API_PASSWORD=mysecretapiuserpassword
    $ rte --hosts-config-file hosts_config.yaml -i

    influx.conf for interactive mode::

        [[inputs.exec]]
        ## Commands array
        commands = [
            "rte --hosts-config-file hosts_config.yaml -i",
         ]

         ## Timeout for each command to complete.
         timeout = "5s"

         ## measurement name suffix (for separating different commands)
         name_suffix = "_mycollector"

         ## Data format to consume.
         ## Each data format has its own unique set of configuration options, read
         ## more about them here:
         ## https://github.com/influxdata/telegraf/blob/master/docs/DATA_FORMATS_INPUT.md
         data_format = "influx"

- Probe from router metric values

    To find out what metrics to measure you can probe all available metrics from measure::

    $ export ROUTEROS_EXPORTER_PATH=$(pwd);
    $ export ROUTEROS_API_USERNAME=api_read_user;
    $ export ROUTEROS_API_PASSWORD=mysecretapiuserpassword
    $ rte_probe --host router1.example.com --path /system/resource
