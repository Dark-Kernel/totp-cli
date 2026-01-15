## TOTP CLI

A command-line tool for generating and validating TOTP (Time-based One-time Password) codes for MFA (Multi-Factor Authentication).


Minimal, offline, GPG-backed TOTP CLI authenticator.

- RFC 6238 compliant
- No cloud
- No GUI
- Secrets encrypted with your GPG key
- Fully interoperable with Google Authenticator, AWS, GitHub, etc.


## Requirements

- Python 3.8+
- gpg
- (optional) wl-copy or xclip for clipboard support


## Install (binary)

```sh
curl -fsSL https://github.com/Dark-Kernel/totp-cli/releases/latest/download/install.sh | sh
````

Installs `totp` into `/usr/local/bin` or `$HOME/.local/bin`.

---

## First use

```sh
totp add aws
```

On first run:

* Lists available GPG secret keys
* Prompts once to select default recipient
* Stores encrypted secret
* Creates a config file in `~/.totp/config`
* Initilizes git repo in `~/.totp`



## Commands

### Add secret

```sh
totp add aws
totp add github --secret JBSWY3DPEHPK3PXP
totp add gmail/email@gmail.com
```

### Generate code

```sh
totp code aws
totp code aws --clip # copy to clipboard
```

### List entries

```sh
totp list
totp ls
totp tree
```



### Remove entry

```sh
totp del aws
totp rm aws
```

### Change default GPG recipient

```sh
totp config --recipient you@example.com
```

### Git integration

```sh
totp git <command>
```

### Autocompletions

Just clone the repository, or grab the completions from [here](https://github.com/Dark-Kernel/totp-cli/tree/master/completions)

```sh 
# bash
sudo cp completions/totp.bash /etc/bash_completion.d/totp

# fish
mkdir -p ~/.config/fish/completions
cp completions/totp.fish ~/.config/fish/completions/

# zsh
sudo cp completions/_totp /usr/share/zsh/site-functions/
```



## Storage

```
~/.totp/
├── store/
│   ├── aws.gpg
│   └── github.gpg
└── config
```

Secrets are never stored in plaintext.


## Security model

* Disk compromise: safe
* Backup leaks: safe
* Session compromise: not solvable by MFA tools
* Loss of GPG private key = loss of MFA access

---

## License

[MIT](https://github.com/Dark-Kernel/totp-cli/blob/master/LICENSE)
