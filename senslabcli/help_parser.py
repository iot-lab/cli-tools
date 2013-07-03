from textwrap import dedent

AUTH_PARSER = dedent("""

    auth-cli command-line store your credentials.
    It creates a file .senslabrc in your home directory with username and password
    options.

    """)

NODE_PARSER = dedent("""

    node-cli command-line manage interaction on sensor nodes. You can launch commands on your
    sensor nodes experiment.

   """)

EXPERIMENT_PARSER = dedent("""

    experiment-cli command-line manage experiments on testbed.

   """)

PROFILE_PARSER = dedent("""

    profile-cli command-line manage profiles experimentation : store you favourite sensor nodes configuration
    with combination of a power supply mode and an automatic measure configuration (e.g. polling).

   """)


PARSER_EPILOG = dedent("""\

       Authentication :
           * username without any password option : use username option with password prompt
               $ %(cli)s-cli -u login %(option)s ...
           * username and password option : use credentials options
               $ %(cli)s-cli -u login -p password  %(option)s ...
           * without username nor password options : try to use credentials file (e.g. auth-cli command-line) or anonymous request
               $ %(cli)s-cli %(option)s ...
    """)

SUBMIT_EPILOG = dedent("""\

        Examples:
            * physical experiment list : site_name,nodeid_list,firmware_path,profile_name
                $ experiment-cli submit -d 20 -a grenoble,1-5+8+9-11,cc1101.hex,battery
                $ experiment-cli submit -d 20 -a grenoble,1-20,/home/cc1101.hex -a rennes,1-5,,battery
                $ experiment-cli submit -d 20 -a grenoble,1-20 

            * alias experiment list : number_nodes,properties,firmware_path,profile_name
                $ experiment-cli submit -d 20 -a 9,archi=wsn430:cc1101+site=grenoble,tp.hex,battery
                $ experiment-cli submit -d 20 -a 9,archi=wsn430:cc1101+site=grenoble,cc1101.hex -a 5,archi=wsn430:cc2420+site=rennes,cc2420.hex
    """)

LOAD_EPILOG = dedent("""\

        Examples:
            * load experiment : 
                $ experiment-cli load -f 192.json 
                Note : by default if you have firmware assocations we search firmware file(s) with relative path 
            * load experiment with firmware list and absolute path :
                $ experiment-cli load -f 192.json -l /home/cc2420.hex,/home/cc1101.hex
            * reload an experiment :
                $ experiment-cli get -i 192 -a
                $ tar -xzvf 192.tar.gz 
                $ cd 192
                $ experiment-cli load -f 192.json  
    """)

INFO_EPILOG = dedent("""\

        Examples:
            $ experiment-cli -r|-rs|-s
            $ experiment-cli info -e --state Running,Terminated --offset 10 --limit 20 

    """)            


ADD_EPILOG = dedent("""\
        Examples :
           $ profile-cli add -n profile -current -voltage -power -cfreq 5000
           $ profile-cli add -n profile -p battery -temperature

    """)


COMMAND_EPILOG = dedent("""\

        Examples:
            * all sensor nodes experiment
               $ node-cli --update /home/tp.hex
            * commmand list : site_name,nodeid_list
               $ node-cli --reset -a grenoble,1-34+72
            * command with several experiments with state Running
               $ node-cli -i <expid> --reset
    """)

