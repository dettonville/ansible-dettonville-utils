from __future__ import absolute_import, division, print_function
__metaclass__ = type

# ref: https://github.com/kyrus/python-junit-xml
import os
import sys
import re
import codecs
import logging
import warnings

from collections import defaultdict
#from collections import OrderedDict

from glob import glob

import xml.etree.ElementTree as ET
import xml.dom.minidom

from functools import singledispatchmethod

# ref: https://stackoverflow.com/questions/47382227/python-yaml-update-preserving-order-and-comments
# ref: https://github.com/ansible/ansible/issues/74383#issuecomment-824884558
# ref: https://docs.ansible.com/ansible-core/devel/dev_guide/testing/sanity/import.html#import
try:
    from ruamel.yaml import YAML
    import ruamel.yaml
except ImportError as imp_exc:
    YAML_IMPORT_ERROR = imp_exc
else:
    YAML_IMPORT_ERROR = None

from ansible.module_utils.six import u, iteritems, PY2

# noinspection PyUnresolvedReferences
from ansible_collections.dettonville.utils.plugins.module_utils.utils \
    import PrettyLog

yaml = ruamel.yaml.YAML()

# prevent line wrapping since different versions handle it differently leading to test compare results issues
# make large using big enough value to prevent line-wrap
# ref: https://stackoverflow.com/questions/42170709/prevent-long-lines-getting-wrapped-in-ruamel-yaml
yaml.width = 4096

CM = ruamel.yaml.comments.CommentedMap

unichr = chr

_LOGLEVEL_DEFAULT = "INFO"


# try:
#     # Python 2
#     unichr
# except NameError:  # pragma: nocover
#     # Python 3
#     unichr = chr

# ref: https://github.com/testmoapp/junitxml
"""
Based on the specification for JUnit XML files.

<?xml version="1.0" encoding="utf-8"?>
<testsuites errors="1" failures="1" tests="4" time="45">
    <testsuite errors="1" failures="1" hostname="localhost" id="0" name="test1"
               package="testdb" tests="4" timestamp="2012-11-15T01:02:29">
        <properties>
            <property name="assert-passed" value="1"/>
        </properties>
        <testcase classname="testdb.directory" name="1-passed-test" time="10"/>
        <testcase classname="testdb.directory" name="2-failed-test" time="20">
            <failure message="Assertion FAILED: failed assert" type="failure">
                the output of the testcase
            </failure>
        </testcase>
        <testcase classname="package.directory" name="3-errord-test" time="15">
            <error message="Assertion ERROR: error assert" type="error">
                the output of the testcase
            </error>
        </testcase>
        <testcase classname="package.directory" name="3-skipped-test" time="0">
            <skipped message="SKIPPED Test" type="skipped">
                the output of the testcase
            </skipped>
        </testcase>
        <testcase classname="testdb.directory" name="3-passed-test" time="10">
            <system-out>
                I am system output
            </system-out>
            <system-err>
                I am the error output
            </system-err>
        </testcase>
    </testsuite>
</testsuites>
"""


def decode(var, encoding):
    """
    If not already unicode, decode it.
    """
    if PY2:
        if isinstance(var, unicode):  # noqa: F821
            ret = var
        elif isinstance(var, str):
            if encoding:
                ret = var.decode(encoding)
            else:
                ret = unicode(var)  # noqa: F821
        else:
            ret = unicode(var)  # noqa: F821
    else:
        ret = str(var)
    return ret


# ref: https://stackoverflow.com/questions/40226610/ruamel-yaml-equivalent-of-sort-keys
def yaml_sort_keys(data, level: int = 0, reverse_sort: str = False):
    log_prefix = "yaml_sort_keys(level=%s):" % level

    logging.debug("%s type(data)=%s" % (log_prefix, type(data)))

    # ref: https://stackoverflow.com/questions/33311258/python-check-if-variable-isinstance-of-any-type-in-list
    if isinstance(data, (TestSuites, TestSuite)):
        if isinstance(data, TestSuites):
            res = TestSuites()
        if isinstance(data, TestSuite):
            res = TestSuite(name=data.name)
        if isinstance(data, dict):
            res = dict()

        sorted_keys = sorted(list(data.keys()))
        if reverse_sort:
            sorted_keys = reversed(sorted_keys)

        for key in sorted_keys:
            logging.debug("%s sorting %s" % (log_prefix, key))
            res[key] = yaml_sort_keys(data[key], level=level+1, reverse_sort=reverse_sort)
        return res
    if isinstance(data, list):
        for idx, elem in enumerate(data):
            logging.debug("%s sorting %s" % (log_prefix, PrettyLog(elem)))
            data[idx] = yaml_sort_keys(elem, level=level+1, reverse_sort=reverse_sort)
    return data


def xml_get_node_key(node: ET.Element, attr: dict = None):
    """Return the sorting key of an xml node
    using tag and attributes
    """
    if attr is None:
        return '%s' % node.tag + ':'.join([node.get(attr)
                                        for attr in sorted(node.attrib)])
    if attr in node.attrib:
        return '%s:%s' % (node.tag, node.get(attr))
    return '%s' % node.tag


# ref: https://stackoverflow.com/questions/25338817/sorting-xml-in-python-etree
def xml_sort_children(node: ET.Element, attr: dict = None):
    """ Sort children along tag and given attribute.
    if attr is None, sort along all attributes"""
    if not isinstance(node.tag, str):  # PYTHON 2: use basestring instead
        # not a TAG, it is comment or DATA
        # no need to sort
        return
    # sort child along attr
    node[:] = sorted(node, key=lambda child: xml_get_node_key(child, attr))
    # and recurse
    for child in node:
        xml_sort_children(child, attr)


# ref: https://yaml.readthedocs.io/en/latest/
# ref: https://matthewpburruss.com/post/yaml/
# ref: https://stackoverflow.com/questions/54378220/declare-data-type-to-ruamel-yaml-so-that-it-can-represent-serialize-it
@yaml.register_class
class TestCase(object):
    """A JUnit test case with a result and possibly some stdout or stderr"""

    def __init__(
        self,
        name,
        classname=None,
        elapsed_sec=None,
        stdout=None,
        stderr=None,
        assertions=None,
        timestamp=None,
        status=None,
        category=None,
        file=None,
        line=None,
        log=None,
        url=None,
        allow_multiple_subelements=False,
    ):
        self.name = name
        self.assertions = assertions
        self.elapsed_sec = elapsed_sec
        self.timestamp = timestamp
        self.classname = classname
        self.status = status
        self.category = category
        self.file = file
        self.line = line
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr

        self.is_enabled = True
        self.properties = {}
        self.errors = []
        self.failures = []
        self.skipped = []
        self.allow_multiple_subelements = allow_multiple_subelements

    # ref: https://yaml.readthedocs.io/en/latest/dumpcls/#dumping-python-classes
    def __repr__(self):
        return f'''{self.__class__.__name__}(name: {self.name}, 
            assertions: {self.assertions}, 
            errors: {self.errors}, 
            failures: {self.failures}, 
            skipped: {self.skipped})'''

    @classmethod
    def from_yaml(cls, constructor, node):
        test_case = TestCase(name='')
        yield test_case
        data = ruamel.yaml.CommentedMap()
        constructor.construct_mapping(node, maptyp=data, deep=True)
        for k, v in data.items():
            setattr(test_case, k, v)

    def add_error_info(self, message=None, output=None, error_type=None):
        """Adds an error message, output, or both to the test case"""
        error = dict(
            message=message,
            output=output,
            type=error_type
        )
        # error = {}
        # error["message"] = message
        # error["output"] = output
        # error["type"] = error_type
        if self.allow_multiple_subelements:
            if message or output:
                self.errors.append(error)
        elif not len(self.errors):
            self.errors.append(error)
        else:
            if message:
                self.errors[0]["message"] = message
            if output:
                self.errors[0]["output"] = output
            if error_type:
                self.errors[0]["type"] = error_type

    def add_failure_info(self, message=None, output=None, failure_type=None):
        """Adds a failure message, output, or both to the test case"""
        failure = dict(
            message=message,
            output=output,
            type=failure_type
        )
        # failure = {}
        # failure["message"] = message
        # failure["output"] = output
        # failure["type"] = failure_type
        if self.allow_multiple_subelements:
            if message or output:
                self.failures.append(failure)
        elif not len(self.failures):
            self.failures.append(failure)
        else:
            if message:
                self.failures[0]["message"] = message
            if output:
                self.failures[0]["output"] = output
            if failure_type:
                self.failures[0]["type"] = failure_type

    def add_skipped_info(self, message=None, output=None):
        """Adds a skipped message, output, or both to the test case"""
        skipped = dict(
            message=message,
            output=output
        )
        # skipped = {}
        # skipped["message"] = message
        # skipped["output"] = output
        if self.allow_multiple_subelements:
            if message or output:
                self.skipped.append(skipped)
        elif not len(self.skipped):
            self.skipped.append(skipped)
        else:
            if message:
                self.skipped[0]["message"] = message
            if output:
                self.skipped[0]["output"] = output

    def is_failure(self):
        """returns true if this test case is a failure"""
        return sum(1 for f in self.failures if f["message"] or f["output"]) > 0

    def is_error(self):
        """returns true if this test case is an error"""
        return sum(1 for e in self.errors if e["message"] or e["output"]) > 0

    def is_skipped(self):
        """returns true if this test case has been skipped"""
        return len(self.skipped) > 0


@yaml.register_class
class TestSuite(object):
    """
    Suite of test cases.
    Can handle unicode strings or binary strings if their encoding is provided.
    """

    def __init__(
        self,
        name,
        test_cases=None,
        hostname=None,
        id=None,
        package=None,
        timestamp=None,
        properties=None,
        file=None,
        log=None,
        url=None,
        stdout=None,
        stderr=None,
    ):
        self.name = name
        if not test_cases:
            test_cases = dict()
        try:
            type(test_cases) is dict
        except TypeError:
            raise TypeError("test_cases must be a dict of test cases {test_case_id: test_case}")
        # if not test_cases:
        #     test_cases = OrderedDict()
        # try:
        #     type(test_cases) is OrderedDict
        # except TypeError:
        #     raise TypeError("test_cases must be a OrderedDict of test cases {test_case_id: test_case}")
        self.test_cases = test_cases
        self.timestamp = timestamp
        self.hostname = hostname
        self.id = id
        self.package = package
        self.file = file
        self.log = log
        self.url = url
        self.stdout = stdout
        self.stderr = stderr
        self.properties = properties

    # ref: https://yaml.readthedocs.io/en/latest/dumpcls/#dumping-python-classes
    def __repr__(self):
        return f'''{self.__class__.__name__}(name: {self.name}, 
            test_cases: {self.test_cases}, 
            properties: {self.properties}, 
            stdout: {self.stdout}, 
            stderr: {self.stderr})'''

    # ref: https://stackoverflow.com/questions/43627405/understanding-getitem-method-in-python#43627975
    def __setitem__(self, test_case_id: str, test_case: TestCase):
        log_prefix = "%s.__setitem__(%s):" % (self.__class__.__name__, test_case_id)
        logging.debug("%s SET %s" % (log_prefix, PrettyLog(test_case)))
        return self.test_cases.update({ test_case_id: test_case })

    def __getitem__(self, test_case_id: str) -> TestCase:
        log_prefix = "%s.__getitem__(%s):" % (self.__class__.__name__, test_case_id)
        test_case: TestCase = self.test_cases[test_case_id]
        logging.debug("%s GET %s" % (log_prefix, PrettyLog(test_case)))
        return test_case

    def keys(self):
        return self.test_cases.keys()

    @classmethod
    def from_yaml(cls, constructor, node):
        test_suite = TestSuite(name='')
        yield test_suite
        data = ruamel.yaml.CommentedMap()
        constructor.construct_mapping(node, maptyp=data, deep=True)
        for k, v in data.items():
            setattr(test_suite, k, v)

    def build_xml_doc(self, encoding=None) -> ET.Element:
        """
        Builds the XML document for the JUnit test suite.
        Produces clean unicode strings and decodes non-unicode with the help of encoding.
        @param encoding: Used to decode encoded strings.
        @return: XML document with unicode string elements
        """

        # build the test suite element
        test_suite_attributes = dict()
        if any(c.assertions for c in self.test_cases.values()):
            test_suite_attributes["assertions"] = str(sum([int(c.assertions) for c in self.test_cases.values() if c.assertions]))
        test_suite_attributes["disabled"] = str(len([c for c in self.test_cases.values() if not c.is_enabled]))
        test_suite_attributes["errors"] = str(len([c for c in self.test_cases.values() if c.is_error()]))
        test_suite_attributes["failures"] = str(len([c for c in self.test_cases.values() if c.is_failure()]))
        test_suite_attributes["name"] = decode(self.name, encoding)
        test_suite_attributes["skipped"] = str(len([c for c in self.test_cases.values() if c.is_skipped()]))
        test_suite_attributes["tests"] = str(len(self.test_cases))
        test_suite_attributes["time"] = str(sum(c.elapsed_sec for c in self.test_cases.values() if c.elapsed_sec))

        if self.hostname:
            test_suite_attributes["hostname"] = decode(self.hostname, encoding)
        if self.id:
            test_suite_attributes["id"] = decode(self.id, encoding)
        if self.package:
            test_suite_attributes["package"] = decode(self.package, encoding)
        if self.timestamp:
            test_suite_attributes["timestamp"] = decode(self.timestamp, encoding)
        if self.file:
            test_suite_attributes["file"] = decode(self.file, encoding)
        if self.log:
            test_suite_attributes["log"] = decode(self.log, encoding)
        if self.url:
            test_suite_attributes["url"] = decode(self.url, encoding)

        xml_element = ET.Element("testsuite", test_suite_attributes)

        # add any properties
        if self.properties:
            props_element = ET.SubElement(xml_element, "properties")
            for k, v in self.properties.items():
                attrs = dict(
                    name=decode(k, encoding),
                    value=decode(v, encoding)
                )
                # attrs = {"name": decode(k, encoding), "value": decode(v, encoding)}
                ET.SubElement(props_element, "property", attrs)

        # add test suite stdout
        if self.stdout:
            stdout_element = ET.SubElement(xml_element, "system-out")
            stdout_element.text = decode(self.stdout, encoding)

        # add test suite stderr
        if self.stderr:
            stderr_element = ET.SubElement(xml_element, "system-err")
            stderr_element.text = decode(self.stderr, encoding)

        # test cases
        for _test_case in self.test_cases.values():
            test_case_attributes = dict()
            test_case_attributes["name"] = decode(_test_case.name, encoding)
            if _test_case.assertions:
                # Number of assertions in the test case
                test_case_attributes["assertions"] = "%d" % _test_case.assertions
            if _test_case.elapsed_sec:
                test_case_attributes["time"] = "%f" % _test_case.elapsed_sec
            if _test_case.timestamp:
                test_case_attributes["timestamp"] = decode(_test_case.timestamp, encoding)
            if _test_case.classname:
                test_case_attributes["classname"] = decode(_test_case.classname, encoding)
            if _test_case.status:
                test_case_attributes["status"] = decode(_test_case.status, encoding)
            if _test_case.category:
                test_case_attributes["class"] = decode(_test_case.category, encoding)
            if _test_case.file:
                test_case_attributes["file"] = decode(_test_case.file, encoding)
            if _test_case.line:
                test_case_attributes["line"] = decode(_test_case.line, encoding)
            if _test_case.log:
                test_case_attributes["log"] = decode(_test_case.log, encoding)
            if _test_case.url:
                test_case_attributes["url"] = decode(_test_case.url, encoding)

            test_case_element = ET.SubElement(xml_element, "testcase", test_case_attributes)

            # add any properties
            if _test_case.properties:
                props_element = ET.SubElement(test_case_element, "properties")
                for k, v in _test_case.properties.items():
                    attrs = dict(
                        name=decode(k, encoding),
                        value=decode(v, encoding)
                    )
                    # attrs = {"name": decode(k, encoding), "value": decode(v, encoding)}
                    ET.SubElement(props_element, "property", attrs)


            # failures
            for failure in _test_case.failures:
                if failure["output"] or failure["message"]:
                    attrs = dict(type="failure")
                    # attrs = {"type": "failure"}
                    if failure["message"]:
                        attrs["message"] = decode(failure["message"], encoding)
                    if failure["type"]:
                        attrs["type"] = decode(failure["type"], encoding)
                    failure_element = ET.Element("failure", attrs)
                    if failure["output"]:
                        failure_element.text = decode(failure["output"], encoding)
                    test_case_element.append(failure_element)

            # errors
            for error in _test_case.errors:
                if error["message"] or error["output"]:
                    attrs = dict(type="error")
                    # attrs = {"type": "error"}
                    if error["message"]:
                        attrs["message"] = decode(error["message"], encoding)
                    if error["type"]:
                        attrs["type"] = decode(error["type"], encoding)
                    error_element = ET.Element("error", attrs)
                    if error["output"]:
                        error_element.text = decode(error["output"], encoding)
                    test_case_element.append(error_element)

            # skippeds
            for skipped in _test_case.skipped:
                attrs = dict(type="skipped")
                # attrs = {"type": "skipped"}
                if skipped["message"]:
                    attrs["message"] = decode(skipped["message"], encoding)
                skipped_element = ET.Element("skipped", attrs)
                if skipped["output"]:
                    skipped_element.text = decode(skipped["output"], encoding)
                test_case_element.append(skipped_element)

            # test stdout
            if _test_case.stdout:
                stdout_element = ET.Element("system-out")
                stdout_element.text = decode(_test_case.stdout, encoding)
                test_case_element.append(stdout_element)

            # test stderr
            if _test_case.stderr:
                stderr_element = ET.Element("system-err")
                stderr_element.text = decode(_test_case.stderr, encoding)
                test_case_element.append(stderr_element)

        return xml_element

    @staticmethod
    def to_xml_string(test_suites, prettyprint=True, encoding=None):
        """
        Returns the string representation of the JUnit XML document.
        @param encoding: The encoding of the input.
        @return: unicode string
        """
        warnings.warn(
            "Testsuite.to_xml_string is deprecated. It will be removed in version 2.0.0. "
            "Use function to_xml_report_string",
            DeprecationWarning,
        )
        return to_xml_report_string(test_suites, prettyprint, encoding)

    def update(self, test_case: TestCase):
        log_prefix = "%s.update():" % self.__class__.__name__
        return self.test_cases.update({ test_case.name: test_case })


# ref: https://stackoverflow.com/questions/2390827/how-to-properly-subclass-dict-and-override-getitem-setitem
@yaml.register_class
class TestSuitesBase(object):
    """
    Dictionary of TestSuites.
    """

    # ref: https://realpython.com/python-multiple-constructors/#a-real-world-example-of-a-single-dispatch-method
    # ref: https://realpython.com/python-multiple-constructors/
    @singledispatchmethod
    def __init__(
        self,
        test_suites=None
    ):
        log_prefix = "%s.__init__(%s):" % (self.__class__.__name__, type(test_suites))
        logging.info("%s unsupported test_suites type: %s" % (log_prefix, type(test_suites)))
        raise ValueError(f"unsupported test_suites type: {type(test_suites)}")

    # https://realpython.com/python-multiple-constructors/
    @__init__.register(object)
    def _from_object(self, obj):
        log_prefix = "%s._from_object(%s):" % (self.__class__.__name__, type(obj))
        logging.debug("%s test_suites type: %s not handled - so initialized to default empty dict" %
                      (log_prefix, type(obj)))
        # self.test_suites = OrderedDict()
        self.test_suites = dict()

    # https://realpython.com/python-multiple-constructors/
    @__init__.register(list)
    def _from_list(self, test_suites_list: list[TestSuite]):
        log_prefix = "%s._from_list(%s):" % (self.__class__.__name__, type(test_suites))
        logging.debug("%s test_suites type: initialize with specified list" % log_prefix)
        # self.test_suites = OrderedDict()
        self.test_suites = dict()
        if test_suites_list:
            for test_suite in test_suites_list:
                self.test_suites.update({ test_suite.name: test_suite })

    # ref: https://stackoverflow.com/questions/2390827/how-to-properly-subclass-dict-and-override-getitem-setitem
    # ref: https://yaml.readthedocs.io/en/latest/dumpcls/#dumping-python-classes
    def __repr__(self):
        # ref: https://realpython.com/python-multiple-constructors/#building-a-polar-point-from-cartesian-coordinates
        return f'{self.__class__.__name__}({self.test_suites})'
        # return (
        #     f"{self.__class__.__name__}"
        #     f'{self.test_suites}'
        # )
        # return f'TestSuites(suites: {self.test_suites})'

    # make class iterable over the self.test_suites dict
    # ref: https://stackoverflow.com/questions/5434400/python-make-class-iterable#5434478
    def __iter__(self):
        for each in self.test_suites.values():
            yield each

    def keys(self):
        return self.test_suites.keys()

    # ref: https://stackoverflow.com/questions/43627405/understanding-getitem-method-in-python#43627975
    def __setitem__(self, test_suite_id: str, test_suite: TestSuite):
        log_prefix = "%s.__setitem__(%s):" % (self.__class__.__name__, test_suite_id)
        logging.debug("%s SET %s" % (log_prefix, PrettyLog(test_suite)))
        return self.test_suites.update({ test_suite_id: test_suite })

    def __getitem__(self, test_suite_id: str) -> TestSuite:
        log_prefix = "%s.__getitem__(%s):" % (self.__class__.__name__, test_suite_id)
        test_suite: TestSuite = self.test_suites[test_suite_id]
        logging.debug("%s GET %s" % (log_prefix, PrettyLog(test_suite)))
        return test_suite

    @classmethod
    def from_yaml(cls, constructor, node):
        test_suites = TestSuites()
        yield test_suites
        data = ruamel.yaml.CommentedMap()
        constructor.construct_mapping(node, maptyp=data, deep=True)
        for k, v in data.items():
            setattr(test_suites, k, v)

    def update(self, test_suite: TestSuite):
        log_prefix = "%s.update():" % self.__class__.__name__
        return self.test_suites.update({ test_suite.name: test_suite })

    def to_xml_report_string(self, prettyprint: bool = True, encoding: str = None, sort_attr: str = 'name'):
        log_prefix = "%s.to_xml_report_string():" % self.__class__.__name__

        xml_element = ET.Element("testsuites")
        attributes = defaultdict(int)

        for ts in self.test_suites.values():
            logging.debug("%s ts=%s" % (log_prefix, PrettyLog(ts)))
            logging.debug("%s type(ts) %s" % (log_prefix, type(ts)))
            ts_xml = ts.build_xml_doc(encoding=encoding)
            # for key in ["disabled", "errors", "failures", "tests"]:
            for key in ["assertions", "disabled", "errors", "failures", "skipped", "tests"]:
                attributes[key] += int(ts_xml.get(key, 0))
            for key in ["time"]:
                attributes[key] += float(ts_xml.get(key, 0))
            xml_element.append(ts_xml)
        for key, value in iteritems(attributes):
            xml_element.set(key, str(value))

        if sort_attr:
            # sort the xml doc by attr='name'
            # ref: https://stackoverflow.com/questions/25338817/sorting-xml-in-python-etree
            xml_sort_children(xml_element, attr=sort_attr)

        xml_string = ET.tostring(xml_element, encoding=encoding)
        # is encoded now
        xml_string = _clean_illegal_xml_chars(xml_string.decode(encoding or "utf-8"))
        # is unicode now

        if prettyprint:
            # minidom.parseString() works just on correctly encoded binary strings
            xml_string = xml_string.encode(encoding or "utf-8")
            xml_string = xml.dom.minidom.parseString(xml_string)
            # toprettyxml() produces unicode if no encoding is being passed or binary string with an encoding
            xml_string = xml_string.toprettyxml(encoding=encoding)
            if encoding:
                xml_string = xml_string.decode(encoding)
            # is unicode now
        return xml_string


@yaml.register_class
class TestSuites(TestSuitesBase):
    """
    Dictionary of TestSuites.
    """

    # ref: https://realpython.com/python-multiple-constructors/#a-real-world-example-of-a-single-dispatch-method
    # ref: https://realpython.com/python-multiple-constructors/
    def __init__(
        self,
        test_suites=None
    ):
        log_prefix = "%s.__init__(%s):" % (self.__class__.__name__, type(test_suites))
        logging.info("%s test_suites type: %s" % (log_prefix, type(test_suites)))
        if test_suites:
            logging.info("%s invoking super.init() for test_suites type: %s" % (log_prefix, type(test_suites)))
            # ref: https://stackoverflow.com/questions/3472853/python-sub-class-initialiser
            super(TestSuite, self).__init__(test_suites)
        else:
            logging.info("%s setting test_suites to empty dict" % log_prefix)
            # self.test_suites = OrderedDict()
            self.test_suites = dict()


# def to_xml_report_string(test_suites: list[TestSuite], prettyprint: bool=True, encoding: str=None):
def to_xml_report_string(test_suites, prettyprint=True, encoding=None):

    try:
        type(test_suites) is dict
    except TypeError:
        raise TypeError("test_suites must be a dict of test suites {test_suite_id: test_suite}")

    return test_suites.to_xml_report_string(prettyprint=prettyprint, encoding=encoding)


def to_xml_report_file(file_descriptor, test_suites, prettyprint=True, encoding=None):
    """
    Writes the JUnit XML document to a file.
    """
    xml_string = to_xml_report_string(test_suites, prettyprint=prettyprint, encoding=encoding)
    # has problems with encoded str with non-ASCII (non-default-encoding) characters!
    file_descriptor.write(xml_string)


def _clean_illegal_xml_chars(string_to_clean):
    """
    Removes any illegal unicode characters from the given XML string.

    @see: http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
    """

    illegal_unichrs = [
        (0x00, 0x08),
        (0x0B, 0x1F),
        (0x7F, 0x84),
        (0x86, 0x9F),
        (0xD800, 0xDFFF),
        (0xFDD0, 0xFDDF),
        (0xFFFE, 0xFFFF),
        (0x1FFFE, 0x1FFFF),
        (0x2FFFE, 0x2FFFF),
        (0x3FFFE, 0x3FFFF),
        (0x4FFFE, 0x4FFFF),
        (0x5FFFE, 0x5FFFF),
        (0x6FFFE, 0x6FFFF),
        (0x7FFFE, 0x7FFFF),
        (0x8FFFE, 0x8FFFF),
        (0x9FFFE, 0x9FFFF),
        (0xAFFFE, 0xAFFFF),
        (0xBFFFE, 0xBFFFF),
        (0xCFFFE, 0xCFFFF),
        (0xDFFFE, 0xDFFFF),
        (0xEFFFE, 0xEFFFF),
        (0xFFFFE, 0xFFFFF),
        (0x10FFFE, 0x10FFFF),
    ]

    illegal_ranges = ["%s-%s" % (unichr(low), unichr(high)) for (low, high) in illegal_unichrs if low < sys.maxunicode]

    illegal_xml_re = re.compile(u("[%s]") % u("").join(illegal_ranges))
    return illegal_xml_re.sub("", string_to_clean)


class TestResultsLogger:

    def __init__(self, module):
        self.module = module
        self.module_name = module._name
        self.module_fqcn = self.module_name.rsplit('.', 1)[0]

        log_prefix = "%s.init():" % self.__class__.__name__
        self.loglevel = self.module.params.get('logging_level') or _LOGLEVEL_DEFAULT
        logging.basicConfig(
            level=self.loglevel
        )
        self.log = logging.getLogger()

        # self.log.info("%s loglevel=%s" % (log_prefix, self.loglevel))
        self.log.debug("%s loglevel=%s" % (log_prefix, self.loglevel))

        self.log.debug("%s module_name => %s" % (log_prefix, self.module_name))
        self.log.debug("%s module_fqcn => %s" % (log_prefix, self.module_fqcn))

        self.test_junit_report_file = self.module.params.get('test_junit_report_file') or _LOGLEVEL_DEFAULT

        # ref: https://www.tutorialexample.com/fix-python-logging-module-not-writing-to-file-python-tutorial/
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        #        console = self.log.StreamHandler()
        #        console.setLevel(self.loglevel)
        #        # add the handler to the root logger
        #        self.log.getLogger().addHandler(console)

        logging.basicConfig(
            level=self.loglevel,
            stream=sys.stdout
        )
        self.log = logging.getLogger()

        self.test_case_base_dir = self.module.params.get('test_case_base_dir')
        self.test_case_file_prefix = self.module.params.get('test_case_file_prefix')
        self.test_results_dir = self.module.params.get('test_results_dir')
        self.test_results_file = self.module.params.get('test_results_file')
        self.test_junit_report_file = self.module.params.get('test_junit_report_file')

        self.log.info("%s self.test_case_base_dir => %s" % (log_prefix, self.test_case_base_dir))
        self.log.info("%s self.test_case_file_prefix => %s" % (log_prefix, self.test_case_file_prefix))
        self.log.info("%s self.test_results_dir => %s" % (log_prefix, self.test_results_dir))
        self.log.info("%s self.test_results_file => %s" % (log_prefix, self.test_results_file))
        self.log.info("%s self.test_junit_report_file => %s" % (log_prefix, self.test_junit_report_file))

        self.test_suites = self.init_test_suites()

    def init_test_suites(self):
        log_prefix = "%s.init_test_suites():" % self.__class__.__name__

        if not os.path.exists(self.test_case_base_dir):
            self.module.fail_json(rc=257, msg='test_case_base_dir directory %s does not exist!' % self.test_case_base_dir)

        if not os.path.exists(self.test_results_dir):
            try:
                os.mkdir(self.test_results_dir)
            except OSError as e:
                self.module.fail_json(
                    status_code=-1,
                    msg=("%s Error occurred.\n*** when attempting to create test_results_dir=%s\n%s"
                        % (log_prefix, self.test_results_dir, to_text(e))),
                )

        self.test_suite_list = self.module.params.get('test_suite_list')
        self.test_case_file_regex = self.module.params.get('test_case_file_regex')
        self.test_case_id_capture_regex = self.module.params.get('test_case_id_capture_regex')

        if not self.test_case_file_regex:
            self.test_case_file_regex = "%s*.yml" % self.test_case_file_prefix

        if not self.test_case_id_capture_regex:
            self.test_case_id_capture_regex = "%s(.*?).yml" % self.test_case_file_prefix

        if not self.test_suite_list:
            self.test_suite_list = [f.name for f in os.scandir(self.test_case_base_dir) if f.is_dir()]

        logging.debug("%s test_suite_list=%s" % (log_prefix, self.test_suite_list))

        logging.debug("%s test_case_file_regex=%s" % (log_prefix, self.test_case_file_regex))

        # test_suites: dict[str, TestSuite] = dict()
        test_suites: TestSuites = TestSuites()
        for test_suite_id in self.test_suite_list:
            test_suite = TestSuite(test_suite_id)
            #test_suite_vars_dir = os.path.join(self.test_case_base_dir, test_suite_id)
            test_suite_vars_dir = os.path.join(self.test_case_base_dir, test_suite_id, '**')
            logging.debug("%s test_suite_vars_dir=%s" % (log_prefix, test_suite_vars_dir))

            # ref: https://stackoverflow.com/questions/2186525/how-to-use-to-find-files-recursively#2186565
            test_var_files = list(glob(os.path.join(test_suite_vars_dir, self.test_case_file_regex), recursive=True))
            logging.debug("%s test_var_files=%s" % (log_prefix, PrettyLog(test_var_files)))

            for test_case_file in test_var_files:
                logging.debug("%s test_case_file=%s" % (log_prefix, test_case_file))
                test_case_id = re.findall(self.test_case_id_capture_regex, str(test_case_file))[0]
                logging.debug("%s test_case_id=%s" % (log_prefix, test_case_id))

                test_case = TestCase(name=test_case_id,
                                     classname=test_suite_id)
                test_case.add_skipped_info(output="test_suite_id:test_case_id=%s:%s skipped"
                                                  % (test_suite_id, test_case_id))

                test_suite.update(test_case)

            logging.debug("%s test_suite=%s" % (log_prefix, PrettyLog(test_suite)))
            test_suites.update(test_suite)

        logging.debug("%s test_suites=%s" % (log_prefix, PrettyLog(test_suites)))
        return test_suites

    def update_test_results(self, test_results: dict) -> dict[bool, bool]:
        log_prefix = "%s.update_test_results():" % self.__class__.__name__

        if test_results:
            self.log.debug("%s test_results=%s" % (log_prefix, PrettyLog(test_results)))
            for test_suite_id, test_suite_data in test_results['test_suites'].items():
                test_cases = test_suite_data['test_cases']

                # test_suite = self.test_suites.get(test_suite_id)
                # ref:
                test_suite = self.test_suites[test_suite_id]
                if 'properties' in test_suite_data:
                    test_suite_properties = test_suite_data['properties']
                    test_suite.properties = test_suite_properties

                for test_case_id, test_case_data in test_cases.items():
                    test_case = TestCase(name=test_case_id,
                                         classname=test_suite_id)

                    if 'properties' in test_case_data:
                        test_case_properties = test_case_data['properties']
                        test_case.properties = test_case_properties

                        if 'test_job_link' in test_case_properties:
                            if test_case_properties['test_job_link']:
                                test_case.url = test_case_properties['test_job_link']

                        if 'assertions' in test_case_properties:
                            test_case_assertions = test_case_properties['assertions']
                            test_case.assertions = len(test_case_assertions.keys())

                            for test_case_assertion_id, test_case_assertion in test_case_assertions.items():
                                self.log.debug("%s test_case_assertion=%s" % (log_prefix, PrettyLog(test_case_assertion)))
                                if test_case_assertion['failed']:
                                    test_assertion_failed_msg = ("%s: %s" %
                                                                 (test_case_assertion_id, test_case_assertion))
                                    test_case.add_failure_info(output=test_assertion_failed_msg)

                    if 'failures' in test_case_data:
                        test_case.add_failure_info(output=test_case_data['failures'])
                    if 'errors' in test_case_data:
                        test_case.add_error_info(output=test_case_data['errors'])
                    if 'skipped' in test_case_data:
                        test_case.add_skipped_info(output=test_case_data['skipped'])

                    self.log.debug("%s update test_suite with test_case" % log_prefix)
                    test_suite.update(test_case)

                # self.test_suites.update(test_suite)
                self.log.debug("%s update self.test_suites with test_suite" % log_prefix)
                self.test_suites.update(test_suite)

        self.log.debug("%s self.test_suites=%s" % (log_prefix, PrettyLog(self.test_suites)))

        result = self.dump_yaml()
        self.log.debug("%s finished" % log_prefix)

        return result

    def dump_junit(self, prettyprint=True, encoding=None) -> dict[bool, bool]:
        log_prefix = "%s.dump_junit():" % self.__class__.__name__

        result = dict(
            changed=True,
            failed=False,
            message=''
        )

        self.log.debug('%s prettyprint=%s, encoding=%s' % (log_prefix, prettyprint, encoding))

        try:
            test_junit_report_file_path = os.path.join(self.test_results_dir, self.test_junit_report_file)
            with codecs.open(test_junit_report_file_path, mode="w", encoding=encoding) as f:
                to_xml_report_file(f, self.test_suites, prettyprint=prettyprint, encoding=encoding)
        except IOError:
            self.module.fail_json(msg="Unable to create file %s", traceback=traceback.format_exc())

        result['message'] = "The test results file has been created successfully at %s" % test_junit_report_file_path

        return result

    def dump_yaml(self, encoding=None, sort_keys=True):
        log_prefix = "%s.dump_yaml():" % self.__class__.__name__
        result = dict(
            changed=True,
            failed=False,
            message=''
        )

        self.log.debug('%s encoding=%s, sort_keys=%s' % (log_prefix, encoding, sort_keys))

        test_results_file_path = os.path.join(self.test_results_dir, self.test_results_file)

        self.log.debug("%s yaml dump=%s" % (log_prefix, test_results_file_path))
        try:
            with codecs.open(test_results_file_path, mode="w", encoding=encoding) as f:
                if sort_keys:
                    self.log.debug("%s sorting keys" % log_prefix)
                    yaml.dump(yaml_sort_keys(self.test_suites), f)
                else:
                    yaml.dump(self.test_suites, f)
        except IOError:
            self.module.fail_json(msg="Unable to create file %s", traceback=traceback.format_exc())

        result['message'] = "The test results file has been created successfully at %s" % test_results_file_path

        return result
