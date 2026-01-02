function __totp_entries
    set -l base ~/.totp/store
    test -d $base; or return
    find $base -type f -name '*.gpg' \
        | sed "s|$base/||" \
        | sed 's|\.gpg$||'
end

complete -c totp -n '__fish_use_subcommand' -a add
complete -c totp -n '__fish_use_subcommand' -a code
complete -c totp -n '__fish_use_subcommand' -a del
complete -c totp -n '__fish_use_subcommand' -a rm
complete -c totp -n '__fish_use_subcommand' -a list
complete -c totp -n '__fish_use_subcommand' -a ls
complete -c totp -n '__fish_use_subcommand' -a tree
complete -c totp -n '__fish_use_subcommand' -a config

complete -c totp -n '__fish_seen_subcommand_from code del rm' -a '(__totp_entries)'
