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
**Report unit test results as Sphinx documentation page(s).**
"""
from typing import Dict, Tuple, Any, List, Mapping, Generator

from docutils                          import nodes
from pyTooling.Decorators              import export
from sphinx.application import Sphinx
from sphinx.config import Config

from sphinx_reports.Common               import ReportExtensionError
from sphinx_reports.Sphinx               import strip, BaseDirective
from sphinx_reports.DataModel.Dependency import Distribution
from sphinx_reports.Adapter.Dependency   import DependencyScanner


@export
class DependencyTable(BaseDirective):
	"""
	This directive will be replaced by a table representing dependencies.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 1

	option_spec = {
		"package":       strip
	}

	directiveName: str = "dependency-table"
	configPrefix:  str = "dep"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		# f"{configPrefix}_testsuites": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by unittest directives.

	_packageName:  str

	_distribution: Distribution

	def _CheckOptions(self) -> None:
		"""
		Parse all directive options or use default values.
		"""
		self._packageName = self._ParseStringOption("package")

	@classmethod
	def CheckConfiguration(cls, sphinxApplication: Sphinx, sphinxConfiguration: Config) -> None:
		"""
		Check configuration fields and load necessary values.

		:param sphinxApplication:   Sphinx application instance.
		:param sphinxConfiguration: Sphinx configuration instance.
		"""
		pass

	def _GenerateDependencyTable(self) -> nodes.table:
		# Create a table and table header with 8 columns
		columns = [
			("Package", None, 500),
			("Version", None, 100),
			("License", None, 100),
		]

		table, tableGroup = self._CreateTableHeader(
			identifier=self._packageName,
			columns=columns,
			classes=["report-dependency-table"]
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		# def sortedValues(d: Mapping[str, Testsuite]) -> Generator[Testsuite, None, None]:
		# 	for key in sorted(d.keys()):
		# 		yield d[key]

		def renderRoot(tableBody: nodes.tbody, distribution: Distribution) -> None:
			tableRow = nodes.row("", classes=["report-dependency-table-row", "report-dependency"])
			tableBody += tableRow

			tableRow += nodes.entry("", nodes.paragraph(text=f"{distribution.Name}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{distribution.Version}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{distribution.Licenses}"))

			# for ts in sortedValues(testsuite._testsuites):
			# 	renderTestsuite(tableBody, ts, 0)

		# def renderTestsuite(tableBody: nodes.tbody, testsuite: Testsuite, level: int) -> None:
		# 	state = stateToSymbol(testsuite._state)
		#
		# 	tableRow = nodes.row("", classes=["report-unittest-table-row", "report-testsuite"])
		# 	tableBody += tableRow
		#
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{'  ' * level}{state}{testsuite.Name}"))
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Tests}"))
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Skipped}"))
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Errored}"))
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Failed}"))
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Passed}"))
		# 	if not self._noAssertions:
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{timeformat(testsuite.Time)}"))
		#
		# 	for ts in sortedValues(testsuite._testsuites):
		# 		renderTestsuite(tableBody, ts, level + 1)
		#
		# 	for testcase in sortedValues(testsuite._testcases):
		# 		renderTestcase(tableBody, testcase, level + 1)
		#
		# def renderTestcase(tableBody: nodes.tbody, testcase: Testcase, level: int) -> None:
		# 	state = stateToSymbol(testcase._state)
		#
		# 	tableRow =	nodes.row("", classes=["report-unittest-table-row", "report-testcase"])
		# 	tableBody += tableRow
		#
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{'  ' * level}{state}{testcase.Name}"))
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Expected}")),
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Covered}")),
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		# 	if not self._noAssertions:
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f"{testcase.Assertions}"))
		# 	tableRow += nodes.entry("", nodes.paragraph(text=f"{timeformat(testcase.Time)}"))
		#
		# 	for test in sortedValues(testcase._tests):
		# 		state = stateToSymbol(test._state)
		# 		tableRow = nodes.row("", classes=["report-unittest-table-row", "report-test"])
		# 		tableBody += tableRow
		#
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f"{'  ' * (level + 1)}{state}{test.Name}"))
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {test.Expected}")),
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {test.Covered}")),
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {test.Covered}")),
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {test.Covered}")),
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {test.Covered}")),
		# 		if not self._noAssertions:
		# 			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {test.Uncovered}")),
		# 		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {test.Coverage :.1%}")),

		renderRoot(tableBody, self._distribution)

		# # Add a summary row

		return table

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()

		# Assemble a list of Python source files
		scanner = DependencyScanner(self._packageName)
		self._distribution = scanner.Distribution

		container = nodes.container()
		container += self._GenerateDependencyTable()

		return [container]
