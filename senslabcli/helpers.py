import getpass
import argparse
import re,os
import base64
import json

DOMAIN_DNS = 'senslab.info'

def password_prompt():
    """ password prompt when command-line option username (e.g. -u or --user) is used without password 

    :returns password
    """
    pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))
    p1, p2 = pprompt()
    while p1 != p2:
       print('Passwords do not match. Try again')
       p1, p2 = pprompt()
    return p1 

def create_password_file(username, password, parser):
    """ Create a password file for basic authentication http when command-line option username and password are used
    We write .senslab file in user home directory with format username:base64(password)

    :param username: basic http auth username
    :type username: string
    :param password: basic http auth password
    :type password: string
    :param parser: command-line parser
    """
    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME') 
    try:
       password_file = open('%s/%s' % (home_directory,'.senslabrc'),'wb')
    except(IOError), e:
       parser.error("Unable to create password file in your home directory : %s." % home_directory)
    password_file.write('%s:%s' % (username,base64.b64encode(password)))
    password_file.close()

def read_password_file(parser):
    """ Try to read password file (.senslab) in user home directory when command-line option 
    username and password are not used. If password file exist whe return username and password
    for basic auth http authentication

    :param parser: command-line parser
    """

    home_directory = os.getenv('USERPROFILE') or os.getenv('HOME')
    path_file = '%s/%s' % (home_directory,'.senslabrc')
    if (os.path.exists(path_file)):
        try:
           password_file = open(path_file,'r')
           field = (password_file.readline()).split(':')
           if (not len(field) == 2):
              parser.error("Bad password file format in your home directory : %s." % home_directory)
           password_file.close()
           return field[0], base64.b64decode(field[1])
        except(IOError), e:
           parser.error("Unable to open password file in your home directory : %s." % home_directory)
    else:
       return None,None

def open_json_file(path_file, parser):
    try:
       json_file = open(path_file,'r')
       json_file_name = os.path.basename(json_file.name)
       json_file_data = json_file.read()
       json_file.close()
       return json_file_name, json_file_data
    except(IOError), e:
       parser.error("Unable to open JSON description file : %s." % path_file)

def read_json_file(json_file_name,json_file_data, parser):
    try:
       json_data = json.loads(json_file_data)
       return json_data
    except (ValueError), e:
       parser.error("Unable to read JSON description file : %s." % json_file_name)

def write_experiment_archive(experiment_id, data, parser):
    try:
       archive_file = open('%s.tar.gz' % experiment_id,'wb')
    except(IOError), e:
       parser.error("Unable to save experiment archive file : %s.tar.gz." % experiment_id)
    archive_file.write(data)
    archive_file.close()

def get_user_credentials(username, password, parser):
    if ((password is None) and (username is not None)):
       password = getpass.getpass()       
    elif ((password is not None) and (username is not None)):
       pass
    else:
       username,password = read_password_file(parser)
    return username, password

def check_experiment_state(state, parser):
    oar_state = 'Terminated,Hold,Waiting,toLaunch,toError,toAckReservation,Launching,Finishing,Running,Suspended,Resuming,Error' 
    if (state is not None):
       experiment_state = state.split(',')
       list_oar_state = oar_state.split(',')
       for exp_st in experiment_state:
          state_exist = False
          for oar_st in list_oar_state:
              if (exp_st==oar_st):
                 state_exist=True
          if (not state_exist):
              parser.error('The experiment filter state %s is not valid.' % state) 
       return state
    else:
       return oar_state

def check_site(site_name, sites_json, parser):
    site_exist = False
    for site in sites_json["items"]:
        if (site["site"]==site_name):
           site_exist=True
    if (not site_exist):
       parser.error('The site name %s doesn\'t exist.' % site_name)
    return site_name

def check_experiments_running(experiments_json, parser):
    items = experiments_json["items"]
    if (len(items) == 0):
       parser.error("You don't have an experiment with state Running")
    experiments_id = []
    for exp in items:
       experiments_id.append(exp["id"])
    if (len(experiments_id)>1):
       parser.error("You have several experiments with state Running. Use option -i|--id and choose experiment id in this list : %s" 
          % experiments_id)
    else:
       return experiments_id[0]       

def check_command_list(nodes_list, parser):
   param_list = nodes_list.split(',')
   if (not len(param_list) == 2):
      parser.error('The number of argument in nodes list %s is not valid.' % nodes_list)
   else:
      return param_list

def check_experiment_list(exp_list, parser):
    param_list = exp_list.split(',')
    if (len(param_list)<2 or len(param_list)>4):
       parser.error('The number of argument in experiment list %s is not valid.' % exp_list)
    else:
       try:
         # try to find if first parameter is nb_nodes
         int(param_list[0])
       except ValueError:
         experiment_type = 'physical'
       else:
         experiment_type = 'alias'
       finally:
         return experiment_type, param_list

def check_nodes_list(site, nodes_list, parser):
    pattern_digit =r'[^\0-9]'
    physical_nodes = []
    for nodes in nodes_list.split('+'):
        node = nodes.split('-')
        if ((len(node)==1 and re.search(pattern_digit,node[0])) or len(node)>2):
          parser.error('You must specify a valid list node in experiment list %s ([0-9+-]).' % nodes_list)
        elif (len(node)==2):
          first=node[0]
          last=node[1]
          if (re.search(pattern_digit,first) or re.search(pattern_digit,last) or int(last) <= int(first)):
             parser.error('You must specify a valid list node in experiment list %s ([0-9+-]).' % nodes_list)
          else:
             for node_id in range(int(first),int(last)+1):
                physical_node = "node%s.%s.%s" % (node_id,site,DOMAIN_DNS)
                physical_nodes.append(physical_node) 
        else:
          physical_node = "node%s.%s.%s" % (node[0],site,DOMAIN_DNS)
          physical_nodes.append(physical_node)
    return physical_nodes


def check_properties(properties_list, sites_json, parser):
    properties = properties_list.split('+')
    if (len(properties)>3): parser.error('You must specify a valid list with \"archi\", \"site\" and \"mobile\" properties : %s.' % properties_list)
    archi = filter(lambda prop: prop.startswith('archi='), properties)
    site = filter(lambda prop: prop.startswith('site='), properties)
    mobile = filter(lambda prop: prop.startswith('mobile='), properties)
    if (len(archi)==0 or len(site)==0):
       parser.error('Properties \"archi\" and \"site\" are mandatory : %s.' % properties_list)
    site_prop = (site[0].split('='))[1]
    check_site(site_prop, sites_json, parser) 
    properties_dict = {}
    properties_dict['site']=site_prop
    archi_prop = (archi[0].split('='))[1]
    properties_dict['archi']=archi_prop
    if (len(mobile)==0):
       properties_dict['mobile']='0' 
    else:
       mobile_prop=(mobile[0].split('='))[1]
       properties_dict['mobile']=mobile_prop
    return properties_dict

def check_command_firmware(firmware_path, parser):
    try:
        firmware_file = open(firmware_path,'r')
    except(IOError), e:
        parser.error("Unable to open command firmware file : %s." % firmware_path)
    else:
        firmware_name = os.path.basename(firmware_file.name)
        firmware_body = firmware_file.read()
        firmware_file.close()
    return firmware_name,firmware_body

def check_experiment_firmwares(firmware_path, firmwares, parser):
    try:
        firmware_file = open(firmware_path,'r') 
    except(IOError), e:
        parser.error("Unable to open experiment firmware file : %s." % firmware_path)
    else:
        firmware_name = os.path.basename(firmware_file.name)
        firmware_body = firmware_file.read()
        firmware_file.close()
        if (firmwares.has_key(firmware_name)):
           if (firmwares[firmware_name] != firmware_path):
              parser.error('A firmware with the same name %s and different path is already present.' % firmware_path)
        else:
           firmwares[firmware_name] = firmware_path
        return firmware_name,firmware_body,firmwares

