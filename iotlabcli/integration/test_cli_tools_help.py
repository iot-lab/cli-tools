import pytest

import subprocess
import shlex

TOOLS = {
  "auth-cli":
     "",
  "experiment-cli":
     "submit,stop,get,load,info,wait",
  "profile-cli":
     "addwsn430,addm3,adda8,addcustom,del,get,load",
  "node-cli":
     "",
  "robot-cli":
     "status,update,get",
}

@pytest.mark.parametrize("tool", TOOLS)
def test_cli_tools_no_args(tool):
    run(tool)

@pytest.mark.parametrize("tool", TOOLS)
def test_cli_tools_help(tool):
    run(tool+" -h")

@pytest.mark.parametrize("tool, cmd", [ (tool, cmd)
    for tool in TOOLS for cmd in TOOLS[tool].split(",") ])
def test_command_help(tool, cmd):
    run(tool+" "+cmd+" -h")


def run(cmd):
    cmd = shlex.split(cmd)
    ret = subprocess.check_output(cmd)
    return ret
