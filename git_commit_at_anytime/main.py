from argparse import ArgumentParser
from datetime import datetime, timedelta
import dateutil
import dateutil.parser
import humanize
from dateutil.tz import tzlocal
import pytimeparse
import argcomplete

from ._version import __version__

import subprocess
from subprocess import Popen, PIPE, check_call
from humanize import time

import random


def run_command(cmd):
    p = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()

    stdout = stdout.decode("utf8", "strict")
    stderr = stderr.decode("utf8", "strict")
    if len(stderr) > 0:
        print(f"{bcolors.WARNING}{stderr}{bcolors.ENDC}")
        return False

    return stdout


def str_duration_to_time_delta(duration_str):
    seconds_duration = pytimeparse.timeparse.timeparse(duration_str)
    return timedelta(seconds=seconds_duration)


def random_sign():
    if random.random() < 0.5:
        return 1
    else:
        return -1


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


DEFAULT_RANDOMNESS = "1 hours"

parser = ArgumentParser()
parser.add_argument("commit_msg", nargs="?")
parser.add_argument(
    "--version", action="version", version=f"git-commit-at-anytime {__version__}"
)
parser.add_argument(
    "--no-randomness",
    help="Turn off randomness that adds deviation to the final commit time",
    action="store_true",
)
parser.add_argument(
    "-r",
    "--random-amount",
    metavar="duration",
    help=f"The max amount of deviation (default: {DEFAULT_RANDOMNESS})",
    type=str,
    default=DEFAULT_RANDOMNESS,
)
parser.add_argument(
    "-f",
    "--delta-time-from-now",
    metavar="duration",
    help=f"Set the commit time to be this amount of time ago from now",
    type=str,
)
parser.add_argument(
    "-s",
    "--delta-time-since-last-commit",
    metavar="duration",
    help=f"Set the commit time to be this amount of time after the latest commit",
    type=str,
)
parser.add_argument(
    "-t",
    "--time",
    metavar="time",
    help=f"Specific the actual time of commit",
    type=str,
)


def main(args):
    OPTIONS_THAT_SET_COMMIT_TIME = [
        args.delta_time_from_now,
        args.delta_time_since_last_commit,
        args.time,
    ]
    ##############################################
    # check for options given
    # if all(a is None for a in OPTIONS_THAT_SET_COMMIT_TIME):
    #     print(
    #         ">> NOTE: None of the options for setting commit time is given. No operation will be performed.\n"
    #     )
    if sum(1 for a in OPTIONS_THAT_SET_COMMIT_TIME if a is not None) > 1:
        print(f">> ERROR: more than one option for setting commit time is given!")
        exit(1)

    ##############################################
    # get last commit time
    out = run_command("git log -1 --format=%cd")
    if out is False:
        return 1
    last_commit_time = dateutil.parser.parse(out)
    now = datetime.now().replace(tzinfo=tzlocal())

    last_commit_time_natural_delta = time.naturaldelta(
        now - last_commit_time, minimum_unit="seconds"
    )
    print(f"> Last commit is from {last_commit_time_natural_delta} ago")

    if all(a is None for a in OPTIONS_THAT_SET_COMMIT_TIME):
        print("No operation given. Exiting.")
        return 0

    ##############################################
    random_secs = random.randint(0, pytimeparse.timeparse.timeparse(args.random_amount))
    if args.no_randomness:
        random_secs = 0
    random_delta = timedelta(seconds=random_secs)
    print(
        f"> Random deviation: {time.precisedelta(random_delta, minimum_unit='seconds')} "
        f"(max: {time.naturaldelta(str_duration_to_time_delta(args.random_amount))})"
    )
    print()

    ##############################################

    if args.time is not None:
        target_commit_time = dateutil.parser.parse(args.time)
        print(
            f">> Using a specific commit time at {humanize.naturalday(target_commit_time)}"
        )
        actual_commit_time = target_commit_time + random_sign() * random_delta
    elif args.delta_time_since_last_commit is not None:
        _delta = str_duration_to_time_delta(args.delta_time_since_last_commit)
        target_commit_time = last_commit_time + _delta
        print(
            f">> Target commit time to be {humanize.precisedelta(_delta)} after last commit"
        )
        actual_commit_time = target_commit_time + random_delta
    elif args.delta_time_from_now is not None:
        _delta = str_duration_to_time_delta(args.delta_time_from_now)
        target_commit_time = now - _delta
        print(f">> Target commit time to be {humanize.precisedelta(_delta)} ago")
        actual_commit_time = target_commit_time - random_delta

    print(f"[New commit time: {actual_commit_time}]")
    print(f"[Original target: {target_commit_time}]")

    actual_commit_time = actual_commit_time.replace(tzinfo=tzlocal())

    def get_export_cmd(datetime_str):
        return (
            f'export GIT_AUTHOR_DATE="{datetime_str}" && '
            f'export GIT_COMMITTER_DATE="{datetime_str}"'
        )

    export_cmd = get_export_cmd(actual_commit_time.strftime("%c"))
    print()
    print(
        f"Last commit --> new commit @duration {humanize.precisedelta(actual_commit_time - last_commit_time)}"
    )
    print(
        f"New commit  --> Now        @duration {humanize.precisedelta(now - actual_commit_time)}"
    )

    git_commit_cmd = "git commit"
    if args.commit_msg is not None:
        git_commit_cmd = f'{git_commit_cmd} -m "{args.commit_msg}"'

    txt = input("\nContinue? (y/N): ")
    if txt == "y":
        check_call(f"{export_cmd} && {git_commit_cmd}", shell=True)

    return 0


def run():
    argcomplete.autocomplete(parser)
    _args = parser.parse_args()
    exit(main(_args))


if __name__ == "__main__":
    run()
