# ==================================================================================================================== #
#            _     _                                           _                                                       #
#  ___ _ __ | |__ (_)_ __ __  __     _ __ ___ _ __   ___  _ __| |_ ___                                                 #
# / __| '_ \| '_ \| | '_ \\ \/ /____| '__/ _ \ '_ \ / _ \| '__| __/ __|                                                #
# \__ \ |_) | | | | | | | |>  <_____| | |  __/ |_) | (_) | |  | |_\__ \                                                #
# |___/ .__/|_| |_|_|_| |_/_/\_\    |_|  \___| .__/ \___/|_|   \__|___/                                                #
#     |_|                                    |_|                                                                       #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2023-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
**A Sphinx extension providing uni test results embedded in documentation pages.**
"""
from pathlib import Path
from xml.dom import minidom, Node
from xml.dom.minidom import Element

from coverage.results             import Numbers
from pyTooling.Configuration.JSON import Configuration
from pyTooling.Decorators         import export, readonly

from sphinx_reports.Common                 import ReportExtensionError
from sphinx_reports.DataModel.CodeCoverage import PackageCoverage, ModuleCoverage, AggregatedCoverage
from sphinx_reports.DataModel.Unittest import Testsuite, Testcase


@export
class UnittestError(ReportExtensionError):
	pass


@export
class Analyzer:
	_packageName:     str
	_reportFile:      Path
	_documentElement: Element
	_testsuite:       Testsuite

	def __init__(self, packageName: str, reportFile: Path):
		self._packageName = packageName
		self._reportFile = reportFile

		if not self._reportFile.exists():
			# not found vs. does not exist
			# text in inner exception needed?
			#   FileNotFoundError(f"File '{self._path!s}' not found.")
			raise UnittestError(f"JUnit unittest report file '{self._reportFile}' not found.") from FileNotFoundError(self._reportFile)

		try:
			self._documentElement = minidom.parse(str(self._reportFile)).documentElement
		except Exception as ex:
			raise UnittestError(f"Couldn't open '{self._reportFile}'.") from ex

	def Convert(self) -> Testsuite:
		return self._ParseRootElement(self._documentElement)

	def _ParseRootElement(self, root: Element) -> Testsuite:
		testsuite = Testsuite("root")

		for rootNode in root.childNodes:
			if rootNode.nodeName == "testsuite":
				ts = self._ParseTestsuite(rootNode)
				testsuite._testsuites[ts._name] = ts

		return testsuite

	def _ParseTestsuite(self, testsuitesNode: Element) -> Testsuite:
		name = testsuitesNode.getAttribute("name")

		testsuite = Testsuite(name)

		for testsuiteNode in testsuitesNode.childNodes:
			if testsuiteNode.nodeType == Node.ELEMENT_NODE:
				if testsuiteNode.tagName == "testcase":
					tc = self._ParseTestcase(testsuiteNode)

					testsuite._testcases[tc._name] = tc

		return testsuite

	def _ParseTestcase(self, testsuiteNode: Element) -> Testcase:
		className = testsuiteNode.getAttribute("classname")

		testcase = Testcase(className)

		return testcase
