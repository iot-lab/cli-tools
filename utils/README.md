# Miscellaneous utilities for iotlab-cli-tools

## Bash-completion

The script `iotlab-cli-tools-bash-completion.sh` is available to complete the
`iotlab-*` commands.  It is compatible with the standard bash-completion
mechanism, as many commands are in [https://github.com/scop/bash-completion].
The scripts only needs to be sourced at runtime from command-line:

    source iotlab-cli-tools-bash-completion.sh

Then, bash is able to autocomplete the iotlab-* commands:

    iotlab-experiment submit --<press tab key here>


One also wants to install it on a whole system, to be automatically available
for all users:

    sudo install -m644 iotlab-cli-tools-bash-completion.sh /usr/share/bash-completion/completions/iotlab-experiment
    for command_name in iotlab-admin admin-cli  \
                        iotlab-auth auth-cli  \
                        experiment-cli  \
                        iotlab-node node-cli  \
                        iotlab-profile profile-cli  \
                        iotlab-robot robot-cli; do
        sudo ln -s iotlab-experiment "/usr/share/bash-completion/completions/$command_name"
    done

Cf. [https://github.com/scop/bash-completion] for more details.
