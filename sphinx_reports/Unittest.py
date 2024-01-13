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
from pathlib import Path
from typing  import Dict, Tuple, Any, List, Iterable, Mapping, Generator, TypedDict

from docutils             import nodes
from pyTooling.Decorators import export

from sphinx_reports.Common             import ReportExtensionError, LegendPosition
from sphinx_reports.Sphinx             import strip, BaseDirective
from sphinx_reports.DataModel.Unittest import Testsuite, TestsuiteSummary, Testcase
from sphinx_reports.Adapter.JUnit      import Analyzer


class report_DictType(TypedDict):
	name: str
	xml_report: str


@export
class UnittestSummary(BaseDirective):
	"""
	This directive will be replaced by a table representing unit test results.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 1

	option_spec = {
		"reportid": strip,
	}

	directiveName: str = "unittest-summary"
	configPrefix:  str = "unittest"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		f"{configPrefix}_testsuites": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by this domain. (name: (default, rebuilt, type))

	_reportID:   str
	_legend:      LegendPosition
	_packageName: str
	_xmlReport:   Path
	_testsuite:   TestsuiteSummary

	def _CheckOptions(self) -> None:
		# Parse all directive options or use default values
		self._reportID = self._ParseStringOption("reportid")

	def _CheckConfiguration(self) -> None:
		from sphinx_reports import ReportDomain

		# Check configuration fields and load necessary values
		try:
			allTestsuites: Dict[str, report_DictType] = self.config[f"{ReportDomain.name}_{self.configPrefix}_testsuites"]
		except (KeyError, AttributeError) as ex:
			raise ReportExtensionError(f"Configuration option '{ReportDomain.name}_{self.configPrefix}_testsuites' is not configured.") from ex

		try:
			testsuiteConfiguration = allTestsuites[self._reportID]
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_testsuites: No configuration found for '{self._reportID}'.") from ex

		try:
			self._packageName = testsuiteConfiguration["name"]
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_testsuites:{self._reportID}.name: Configuration is missing.") from ex

		try:
			self._xmlReport = Path(testsuiteConfiguration["xml_report"])
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_testsuites:{self._reportID}.xml_report: Configuration is missing.") from ex

		if not self._xmlReport.exists():
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_testsuites:{self._reportID}.xml_report: Unittest report file '{self._xmlReport}' doesn't exist.") from FileNotFoundError(self._xmlReport)

	def _GenerateTestSummaryTable(self) -> nodes.table:
		# Create a table and table header with 5 columns
		table, tableGroup = self._PrepareTable(
			identifier=self._reportID,
			columns={
				"Testsuite / Testcase": 500,
				"???": 100,
				"????": 100,
				"?????": 100,
				"Status": 100
			},
			classes=["report-unittest-table"]
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		def sortedValues(d: Mapping[str, Testsuite]) -> Generator[Testsuite, None, None]:
			for key in sorted(d.keys()):
				yield d[key]

		def renderRoot(tableBody: nodes.tbody, testsuite: TestsuiteSummary, level: int = 0) -> None:
			tableBody += nodes.row(
				"",
				nodes.entry("", nodes.paragraph(text=f"{' '*level}❌{testsuite.Name}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Expected}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Covered}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Uncovered}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Coverage:.1%}")),
				classes=["report-unittest-table-row"],
				# style="background: rgba(  0, 200,  82, .2);"
			)

			for ts in sortedValues(testsuite._testsuites):
				renderTestsuite(tableBody, ts, level + 1)

		def renderTestsuite(tableBody: nodes.tbody, testsuite: Testsuite, level: int) -> None:
			tableBody += nodes.row(
				"",
				nodes.entry("", nodes.paragraph(text=f"{' '*level}✅{testsuite.Name}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Expected}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Covered}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Uncovered}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Coverage:.1%}")),
				classes=["report-unittest-table-row"],
				# style="background: rgba(  0, 200,  82, .2);"
			)

			for ts in sortedValues(testsuite._testsuites):
				renderTestsuite(tableBody, ts, level + 1)

			for testcase in sortedValues(testsuite._testcases):
				renderTestcase(tableBody, testcase, level + 1)

		def renderTestcase(tableBody: nodes.tbody, testcase: Testcase, level: int) -> None:
			tableBody += nodes.row(
				"",
				nodes.entry("", nodes.paragraph(text=f"{' '*level}✅{testcase.Name}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Expected}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Covered}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Uncovered}")),
				nodes.entry("", nodes.paragraph(text=f"")),  # {testsuite.Coverage:.1%}")),
				classes=["report-unittest-table-row"],
				# style="background: rgba(  0, 200,  82, .2);"
			)

			for test in sortedValues(testcase._tests):
				tableBody += nodes.row(
					"",
					nodes.entry("", nodes.paragraph(text=f"{' '*(level+1)}✅{test.Name}")),
					nodes.entry("", nodes.paragraph(text=f"")),  # {test.Expected}")),
					nodes.entry("", nodes.paragraph(text=f"")),  # {test.Covered}")),
					nodes.entry("", nodes.paragraph(text=f"")),  # {test.Uncovered}")),
					nodes.entry("", nodes.paragraph(text=f"")),  # {test.Coverage :.1%}")),
					classes=["report-unittest-table-row"],
					# style="background: rgba(  0, 200,  82, .2);"
				)

		renderRoot(tableBody, self._testsuite)

		# # Add a summary row
		# tableBody += nodes.row(
		# 	"",
		# 	nodes.entry("", nodes.paragraph(text=f"Overall ({self._testsuite.FileCount} files):")),
		# 	nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Expected}")),
		# 	nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Covered}")),
		# 	nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Uncovered}")),
		# 	nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Coverage:.1%}"),
		# 							# classes=[self._ConvertToColor(self._coverage.coverage(), "class")]
		# 							),
		# 	classes=["report-unittest-summary-row"]
		# )

		return table

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()
		self._CheckConfiguration()

		# Assemble a list of Python source files
		analyzer = Analyzer(self._packageName, self._xmlReport)
		self._testsuite = analyzer.Convert()
		# self._testsuite.Aggregate()

		container = nodes.container()
		container += self._GenerateTestSummaryTable()

		return [container]
