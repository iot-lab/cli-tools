JMESPATH and FORMAT Examples
============================


Examples on how to query values and format cli-tools output.


Examples from iot-lab bash scripts
----------------------------------

### Get Grenoble M3 alive nodes ###

    iotlab-experiment --jmespath 'items[?site==`grenoble`]|[0].archis[?archi==`m3:at86rf231`]|[0].states[?state==`Alive`]|[0].ids' --format='str' info -li
    1-16+18+20-43+45-49+51-154+156-164+166-186+188-242+244-261+263-289+346+359-363+365-380


### New line seperated nodes list ###

    iotlab-experiment --jp='items[].network_address' --fmt='"\n".join'  get -r
    a8-6.grenoble.iot-lab.info
    a8-5.grenoble.iot-lab.info
    a8-9.grenoble.iot-lab.info
    a8-7.grenoble.iot-lab.info
    a8-8.grenoble.iot-lab.info


### New line seperated open nodes list ###

    iotlab-experiment --jp='items[].network_address' --fmt='lambda x: "\n".join(["node-"+n for n in x])'  get -r
    node-a8-6.grenoble.iot-lab.info
    node-a8-5.grenoble.iot-lab.info
    node-a8-9.grenoble.iot-lab.info
    node-a8-7.grenoble.iot-lab.info
    node-a8-8.grenoble.iot-lab.info


### Successfully deployed nodes ###

    iotlab-experiment --jp='deploymentresults."0"' --fmt='" ".join' get -p
    a8-5.grenoble.iot-lab.info a8-6.grenoble.iot-lab.info a8-7.grenoble.iot-lab.info a8-8.grenoble.iot-lab.info a8-9.grenoble.iot-lab.info


### Get experiment state ###

    iotlab-experiment --jp=state --fmt=str get -i 29251 -s
    Running


Get nodes list per architecture
-------------------------------

### List all 'samr21' archi nodes ###

    iotlab-experiment --jmespath="items[?starts_with(@.archi, 'samr21:')]" info -l
    [
        {
            "archi": "samr21:at86rf233",
            "mobile": 0,
            "network_address": "samr21-1.saclay.iot-lab.info",
            ...
        }
    ]


### List all saclay 'samr21' network addresses ###

    iotlab-experiment --jmespath="items[?contains(@.archi, 'samr21')].network_address" info  -l
    [
        "samr21-1.saclay.iot-lab.info",
        ...
        "samr21-8.saclay.iot-lab.info"
    ]


### List nodes by exact archi ###

    iotlab-experiment --jmespath="items[?archi=='samr21:at86rf233'].network_address" info -l
    [
        {
            "archi": "samr21:at86rf233",
            "mobile": 0,
            "network_address": "samr21-1.saclay.iot-lab.info",
            ...
        }
    ]


RIOT Makefile
-------------

Get current experiment ID
-------------------------

Get first one if multiple

    iotlab-experiment --jp 'items[].id|[0]' get -l --state Running
    29251

    # Bash version
    iotlab-experiment get -l --state Running | grep -m 1 '"id"' | grep -Eo '[[:digit:]]+'
    29251



### Get first node of list ###

Maybe use the first with "deploymentresults" == 0 here instead.

    iotlab-experiment --jp='items[0].network_address' --fmt=str get --resources
    a8-6.grenoble.iot-lab.info

    # Bash version
    iotlab-experiment get  --resources | grep -m 1 "network_address"  | sed 's/.*: "\(.*\)".*/\1/'
    a8-6.grenoble.iot-lab.info

