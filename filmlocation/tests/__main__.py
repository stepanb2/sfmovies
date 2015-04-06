import sys
import unittest

import filmlocation.tests.AllTests


def main(argv):
    unittest.main(module=filmlocation.tests.AllTests, argv=argv)

if __name__ == "__main__":
    main(sys.argv)