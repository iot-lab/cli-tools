Resources list
==============

Resources list selects and configures resources for the experiment.
The argument can be specified multiple times.

    --list <resources_selection>,<resources_configuration>

Example:

    --list grenoble,m3,1-2,firmware=tutorial_m3.elf


Resources selection
-------------------

Resources selection has two modes (a submit should only contain one mode):

 - 'physical' where you explicitely specify nodes numbers
 - 'alias' where nodes are selected from available nodes

    <physical_selection|alias_selection>

### Physical selection ###

    <site>,<short_archi>,<id_list>

    grenoble,m3,1-10+31-40 : grenoble m3 nodes 1..10 and 31..40
    saclay,samr21,1+2+3    : saclay samr21 nodes 1..3

### Alias selection ###

    <num>,<properties>

    Properties is a '+' separated list of 'key=value'
    properties == 'site=<site>+archi=<full_archi>[+mobile=0|1]' in any order

    1,site=grenoble+archi=m3:at86rf231+mobile=1 : one mobile m3 in Grenoble
    2,archi=samr21:at86rf233+site=saclay : two custom samr21 in saclay


Resources configuration
-----------------------

Resources configuration sets configuration for given nodes which includes:

* firmware
* profile
* mobility
* ... (maybe another one non documented here)

Format:

    <,assocname=assocvalue><,assocname=assovalue>

    firmware=test.elf,profile=consumption
    mobility=JHall,profile=sniffer


Firmware and profile can also be specified by position, empty means no value.

    <,firmwarepath><,profilename><,assocname=assovalue>

    The same examples as before by position

    test.elf,consumption
    ,sniffer,mobility=JHall : nothing before the first ',' to set 'no firmware'
