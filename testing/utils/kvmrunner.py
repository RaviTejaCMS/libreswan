#!/usr/bin/env python3

# Run the pluto testsuite, for libreswan
#
# Copyright (C) 2015 Andrew Cagney <cagney@gnu.org>
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See <http://www.fsf.org/copyleft/gpl.txt>.
# 
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

import sys
import os
import re
import pexpect
import argparse
import subprocess
import time
from collections import defaultdict
from datetime import datetime
from distutils import util
from concurrent import futures
from fab import runner
from fab import testsuite
from fab import logutil
from fab import post

class Counts:

    def __init__(self):
        self.counts = defaultdict(list)

    def add(self, key, value):
        self.counts[key].append(value)

    def log_summary(self, logger, level=logutil.INFO, prefix=""):
        for key, values in sorted(self.counts.items()):
            logger.log(level, "%s%s: %d", prefix, key, len(values))

    def log_details(self, logger, level=logutil.DEBUG, prefix=""):
        for key in sorted(self.counts):
            values = self.counts[key]
            line = ""
            for value in sorted(values):
                if value:
                    line += " "
                    line += value
            logger.log(level, "%s%s:%s", prefix, key, line)


class Stats(Counts):
    def add(self, stat, test):
        Counts.add(self, stat, test.name)

class Results(Counts):
    def add(self, result):
        Counts.add(self, str(result), result.test.name)
        for error in result.errors:
            Counts.add(self, "%s(%s)" % (result, error), result.test.name)

def main():
    parser = argparse.ArgumentParser(description="Run tests")

    # This argument's behaviour is overloaded; the shorter word "try"
    # is a python word.
    parser.add_argument("--retry", type=int, metavar="COUNT",
                        help="number of times a test should be attempted before giving up (tests are categorised as not-started (no OUTPUT directory), incomplete, failed, passed); a negative %(metavar)s selects all tests; a zero %(metavar)s selects not-started tests; a positive %(metavar)s selects not-started, incomplete and failing tests; default is to select not-started tests")
    parser.add_argument("--dry-run", "-n", action="store_true")
    parser.add_argument("--verbose", "-v", action="count", default=0)
    parser.add_argument("--output-directory", default=None, metavar="DIRECTORY",
                        help="save test results as %(metavar)s/<test> instead of <test>/OUTPUT")
    parser.add_argument("directories", metavar="DIRECTORY", nargs="+",
                        help="either a testsuite directory or a list of test directories")
    testsuite.add_arguments(parser)
    runner.add_arguments(parser)
    post.add_arguments(parser)
    logutil.add_arguments(parser)

    args = parser.parse_args()
    logutil.config(args)

    logger = logutil.getLogger("kvmrunner")
    logger.info("Options:")
    logger.info("  retry: %s", args.retry or "0 (default)")
    logger.info("  dry-run: %s", args.dry_run)
    logger.info("  output-directory: %s", args.output_directory or "<testsuite>/<test>/OUTPUT (default)")
    logger.info("  directories: %s", args.directories)
    testsuite.log_arguments(logger, args)
    runner.log_arguments(logger, args)
    post.log_arguments(logger, args)
    logutil.log_arguments(logger, args)

    tests = testsuite.load_testsuite_or_tests(logger, args.directories, args,
                                              testsuite_output_directory=args.output_directory,
                                              log_level=logutil.INFO)
    if not tests:
        logger.error("test or testsuite directory invalid: %s", args.directories)
        return 1

    # A list of test directories was specified (i.e, not a testsuite),
    # then force the tests to run.
    if isinstance(tests, list) and args.retry is None:
        args.retry = 1;
        logger.info("Explicit directory list; forcing --retry=%d (retry failed tests)", args.retry)

    # Use a default dict so no need to worry about initializing values
    # to zero.
    stats = Stats()
    results = Results()
    start_time = time.localtime()

    try:
        logger.info("run started at %s", datetime.now())

        test_count = 0
        for test in tests:
            stats.add("total", test)
            test_count += 1
            # Would the number of tests to be [re]run be better?
            test_prefix = "****** %s (test %d of %d)" % (test.name, test_count, len(tests))

            ignore = testsuite.ignore(test, args)
            if ignore:
                stats.add("ignored", test)
                # No need to log all the ignored tests when an
                # explicit sub-set of tests is being run.  For
                # instance, when running just one test.
                if not args.test_name:
                    logger.info("%s: ignore (%s)", test_prefix, ignore)
                continue

            # Implement "--retry" as described above: if retry is -ve,
            # the test is always run; if there's no result, the test
            # is always run; skip passed tests; else things get a
            # little wierd.
            retry = args.retry or 0
            if retry >= 0:
                result = post.mortem(test, args)
                if result:
                    if result.passed:
                        logger.info("%s: passed", test_prefix)
                        stats.add("skipped", test)
                        results.add(result)
                        continue
                    if retry == 0:
                        logger.info("%s: %s (delete '%s' to re-test)", test_prefix,
                                    result, test.output_directory)
                        stats.add("skipped", test)
                        results.add(result)
                        continue
                    stats.add("retry", test)

            logger.info("%s: starting ...", test_prefix)
            stats.add("tests", test)

            debugfile = None
            result = None

            # At least one iteration; above will have filtered out
            # skips and ignores
            attempts = max(abs(retry), 1)
            for attempt in range(attempts):
                stats.add("attempts", test)

                # Create an output directory.  If there's already an
                # existing OUTPUT directory copy its contents to:
                #
                #     OUTPUT/YYYYMMDDHHMMSS.ATTEMPT
                #
                # so, when re-running, earlier attempts are saved.  Do
                # this before the OUTPUT/debug.log is started so that
                # each test attempt has its own log, and otherwise, it
                # too would be moved away.
                saved_output_directory = None
                saved_output = []
                if not args.dry_run:
                    try:
                        os.mkdir(test.output_directory)
                    except FileExistsError:
                        # Include the time this test run started in
                        # the suffix - that way all saved results can
                        # be matched using a wild card.
                        saved_output_directory = os.path.join(test.output_directory,
                                                              "%s.%d" % (time.strftime("%Y%m%d%H%M%S", start_time), attempt))
                        logger.debug("moving existing OUTPUT to '%s'", saved_output_directory)
                        for name in os.listdir(test.output_directory):
                            src = os.path.join(test.output_directory, name)
                            dst = os.path.join(saved_output_directory, name)
                            if os.path.isfile(src):
                                os.makedirs(saved_output_directory, exist_ok=True)
                                os.rename(src, dst)
                                saved_output.append(name)
                                logger.debug("  moved '%s' to '%s'", src, dst)

                # Start a debug log in the OUTPUT directory; include
                # timing for this specific test attempt.
                with logutil.TIMER, logutil.Debug(logger, os.path.join(test.output_directory, "debug.log")):
                    logger.info("****** test %s attempt %d of %d started at %s ******",
                                test.name, attempt+1, attempts, datetime.now())

                    # Add a log message about any saved output
                    # directory to the per-test-attempt debug log.  It
                    # just looks better.
                    if saved_output:
                        logger.info("saved existing '%s' in '%s'", saved_output, saved_output_directory)

                    ending = "undefined"
                    try:
                        if not args.dry_run:
                            runner.run_test(test, max_workers=args.workers)
                        ending = "finished"
                        result = post.mortem(test, args, update=(not args.dry_run))
                        if not args.dry_run:
                            # Store enough to fool the script
                            # pluto-testlist-scan.sh.
                            logger.info("storing result in '%s'", test.result_file)
                            with open(test.result_file, "w") as f:
                                f.write('"result": "%s"\n' % result)
                    except pexpect.TIMEOUT as e:
                        ending = "timeout"
                        logger.exception("**** test %s timed out ****", test.name)
                        result = post.mortem(test, args, update=(not args.dry_run))
                    # Since the OUTPUT directory exists, all paths to
                    # here should have a non-null RESULT.
                    stats.add("attempts(%s:%s)" % (ending, result), test)
                    logger.info("****** test %s %s ******", test.name, result)
                    if result.passed:
                        break

            # Above will have set RESULT (don't reach here during
            # cntrl-c or crash).
            results.add(result)
            stats.add("tests(%s)" % result, test)

    except KeyboardInterrupt:
        logger.exception("**** test %s interrupted ****", test.name)
        return 1

    finally:
        logger.info("run finished at %s", datetime.now())

        level = args.verbose and logutil.INFO or logutil.DEBUG
        logger.log(level, "stat details:")
        stats.log_details(logger, level=level, prefix="  ")

        logger.info("result details:")
        results.log_details(logger, level=logutil.INFO, prefix="  ")

        logger.info("stat summary:")
        stats.log_summary(logger, level=logutil.INFO, prefix="  ")
        logger.info("result summary:")
        results.log_summary(logger, level=logutil.INFO, prefix="  ")

    return 0


if __name__ == "__main__":
    sys.exit(main())
