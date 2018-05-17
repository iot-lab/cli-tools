# iotlab-* completion

_iotlab_sites=(euratech strasbourg paris grenoble rennes lille saclay lyon)
_iotlab_archis=(wsn430 a8 m3 firefly arduino-zero samr21 st-lrwan1)
_iotlab_states=(Waiting toLaunch Launching Running Finishing Terminated Error)

_iotlab_site_scripts() {
    # TODO: complete `iotlab-experiment submit -s <tab>` and iotlab-experiment script --run <tab>`
    COMPREPLY=()
}

_iotlab_resources_list() {
    # TODO: complete `iotlab-experiment submit -l <tab>`
    COMPREPLY=()
}

_iotlab_experiment_id() {
    # TODO: complete e.g. `iotlab-experiment reload -i <tab>`
    # Warning: we should use the IoT-lab API, but this might be slow…
    COMPREPLY=()
}

_iotlab_profile() {
    # TODO: complete e.g. `iotlab-node -l grenoble,m3,64 --profile <tab>`
    # Warning: we should use the IoT-lab API, but this might be slow…
    COMPREPLY=()
}

_iotlab_experiment() {
    local cur prev words cword
    _init_completion || return

    case $prev in
        -v|--version|-h|--help)
            return 0
            ;;
        -u|--user|-p|--password)
            return 0
            ;;
    esac

    # Look for the command name
    local subcword cmd
    for (( subcword=1; subcword < ${#words[@]}-1; subcword++ )); do
        [[ ${words[subcword]} != -* && \
            ! ${words[subcword-1]} =~ -+(jmespath|jp|format|fmt|u(ser)?|p(assword)) ]] && \
                { cmd=${words[subcword]}; break; }
    done

    if [[ -z $cmd ]]; then
        case $cur in
            -*)
                # No command name, complete with generic flags
                COMPREPLY=($(compgen -W "-v --version -h --help -u --user -p --password --jmespath --jp --format --fmt" -- "$cur" ))
                return 0
                ;;
            *)
                # Complete with a command name
                COMPREPLY=($(compgen -W 'submit script stop get load reload info wait' -- "$cur"))
                return 0
                ;;
        esac
    fi

    # Complete command arguments
    case $cmd in
        submit)
            case "$prev" in
                -n|--name|-d|--duration|-r|--reservation)
                    # We don't need to complete there
                    ;;
                -l|--list)
                    _iotlab_resources_list
                    ;;
                -s|--site-association)
                    _iotlab_site_scripts
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help -p --print -n --name -d --duration -r --reservation -l --list -s --site-association --help-list --help-site-association' -- "$cur" ))
            esac
            ;;
        script)
            case "$prev" in
                -i|--id)
                    _iotlab_experiment_id
                    ;;
                --run)
                    _iotlab_site_scripts
                    ;;
                --kill|--status)
                    # TODO: this works for the first site, not for the following ones
                    COMPREPLY=($(compgen -W "${_iotlab_sites[*]}" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help -i --id --run --kill --status' -- "$cur" ))
            esac
           ;;
        stop)
            case "$prev" in
                -i|--id)
                    _iotlab_experiment_id
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help -i --id' -- "$cur" ))
            esac
            ;;
        get)
            case "$prev" in
                -i|--id)
                    _iotlab_experiment_id
                    ;;
                --offset|--limit)
                    # We don't need to complete there
                    ;;
                --state)
                    COMPREPLY=($(compgen -W "${_iotlab_states[*]}" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help -i --id -r --resources -ri --resources-id -s --exp-state -st --start-time -p --print -a --archive -l --list --offset --limit --state -e --experiments --active' -- "$cur" ))
            esac
            ;;
        load)
            case "$prev" in
                -f|--file)
                    _filedir json
                    ;;
                -l|--list)
                    _filedir
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help -f --file -l --list' -- "$cur" ))
            esac
            ;;
        reload)
            case "$prev" in
                -i|--id)
                    _iotlab_experiment_id
                    ;;
                -d|--duration|-r|--reservation)
                    # We don't need to complete there
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help -i --id -d --duration -r --reservation' -- "$cur" ))
            esac
            ;;
        info)
            case "$prev" in
                --site)
                    COMPREPLY=($(compgen -W "${_iotlab_sites[*]}" -- "$cur"))
                    ;;
                --archi)
                    COMPREPLY=($(compgen -W "${_iotlab_archis[*]}" -- "$cur"))
                    ;;
                --state)
                    COMPREPLY=($(compgen -W "${_iotlab_states[*]}" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help --site --archi --state -l --list -li --list-id' -- "$cur"))
                    ;;
            esac
            ;;
        wait)
            case "$prev" in
                -i|--id)
                    _iotlab_experiment_id
                    ;;
                --step|--timeout)
                    # We don't need to complete there
                    ;;
                --state)
                    COMPREPLY=($(compgen -W "${_iotlab_states[*]}" -- "$cur"))
                    ;;
                *)
                    COMPREPLY=($(compgen -W '-h --help -i --id --state --step --timeout' -- "$cur"))
                    ;;
            esac
    esac
}

_iotlab_node() {
    local cur prev words cword
    _init_completion || return

    case "$prev" in
        -u|--username|-p|--password|--jmespath|--jp|--format|--fmt)
            # We don't need to complete there
            ;;
        -i|--id)
            _iotlab_experiment_id
            ;;
        -up|--update)
            _filedir
            ;;
        --profile|--update-profile)
            _iotlab_profile
            ;;
        --profile-load)
            _filedir json
            ;;
        -e|--exclude)
            _iotlab_resources_list
            ;;
        -l|--list)
            _iotlab_resources_list
            ;;
        *)
            COMPREPLY=($(compgen -W '-h --help -u --user -p --password -v --version -i --id -sta --start -sto --stop -r --reset --update-idle --debug-start --debug-stop -up --update --profile --profile-load --profile-reset -e --exclude -l --list --jmespath --jp --format --fmt' -- "$cur"))
            ;;
    esac
}

_iotlab_admin() {
    local cur prev words cword
    _init_completion || return

    # Look for the command name
    local subcword cmd
    for (( subcword=1; subcword < ${#words[@]}-1; subcword++ )); do
        [[ ${words[subcword]} != -* && \
            ! ${words[subcword-1]} =~ -+(jmespath|jp|format|fmt|u(ser)?|p(assword)) ]] && \
                { cmd=${words[subcword]}; break; }
    done

    if [[ -z $cmd ]]; then
        case "$prev" in
            -u|--username|-p|--password|--jmespath|--jp|--format|--fmt)
                # We don't need to complete there
                ;;
            *)
                COMPREPLY=($(compgen -W 'wait -h --help -u --user -p --password -v --version --jmespath --jp --format --fmt' -- "$cur"))
                ;;
        esac
    else
        # Sole `wait` command
        case "$prev" in
            -u|--username|-p|--password|--jmespath|--jp|--format|--fmt)
                # We don't need to complete there
                ;;
            -i|--id)
                _iotlab_experiment_id
                ;;
            --state)
                COMPREPLY=($(compgen -W "${_iotlab_states[*]}" -- "$cur"))
                ;;
            --step|--timeout)
                # We don't need to complete there
                ;;
            --exp-user)
                # FIXME: don't know what that option does…
                ;;
            *)
                COMPREPLY=($(compgen -W '-h --help -i --id --state --step --timeout --exp-user' -- "$cur"))
                ;;
        esac
    fi
}

_iotlab_auth() {
    case "$prev" in
        -u|--username|-p|--password|--jmespath|--jp|--format|--fmt)
            # We don't need to complete there
            ;;
        *)
            COMPREPLY=($(compgen -W '-h --help -u --user -p --password -v --version --jmespath --jp --format --fmt' -- "$cur"))
            ;;
    esac
}

complete -F _iotlab_admin iotlab-admin
complete -F _iotlab_admin admin-cli
complete -F _iotlab_auth iotlab-auth
complete -F _iotlab_auth auth-cli
complete -F _iotlab_experiment iotlab-experiment
complete -F _iotlab_experiment experiment-cli
complete -F _iotlab_node iotlab-node
complete -F _iotlab_node node-cli
# TODO
#complete -F _iotlab_profile iotlab-profile
#complete -F _iotlab_profile profile-cli
#complete -F _iotlab_robot iotlab-robot
#complete -F _iotlab_robot robot-cli
#complete -F _iotlab_ssh iotlab-ssh
#complete -F _iotlab_ssh ssh-cli
