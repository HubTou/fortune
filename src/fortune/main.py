#!/usr/bin/env python
""" fortune - print a random, hopefully interesting, adage
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Hubert Tournier
"""

import getopt
import logging
import os
import random
import re
import sys
import time

import strfile

# Version string used by the what(1) and ident(1) commands:
ID = "@(#) $Id: fortune - print a random, hopefully interesting, adage v1.0.0 (August 9, 2021) by Hubert Tournier $"

# Default parameters. Can be overcome by environment variables, then command line options
parameters = {
    "Compatibility mode": False,
    "Logging level": logging.INFO,
    "Debug": 0,
    "Path": [],
    "Save state": False,
    "Offensive only": False,
    "All files": False,
    "List files": False,
    "Show cookie file": False,
    "Equal size": False,
    "Long only": False,
    "Short only": False,
    "Short max length": 160,
    "Max attempts": 10,
    "Pattern": None,
    "Ignore case": False,
    "Wait": False,
    "Minimum wait": 6,
    "Characters per second": 20,
    "Command flavour": "",
}


################################################################################
def display_help():
    """Displays usage and help"""
    print("usage: fortune [--debug] [--help|-?] [--version]", file=sys.stderr)
    print("       [-acCDefilosw] [-m pattern] [-n length] [-t tries]", file=sys.stderr)
    print("       [--] [[N%] file/directory/all]", file=sys.stderr)
    print("  ----------  -------------------------------------------------------", file=sys.stderr)
    print("  -a          Choose from all lists of maxims, both offensive and not", file=sys.stderr)
    print("  -c          Show the cookie file from which the fortune came", file=sys.stderr)
    print("  -C          Enable compatibility mode", file=sys.stderr)
    print("  -D          Enable additional debugging output", file=sys.stderr)
    print("  -e          Consider all fortune files to be of equal size", file=sys.stderr)
    print("  -f          Print out the list of files which would be searched", file=sys.stderr)
    print("  -l          Long dictums only", file=sys.stderr)
    print("  -m pattern  Print out all fortunes which match the RegEx pattern", file=sys.stderr)
    print("  -n length   Set the longest short fortune length ({} chars)".format(
        parameters["Short max length"]), file=sys.stderr
    )
    print("  -o          Choose only from potentially offensive aphorisms", file=sys.stderr)
    print("  -s          Short apophthegms only", file=sys.stderr)
    print("  -t tries    Set the maximum number of attempts ({} tries)".format(
        parameters["Max attempts"]), file=sys.stderr
    )
    print("  -i          Ignore case for -m patterns", file=sys.stderr)
    print("  -w          Wait before termination for an amount of time", file=sys.stderr)
    print("  --debug     Enable debug mode", file=sys.stderr)
    print("  --help|-?   Print usage and this help message and exit", file=sys.stderr)
    print("  --version   Print version and exit", file=sys.stderr)
    print("  --          Options processing terminator", file=sys.stderr)
    print(file=sys.stderr)


################################################################################
def process_environment_variables():
    """Process environment variables"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    if "FORTUNE_DEBUG" in os.environ.keys():
        logging.disable(logging.NOTSET)
        parameters["Logging level"] = logging.NOTSET

    if "FORTUNE_COMPAT" in os.environ.keys():
        parameters["Compatibility mode"] = True

    if "FORTUNE_PATH" in os.environ.keys():
        for directory in os.environ["FORTUNE_PATH"].split(os.pathsep):
            if os.path.isdir(directory):
                parameters["Path"].append(directory)
            else:
                logging.warning('FORTUNE_PATH directory "%s" not found', directory)
        if len(parameters["Path"]) == 0:
            if parameters["Compatibility mode"]:
                print("fortune: FORTUNE_PATH: None of the specified directories found.",
                    file=sys.stderr
                )
            else:
                logging.critical("None of the directories specified in FORTUNE_PATH found")
            sys.exit(1)
    else:
        if os.name == "posix":
            if os.path.isdir("/usr/share/games/fortune"):
                parameters["Path"].append("/usr/share/games/fortune")
            if os.path.isdir("/usr/local/share/games/fortune"):
                parameters["Path"].append("/usr/local/share/games/fortune")
            if "HOME" in os.environ.keys():
                home = os.environ["HOME"]
                if os.path.isdir(home + os.sep + ".local/share/games/fortune"):
                    parameters["Path"].append(home + os.sep + ".local/share/games/fortune")

        elif os.name == "nt":
            appdata_path = os.sep + "appdata" + os.sep + "roaming"
            pnu_fortune_path = os.sep + "python" + os.sep + "share" + os.sep + "games" + os.sep + "fortune"
            if os.environ["APPDATA"]:
                pnu_fortune_path = os.environ["APPDATA"] + pnu_fortune_path
            elif os.environ["HOMEPATH"]:
                pnu_fortune_path = os.environ["HOMEPATH"] + appdata_path + pnu_fortune_path
            elif os.environ["USERPROFILE"]:
                pnu_fortune_path = os.environ["USERPROFILE"] + appdata_path + pnu_fortune_path
            if os.path.isdir(pnu_fortune_path):
                parameters["Path"].append(pnu_fortune_path)

        if len(parameters["Path"]) == 0:
            logging.critical("No fortune databases directories found")
            sys.exit(1)

    # UNUSED:
    # The original command tries to write a fortune cookie file with the ".pos" extension
    # in the root owned directory where the cookie files reside, which results in a
    # "Permission denied" error message. So, apart for debugging purposes, this doesn't
    # seem useful to reimplement user wise...
    if "FORTUNE_SAVESTATE" in os.environ.keys():
        parameters["Save state"] = True

    # TODO:
    # To be used one day to diffentiate command behaviour between the Unix V7, BSD
    # and Linux versions.
    if "FLAVOUR" in os.environ.keys():
        parameters["Command flavour"] = os.environ["FLAVOUR"].lower()
    if "FORTUNE_FLAVOUR" in os.environ.keys():
        parameters["Command flavour"] = os.environ["FORTUNE_FLAVOUR"].lower()

    logging.debug("process_environment_variables(): parameters:")
    logging.debug(parameters)


################################################################################
def process_command_line():
    """Process command line options"""
    # pylint: disable=C0103
    global parameters
    # pylint: enable=C0103

    # option letters followed by : expect an argument
    # same for option strings followed by =
    character_options = "acCDeflm:n:ost:iw?"
    string_options = [
        "debug",
        "help",
        "version",
    ]

    try:
        options, remaining_arguments = getopt.getopt(
            sys.argv[1:], character_options, string_options
        )
    except getopt.GetoptError as error:
        if parameters["Compatibility mode"]:
            option = re.sub(r"(^option -| not recognized$)", "", str(error))
            print("fortune: illegal option -- {}".format(option), file=sys.stderr)
            print("fortune [-aDefilosw] [-m pattern] [[N%] file/directory/all]", file=sys.stderr)
        else:
            logging.critical("Syntax error: %s", error)
            display_help()
        sys.exit(1)

    for option, argument in options:

        if option == "--debug":
            logging.disable(logging.NOTSET)
            parameters["Logging level"] = logging.NOTSET

        elif option in ("--help", "-?"):
            display_help()
            sys.exit(0)

        elif option == "--version":
            print(ID.replace("@(" + "#)" + " $" + "Id" + ": ", "").replace(" $", ""))
            sys.exit(0)

        elif option == "-a":
            parameters["All files"] = True
            parameters["Offensive only"] = False

        elif option == "-c":
            parameters["Show cookie file"] = True

        elif option == "-C":
            parameters["Compatibility mode"] = True

        # UNUSED:
        # Superseded by the --debug option.
        # This doesn't seem useful to reimplement user wise...
        elif option == "-D":
            parameters["Debug"] += 1

        elif option == "-e":
            parameters["Equal size"] = True

        elif option == "-f":
            parameters["List files"] = True

        elif option == "-i":
            parameters["Ignore case"] = True

        elif option == "-l":
            parameters["Long only"] = True
            parameters["Short only"] = False

        elif option == "-m":
            try:
                _ = re.compile(argument)
            except:
                if parameters["Compatibility mode"]:
                    print("regcomp({}) fails".format(argument), file=sys.stderr)
                else:
                    logging.critical("Invalid -m pattern: %s", argument)
                sys.exit(1)
            parameters["Pattern"] = argument

        elif option == "-n":
            try:
                parameters["Short max length"] = int(argument)
            except ValueError:
                logging.critical("Invalid -n length: %s", argument)
                sys.exit(1)
            if parameters["Short max length"] < 1:
                logging.critical("Longest short fortunes cannot be lower than 1")
                sys.exit(1)

        elif option == "-o":
            if not parameters["All files"]:
                parameters["Offensive only"] = True

        elif option == "-s":
            parameters["Short only"] = True
            parameters["Long only"] = False

        elif option == "-t":
            try:
                parameters["Max attempts"] = int(argument)
            except ValueError:
                logging.critical("Invalid -t tries: %s", argument)
                sys.exit(1)
            if parameters["Max attempts"] < 1:
                logging.critical("Max attempts cannot be lower than 1")
                sys.exit(1)

        elif option == "-w":
            parameters["Wait"] = True

    logging.debug("process_command_line(): parameters:")
    logging.debug(parameters)
    logging.debug("process_command_line(): remaining_arguments:")
    logging.debug(remaining_arguments)

    return remaining_arguments


################################################################################
def process_file(name):
    """Return a dictionary describing a fortune file"""
    dirname = os.path.dirname(name)
    basename = os.path.basename(name)
    header = strfile.read_strfile_header(name)

    logging.debug("%s / %s => %d fortune(s)", dirname, basename, header["number of strings"])

    return {"Dirname": dirname, "Basename": basename, "Header": header, "Prob": 0}


################################################################################
def process_filesystem_item(name):
    """Search a directory or file for fortune files and return a list of them"""
    fortune_files = []
    if os.path.isdir(name):
        found_something = False
        for item in os.listdir(name):
            item_path = name + os.sep + item
            if os.path.isfile(item_path) \
            and not item.endswith(".dat"):
                if item.endswith("-o"):
                    if parameters["Offensive only"] or parameters["All files"]:
                        if os.path.isfile(item_path + ".dat"):
                            found_something = True
                            fortune_files.append(process_file(item_path))
                elif not parameters["Offensive only"]:
                    if os.path.isfile(item_path + ".dat"):
                        found_something = True
                        fortune_files.append(process_file(item_path))

        if not found_something:
            if parameters["Compatibility mode"]:
                print("fortune: {}: No fortune files in directory.".format(name), file=sys.stderr)
                print("fortune:{} not a fortune file or directory".format(name), file=sys.stderr)
            else:
                logging.critical("No fortune files in directory %s", name)
            sys.exit(1)

        return fortune_files

    # elif os.path.isfile(name):
    # Fortune only process a file if both the text and the dat files are present:
    if os.path.isfile(name + ".dat"):
        return [ process_file(name) ]

    return []


################################################################################
def process_name(name):
    """Search a directory or file for fortune files and return a list of them"""
    fortune_files = []

    if name == "all":
        for directory in parameters["Path"]:
            for item in os.listdir(directory):
                item_path = directory + os.sep + item
                if os.path.isfile(item_path) \
                and not item.endswith("-o") \
                and not item.endswith(".dat"):
                    fortune_files += process_filesystem_item(item_path)
        return fortune_files

    if name == "all-o":
        for directory in parameters["Path"]:
            for item in os.listdir(directory):
                item_path = directory + os.sep + item
                if os.path.isfile(item_path) \
                and item.endswith("-o") \
                and not item.endswith(".dat"):
                    fortune_files += process_filesystem_item(item_path)
        return fortune_files

    dirname = os.path.dirname(name)
    if dirname:
        # Absolute path:
        if os.path.exists(name):
            fortune_files = process_filesystem_item(name)
        else:
            if not parameters["Compatibility mode"]:
                logging.critical("'%s' does not exist", name)
            sys.exit(1)
    else:
        # Relative path:
        found = False
        if os.path.exists(name):
            found = True
            fortune_files = process_filesystem_item(name)
        for directory in parameters["Path"]:
            if os.path.isfile(directory + os.sep + name):
                found = True
                fortune_files += process_filesystem_item(directory + os.sep + name)
        if not found:
            if parameters["Compatibility mode"]:
                print("No '{}' found in {}.".format(name, ":".join(parameters["Path"])), file=sys.stderr)
            else:
                logging.critical("No '%s' found in %s", name, ":".join(parameters["Path"]))
            sys.exit(1)

    return fortune_files


################################################################################
def count_strings(files_list):
    """Count the number of strings in a list of files"""
    number_of_strings = 0
    for file in files_list:
        number_of_strings += file["Header"]["number of strings"]

    return number_of_strings


################################################################################
def process_arguments(arguments):
    """Process remaining command-line args and return a fortune files list with probabilities"""
    fortune_files = []
    probabilities = []
    no_probabilities = []
    probabilities_sum = 0

    if len(arguments):
        probability = None
        for argument in arguments:
            if argument.endswith("%"):
                if probability is None:
                    if argument[:-1].isdigit():
                        probability = int(argument[:-1])
                        probabilities_sum += probability
                        if probability > 100:
                            if parameters["Compatibility mode"]:
                                print("percentages must be <= 100", file=sys.stderr)
                            else:
                                logging.critical("percentages must be <= 100")
                            sys.exit(1)
                        continue

            if os.path.isdir(argument):
                files = process_name(argument)
            elif parameters["Offensive only"]:
                files = process_name(argument + "-o")
            elif parameters["All files"]:
                files = process_name(argument)
                files += process_name(argument + "-o")
            else:
                files = process_name(argument)
            fortune_files += files

            if probability:
                probabilities.append([files, probability])
                probability = None
            else:
                no_probabilities.append(files)

        if probabilities_sum > 100:
            if parameters["Compatibility mode"]:
                print("fortune: probabilities sum to {}% > 100%!".format(probabilities_sum), file=sys.stderr)
            else:
                logging.critical("Probabilities sum to {}% > 100%!".format(probabilities_sum))
            sys.exit(1)

        if probabilities_sum < 100 and not no_probabilities:
            if parameters["Compatibility mode"]:
                print("fortune: no place to put residual probability ({}% < 100%)".format(probabilities_sum), file=sys.stderr)
            else:
                logging.critical("No place to put residual probability ({}% < 100%)".format(probabilities_sum))
            sys.exit(1)

    else:
        if parameters["Offensive only"]:
            fortune_files = process_name("fortunes-o")
        elif parameters["All files"]:
            fortune_files = process_name("fortunes")
            fortune_files += process_name("fortunes-o")
        else:
            fortune_files = process_name("fortunes")

    # Now it's time to assign those damned probabilities!
    if len(fortune_files) == 1:
        fortune_files[0]["Prob"] = 100
    elif parameters["Equal size"]:
        probability = 100 / len(fortune_files)
        for file in fortune_files:
            file["Prob"] = probability
    elif probabilities_sum == 0:
        number_of_strings = count_strings(fortune_files)
        for file in fortune_files:
            file["Prob"] = (file["Header"]["number of strings"] * 100) / number_of_strings
    else:
        # First assign the remaining probabilities to all the remaining files:
        if no_probabilities:
            all_files = []
            for file_list in no_probabilities:
                for file in file_list:
                    all_files.append(file)
            probabilities.append([all_files, 100 - probabilities_sum])

        # Then split all group probabilities between individual files
        # according to their respective weight:
        for element in probabilities:
            if len(element[0]) == 1:
                for file in fortune_files:
                    if file["Dirname"] == element[0][0]["Dirname"] \
                    and file["Basename"] == element[0][0]["Basename"]:
                        file["Prob"] += element[1]
                        break
            else:
                number_of_strings = count_strings(element[0])
                for sub_element in element[0]:
                    for file in fortune_files:
                        if file["Dirname"] == sub_element["Dirname"] \
                        and file["Basename"] == sub_element["Basename"]:
                            file["Prob"] += element[1] * (sub_element["Header"]["number of strings"] / number_of_strings)
                            break

    return fortune_files


################################################################################
def sum_probabilities(fortune_files, directory):
    """Return the overall probability to select the files in the directory"""
    probability = 0
    for file in fortune_files:
        if file["Dirname"] == directory:
            probability += file["Prob"]

    return probability


################################################################################
def list_files(fortune_files):
    """Print the list of directories and fortune files with probabilities"""
    files = sorted(fortune_files, key=lambda k: (k["Dirname"], k["Basename"]))

    directory = ""
    for file in files:
        if file["Dirname"] != directory:
            directory = file["Dirname"]
            probability = sum_probabilities(fortune_files, directory)
            if parameters["Compatibility mode"]:
                print("{:>6.2f}% {}".format(probability, directory), file=sys.stderr)
            else:
                print("{:>6.2f}% {}".format(probability, directory))

        prefix = "    "
        if not file["Dirname"]:
            prefix = ""

        if parameters["Compatibility mode"]:
            print("{}{:>6.2f}% {}".format(prefix, file["Prob"], file["Basename"]), file=sys.stderr)
        else:
            if parameters["Logging level"] == logging.NOTSET:
                print("{}{:>6.2f}% {} (#{})".format(prefix, file["Prob"], file["Basename"], file["Header"]["number of strings"]))
            else:
                print("{}{:>6.2f}% {}".format(prefix, file["Prob"], file["Basename"]))


################################################################################
def search_for_pattern(fortune_files):
    """Print the list of fortunes matching the given pattern"""
    found = False
    for file in fortune_files:
        if file["Dirname"]:
            filename = file["Dirname"] + os.sep + file["Basename"]
        else:
            filename = file["Basename"]
        offsets = strfile.read_strfile_body(filename, file["Header"]["number of strings"])
        comment = file["Header"]["delimiting char"] + file["Header"]["delimiting char"]
        found_here = False

        for i in range(file["Header"]["number of strings"]):
            fortune = strfile.read_fortune(filename, offsets[i], file["Header"]["delimiting char"])

            if file["Header"]["comments flag"] and fortune.startswith(comment):
                continue

            if file["Header"]["rotated flag"]:
                fortune = rot13(fortune)

            if parameters["Ignore case"]:
                results = re.search(parameters["Pattern"], fortune, flags=re.IGNORECASE)
            else:
                results = re.search(parameters["Pattern"], fortune)

            if results:
                if not found_here:
                    print("{} ({})".format(comment, file["Basename"]))
                    found_here = True
                else:
                    print(comment)
                print(fortune, end="")

        if found_here:
            found = True

    return found


################################################################################
def select_fortune_file(fortune_files):
    """Randomly choose a fortune file"""
    alea = random.randint(1, 100000)
    total = 0
    for file in fortune_files:
        total += file["Prob"] * 1000
        if alea <= total:
            logging.debug("Selected file:")
            logging.debug(file)

            return file

    return None


################################################################################
def rot13(fortune):
    """Return the ROT13 version of the given fortune"""
    # TODO:
    # To be moved one day in a future rot13 command/library
    rotated_fortune = ""
    for character in fortune:
        if character.isalpha():
            if character.isupper():
                rotated_fortune += chr(ord('A') + (ord(character) - ord('A') + 13) % 26)
            else:
                rotated_fortune += chr(ord('a') + (ord(character) - ord('a') + 13) % 26)
        else:
            rotated_fortune += character

    return rotated_fortune


################################################################################
def select_fortune(file):
    """Randomly choose a fortune from a fortune file"""

    if parameters["Short only"] \
    and file["Header"]["shortest length"] > parameters["Short max length"]:
        return None

    if parameters["Long only"] \
    and file["Header"]["longest length"] <= parameters["Short max length"]:
        return None

    if file["Dirname"]:
        filename = file["Dirname"] + os.sep + file["Basename"]
    else:
        filename = file["Basename"]
    offsets = strfile.read_strfile_body(filename, file["Header"]["number of strings"])
    comment = file["Header"]["delimiting char"] + file["Header"]["delimiting char"]

    for _ in range(parameters["Max attempts"]):
        alea = random.randint(0, file["Header"]["number of strings"] - 1)
        fortune = strfile.read_fortune(filename, offsets[alea], file["Header"]["delimiting char"])

        if parameters["Short only"] and len(fortune) > parameters["Short max length"]:
            continue

        if parameters["Long only"] and len(fortune) <= parameters["Short max length"]:
            continue

        if file["Header"]["comments flag"] and fortune.startswith(comment):
            continue

        if file["Header"]["rotated flag"]:
            return rot13(fortune)

        return fortune

    return None


################################################################################
def main():
    """The program's main entry point"""
    program_name = os.path.basename(sys.argv[0])
    exit_status = 0

    console_log_format = program_name + ": %(levelname)s: %(message)s"
    logging.basicConfig(format=console_log_format, level=logging.DEBUG)
    logging.disable(logging.INFO)

    process_environment_variables()
    arguments = process_command_line()
    fortune_files = process_arguments(arguments)

    if parameters["List files"]:
        list_files(fortune_files)

    elif parameters["Pattern"]:
        if not search_for_pattern(fortune_files):
            exit_status = 1

    else:
        selected_file = select_fortune_file(fortune_files)

        if parameters["Show cookie file"]:
            if selected_file["Dirname"]:
                print("({})".format(selected_file["Dirname"] + os.sep + selected_file["Basename"]))
            else:
                print("({})".format(selected_file["Basename"]))
            print("{}".format(selected_file["Header"]["delimiting char"]))

        fortune = select_fortune(selected_file)

        if fortune is None:
            exit_status = 1
        else:
            print(fortune, end="")

            if parameters["Wait"]:
                wait_time = len(fortune) / parameters["Characters per second"]
                if wait_time < parameters["Minimum wait"]:
                    wait_time = parameters["Minimum wait"]
                time.sleep(wait_time)

    sys.exit(exit_status)


if __name__ == "__main__":
    main()
