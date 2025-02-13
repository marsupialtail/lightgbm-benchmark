# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
LightGBM/Python inferencing script
"""
import os
import sys
import argparse
from lightgbm import Booster, Dataset
from subprocess import PIPE
from subprocess import run as subprocess_run
from subprocess import TimeoutExpired

# let's add the right PYTHONPATH for common module
COMMON_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

if COMMON_ROOT not in sys.path:
    print(f"Adding {COMMON_ROOT} to PYTHONPATH")
    sys.path.append(str(COMMON_ROOT))

# before doing local import
from common.metrics import LogTimeBlock
from common.io import input_file_path

def get_arg_parser(parser=None):
    """Adds component/module arguments to a given argument parser.

    Args:
        parser (argparse.ArgumentParser): an argument parser instance

    Returns:
        ArgumentParser: the argument parser instance

    Notes:
        if parser is None, creates a new parser instance
    """
    # add arguments that are specific to the module
    if parser is None:
        parser = argparse.ArgumentParser(__doc__)

    group_i = parser.add_argument_group("Input Data")
    group_i.add_argument("--lightgbm_exec",
        required=True, type=str, help="Path to lightgbm.exe (file path)")
    group_i.add_argument("--data",
        required=True, type=input_file_path, help="Inferencing data location (file path)")
    group_i.add_argument("--model",
        required=False, type=input_file_path, help="Exported model location")
    group_i.add_argument("--output",
        required=False, default=None, type=str, help="Inferencing output location (file path)")
    
    return parser


def run(args, other_args=[]):
    """Run script with arguments (the core of the component)

    Args:
        args (argparse.namespace): command line arguments provided to script
        unknown_args (list[str]): list of arguments not known
    """
    # create sub dir and output file
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        args.output = os.path.join(args.output, "predictions.txt")

    if not os.path.isfile(args.lightgbm_exec):
        raise Exception(f"Could not find lightgbm exec under path {args.lightgbm_exec}")

    lightgbm_cli_command = [
        args.lightgbm_exec,
        "task=prediction",
        f"data={args.data}",
        f"input_model={args.model}",
        "verbosity=2"
    ]
    if args.output:
        lightgbm_cli_command.append(f"output_result={args.output}")

    metric_tags = {'framework':'lightgbm_cli','task':'score'}

    print(f"Running .predict()")
    with LogTimeBlock("inferencing", methods=['print'], tags=metric_tags):
        lightgbm_cli_call = subprocess_run(
            " ".join(lightgbm_cli_command),
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
            check=False, # will not raise an exception if subprocess fails (so we capture with .returncode)
            timeout=None
        )
        print(f"LightGBM stdout: {lightgbm_cli_call.stdout}")
        print(f"LightGBM stderr: {lightgbm_cli_call.stderr}")
        print(f"LightGBM return code: {lightgbm_cli_call.returncode}")


def main(cli_args=None):
    """ Component main function, parses arguments and executes run() function.

    Args:
        cli_args (List[str], optional): list of args to feed script, useful for debugging. Defaults to None.
    """
    # construct arg parser
    parser = get_arg_parser()
    args, unknown_args = parser.parse_known_args(cli_args)

    # run the actual thing
    run(args, unknown_args)


if __name__ == "__main__":
    main()    
