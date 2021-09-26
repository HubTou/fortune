# Installation
pip install [pnu-fortune](https://pypi.org/project/pnu-fortune/)

# FORTUNE(6)

## NAME
fortune — print a random, hopefully interesting, adage

## SYNOPSIS
**fortune**
\[-acCDefilosw\]
\[-m pattern\]
\[-n length\]
\[-t tries\]
\[--debug\]
\[--help|-?\]
\[--version\]
\[--\]
\[\[N%\] file/directory/all\]

## DESCRIPTION
When **fortune** is run with no arguments it prints out a random epigram from the *fortunes* database.
Epigrams are divided into several categories, where each category is subdivided into those which are potentially offensive and those which are not.  

### OPTIONS
The options are as follows:

Option|Use
---|---
-a|Choose from all lists of maxims, both offensive and not (See the *-o* option for more information on offensive fortunes).
-c|Show the cookie file from which the fortune came.
-C|Compatibility mode. Try to imitate the original BSD fortune command display as closely as possible.
-D|Enable additional debugging output. Specify this option multiple times for more verbose output (unused in this re-implementation).
-e|Consider all fortune files to be of equal size (see discussion below on multiple files).
-f|Print out the list of files which would be searched, but do not print a fortune.
-i|Ignore case for *-m patterns*.
-l|Long dictums only. See *-n* on how ''long'' is defined.
-m pattern|Print out all fortunes which match the regular expression pattern. See regex(3) for a description of patterns.
-n length|Set the longest fortune length (in characters) considered to be ''short'' (the default is 160). All fortunes longer than this are considered ''long''.
-o|Choose only from potentially offensive aphorisms. This option is superseded by *-a*.<br><br>... let us keep in mind the basic governing philosophy<br>of The Brotherhood, as handsomely summarized in these words:<br>we believe in healthy, hearty laughter -- at the expense of<br>the whole human race, if needs be.<br>Needs be.<br>--H. Allen Smith, "Rude Jokes"
-s|Short apophthegms only. See *-n* on how ''short'' is defined.
-t tries|Set the maximum number of attempts while searching for a ''short'' or ''long'' fortune (the default is 10).
-w|Wait before termination for an amount of time calculated from the number of characters in the message. This is useful if it is executed as part of the logout procedure to guarantee that the message can be read before the screen is cleared.
--debug|Enable debug mode
--help\|-?|Print usage and a short help message and exit
--version|Print version and exit
--|Options processing terminator

The user may specify alternate sayings.
You can specify a specific file, a directory which contains one or more files, or the special word *all* which says to use all the standard databases.
Any of these may be preceded by a percentage, which is a number N between 0 and 100 inclusive, followed by a ‘%’.
If it is, there will be an N percent probability that an adage will be picked from that file or directory. 
If the percentages do not sum to 100, and there are specifications without percentages, the remaining percent will apply to those files and/or directories, in which case the probability of selecting from one of them will be based on their relative sizes.

As an example, given two databases funny and not-funny, with funny twice as big, saying

    fortune funny not-funny

will get you fortunes out of funny two-thirds of the time. The command

    fortune 90% funny 10% not-funny

will pick out 90% of its fortunes from funny (the “10% not-funny” is unnecessary, since 10% is all that is left).
The *-e* option says to consider all files equal; thus

    fortune -e funny not-funny

is equivalent to

    fortune 50% funny 50% not-funny

## ENVIRONMENT
Variable|Use
---|---
FORTUNE_PATH|The search path for the data files. It is a colon-separated list of directories in which fortune looks for datafiles. If not set it will default to */usr/share/games/fortune:/usr/local/share/games/fortune*.<br><br>Under a Posix system, *$HOME/.local/share/games/fortune* will also be added to the default, while *%HOMEPATH%/appdata/roaming/python/share/games/fortune:%HOMEPATH%\appdata\local\programs\python\pythonXX\share\games\fortune* will be added under a Windows system.<br><br>If none of the directories specified exist, it will print a warning and exit. Note that by default, fortune only searches for a *fortunes* file, instead of all files in its FORTUNE_PATH.
FORTUNE_SAVESTATE|If set, fortune will save some state about what fortune it was up to on disk (unused in this re-implementation, as it requires root access to the fortune directories).
FORTUNE_COMPAT|Compatibility mode. If set, try to imitate the original BSD fortune command display as closely as possible.
FORTUNE_DEBUG|Debug mode. If set, print some debug messages.

## FILES
Path|Description
---|---
/usr/share/games/fortune/\*|the fortunes databases (those files ending “-o” contain the offensive fortunes)
/usr/local/share/games/fortune/\*|Additional fortunes

We offer many data files for this utility in several additional packages, a few of them already installed as a dependency to this one.

## EXIT STATUS
The **fortune** utility exits 0 on success, and >0 if an error occurs.
In particular, if *-l*, *-m*, or *-s* is specified, failure to find a matching citation in the selected files counts as an error.

## EXAMPLES
Boxing the fortune output with [echobox(1)](https://github.com/HubTou/echobox/blob/main/README.md):

```
/usr/local/bin/fortune unix-philosophy unix-quotes | echobox -S single
```

## SEE ALSO
[cowsay(1)](https://linux.die.net/man/1/cowsay),
[echobox(1)](https://github.com/HubTou/echobox/blob/main/README.md),
[regex(3)](https://www.freebsd.org/cgi/man.cgi?query=regex&sektion=3),
[strfile(8)](https://github.com/HubTou/strfile/blob/main/README.md)

## STANDARDS
The **fortune** utility is a standard UNIX command, though not a part of POSIX.

This version tries to follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for [Python](https://www.python.org/) code.

## PORTABILITY
Tested OK under Windows.

## HISTORY
The **fortune** utility first appeared in Version 7 AT&T UNIX.

The much more sophisticated BSD version which this version re-implement was written by Ken Arnold around the end of 1978 and released with 4BSD and 4.1cBSD between 1980 and 1982.

This re-implementation was made for the [PNU project](https://github.com/HubTou/PNU).

It also has the *-c* and *-n* options of the Linux version.
And it added *-C* and *-t* options of its own.

## LICENSE
This utility is available under the [3-clause BSD license](https://opensource.org/licenses/BSD-3-Clause).

## AUTHORS
[Hubert Tournier](https://github.com/HubTou)

The man page is derived from the [FreeBSD project's one](https://www.freebsd.org/cgi/man.cgi?query=fortune&manpath=FreeBSD+14.0-current).

## CAVEATS
There are some display differences with the *-f* option between this re-implementation and classical BSD or Linux versions.
For instance, probability percentages are printed for all files, not just those indicated.

Another difference is that this re-implementation does not risk permanently searching for a short or long fortune in a data file which has none. It will make the specified number of attempts, then exit with an error code if nothing was found.

