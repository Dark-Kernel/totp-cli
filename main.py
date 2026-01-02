#!/usr/bin/env python3

import time
import hmac
import hashlib
import base64
import struct
import argparse
import subprocess
from pathlib import Path
import sys
import getpass
import os

STORE = Path.home() / ".totp" / "store"

CONFIG = Path.home() / ".totp" / "config"


def list_gpg_recipients():
    p = subprocess.run(
        ["gpg", "--list-secret-keys", "--with-colons"],
        capture_output=True,
        text=True,
        check=True
    )

    recipients = []
    current_uid = None

    for line in p.stdout.splitlines():
        parts = line.split(":")
        if parts[0] == "uid":
            uid = parts[9]
            recipients.append(uid)

    if not recipients:
        sys.exit("no gpg public keys found")

    return recipients

def select_recipient_interactive():
    recipients = list_gpg_recipients()

    for i, r in enumerate(recipients):
        print(f"{i+1}) {r}")

    while True:
        try:
            idx = int(input("select recipient: ")) - 1
            if 0 <= idx < len(recipients):
                return recipients[idx]
        except ValueError:
            pass

def resolve_recipient(args):
    if args.recipient:
        return args.recipient

    if CONFIG.exists():
        return get_default_recipient()

    recipient = select_recipient_interactive()
    set_default_recipient(recipient)
    return recipient



def get_default_recipient():
    if not CONFIG.exists():
        sys.exit("no default recipient set")
    for line in CONFIG.read_text().splitlines():
        if line.startswith("recipient="):
            return line.split("=", 1)[1].strip()
    sys.exit("invalid config")

def set_default_recipient(recipient):
    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(f"recipient={recipient}\n")


def read_secret(args):
    if args.secret:
        return args.secret
    return getpass.getpass("secret: ").strip()



def store_secret(name, secret, gpg_recipient):
    STORE.mkdir(parents=True, exist_ok=True)
    path = STORE / f"{name}.gpg"
    path.parent.mkdir(parents=True, exist_ok=True)

    p = subprocess.run(
        ["gpg", "-e", "-r", gpg_recipient, "-o", str(path)],
        input=secret.encode(),
        check=True
    )

def load_secret(name):
    path = STORE / f"{name}.gpg"
    if not path.exists():
        sys.exit("entry not found")

    p = subprocess.run(
        ["gpg", "-dq", str(path)],
        capture_output=True,
        check=True
    )
    return p.stdout.decode().strip()

def cmd_add(args):
    secret = read_secret(args)
    recipient = resolve_recipient(args)
    store_secret(args.name, secret, recipient)
    print(args.name)

def cmd_del(args):
    path = STORE / f"{args.name}.gpg"
    if not path.exists():
        sys.exit("entry not found")
    path.unlink()
    parent = path.parent
    while parent != STORE and not any(parent.iterdir()):
        parent.rmdir()
        parent = parent.parent


def cmd_config(args):
    set_default_recipient(args.recipient)
    print("ok")

def cmd_code(args):
    secret = load_secret(args.name)
    code = totp(secret, args.digits, args.period)

    if args.clip:
        if os.environ.get("WAYLAND_DISPLAY"):
            subprocess.run(["wl-copy"], input=code.encode(), check=True)
        else:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=code.encode(),
                check=True
            )
    else:
        print(code)



def cmd_list(_args):
    if not STORE.exists():
        return
    for f in sorted(STORE.rglob("*.gpg")):
        print(f.relative_to(STORE).with_suffix(""))


def cmd_tree(_args):
    if STORE.exists():
        print("store")
        print_tree(STORE)

def print_tree(root, prefix=""):
    entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name))
    for i, path in enumerate(entries):
        connector = "└── " if i == len(entries) - 1 else "├── "
        name = path.name.removesuffix(".gpg")
        print(prefix + connector + name)

        if path.is_dir():
            extension = "    " if i == len(entries) - 1 else "│   "
            print_tree(path, prefix + extension)




def totp(secret, digits=6, period=30, algo=hashlib.sha1):
    key = base64.b32decode(secret.upper(), casefold=True)
    counter = int(time.time() // period)
    msg = struct.pack(">Q", counter)

    hmac_digest = hmac.new(key, msg, algo).digest()
    offset = hmac_digest[-1] & 0x0F
    code = struct.unpack(">I", hmac_digest[offset:offset+4])[0] & 0x7FFFFFFF

    return str(code % (10 ** digits)).zfill(digits)

def main():
    #structure
    # totp add aws-root
    # totp code aws-root
    # totp list

    parser = argparse.ArgumentParser(prog="totp")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # add
    p_add = sub.add_parser("add")
    p_add.add_argument("name")
    p_add.add_argument("--secret")
    p_add.add_argument("--recipient")
    p_add.set_defaults(func=cmd_add)

    # code
    p_code = sub.add_parser("code")
    p_code.add_argument("name")
    p_code.add_argument("--digits", type=int, default=6)
    p_code.add_argument("--period", type=int, default=30)
    p_code.add_argument("--clip", action="store_true")
    p_code.set_defaults(func=cmd_code)


    # del
    p_del = sub.add_parser("del")
    p_del.add_argument("name")
    p_del.set_defaults(func=cmd_del)

    # rm
    p_rm = sub.add_parser("rm")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=cmd_del)

    # list
    p_list = sub.add_parser("list")
    p_list.set_defaults(func=cmd_list)

    # ls
    p_list = sub.add_parser("ls")
    p_list.set_defaults(func=cmd_list)

    # config
    p_cfg = sub.add_parser("config")
    p_cfg.add_argument("--recipient", required=True)
    p_cfg.set_defaults(func=cmd_config)

    # tree
    p_tree = sub.add_parser("tree")
    p_tree.set_defaults(func=cmd_tree)


    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

