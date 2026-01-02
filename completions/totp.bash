_totp_entries() {
    local base="$HOME/.totp/store"
    [ -d "$base" ] || return
    find "$base" -type f -name '*.gpg' \
        | sed "s|$base/||" \
        | sed 's|\.gpg$||'
}

_totp() {
    local cur prev
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    case "$prev" in
        code|del|rm)
            COMPREPLY=( $(compgen -W "$(_totp_entries)" -- "$cur") )
            ;;
        *)
            COMPREPLY=( $(compgen -W "add code del rm list ls tree config" -- "$cur") )
            ;;
    esac
}

complete -F _totp totp

