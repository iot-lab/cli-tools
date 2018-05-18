# Miscellaneous utilities for iotlab-cli-tools

## Bash-completion

The script `iotlabcli-bash-completion.sh` is available to complete the
`iotlab-*` commands.  It is compatible with the standard bash-completion
mechanism, as many commands are in https://github.com/scop/bash-completion.
The scripts only needs to be sourced at runtime from command-line:

    source iotlabcli-bash-completion.sh

Then, bash is able to autocomplete the iotlab-* commands:

    iotlab-experiment submit --<press tab key here>

One also wants to install it on a whole system, to be automatically available
for all users:

    export BASH_COMPLETION_DIR=/usr/share/bash-completion/completions
    sudo install -m644 iotlabcli-bash-completion.sh $BASH_COMPLETION_DIR/iotlab-experiment
    for command_name in iotlab-admin iotlab-auth iotlab-node iotlab-profile iotlab-robot; do
        sudo ln -s $BASH_COMPLETION_DIR/iotlab-experiment $BASH_COMPLETION_DIR/$command_name
    done

Cf. https://github.com/scop/bash-completion for more details.
