from pybuilder.core import use_plugin, init

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("pypi:pybuilder_pytest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin('pypi:pybuilder_pytest_coverage')
use_plugin("python.distutils")


name = "pybdemo"
default_task = "publish"


@init
def initialize(project):
    project.build_depends_on('mockito')
    project.get_property('pytest_extra_args').append('-x')
    project.set_property("coverage_break_build", False)
    project.set_property_if_unset("pytest_coverage_break_build_threshold", 30)
