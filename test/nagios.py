#!/usr/bin/env python
##
#
# Copyright 2012 Andy Georges
#
# This file is part of VSC-tools,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# VSC-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
##
"""
Tests for the vsc.utils.nagios module.
"""
import os
import tempfile
import time
import sys

from paycheck import with_checker, irange
from unittest import TestCase, TestLoader, main

from vsc.utils.nagios import NagiosReporter, NAGIOS_EXIT_OK, NAGIOS_EXIT_WARNING, NAGIOS_EXIT_CRITICAL, NAGIOS_EXIT_UNKNOWN


class TestNagios(TestCase):
    """Test for the nagios reporter class."""

    @with_checker(irange(0, 3), str, irange(0, 10))
    def test_cache(self, exit_code, message, threshold):
        """Test the caching mechanism in the reporter."""
        (handle, filename) = tempfile.mkstemp()
        os.unlink(filename)
        reporter = NagiosReporter('test_cache', filename, threshold)

        nagios_exit = [NAGIOS_EXIT_OK, NAGIOS_EXIT_WARNING, NAGIOS_EXIT_CRITICAL, NAGIOS_EXIT_UNKNOWN][exit_code]

        reporter.cache(nagios_exit, message)

        (handle, output_filename) = tempfile.mkstemp()
        os.close(handle)

        try:
            time.sleep(threshold + 1)
            old_stdout = sys.stdout
            sys.stdout = os.open(output_filename, 'w')
            reporter_test = NagiosReporter('test_cache', filename, threshold)
            reporter_test.report_and_exit()
        except SystemExit, err:
            sys.stdout.close()
            sys.stdout = old_stdout
            self.assertTrue(err.code == nagios_exit[0])
            output_file = os.open(output_filename, 'r')
            line = output_file.read().rstrip()
            self.assertTrue(line == "%s %s" % (nagios_exit[1], message))


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestNagios)


if __name__ == '__main__':
    main()  # unittest.main
