import setuptools
import textwrap
import subprocess
import shutil
import os.path

version = "0.0.1"


if __name__ == "__main__":
    setuptools.setup(
        name="PyFilmLocation",
        version=version,
        description="Use the film locations lib.",
        author="Stepan B.",
        url="http://github.com/stepanb2/sfmovies",
        long_description=textwrap.dedent("""\
            Short Tutorial
            =====================
            """),
        packages=[
            "filmlocation",
            "filmlocation.tests",
        ],

        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Web Environment",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.5",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Topic :: Software Development",
        ],
        test_suite="filmlocation.tests.AllTests",
        use_2to3=True
    )