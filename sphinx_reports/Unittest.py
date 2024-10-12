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
from datetime import timedelta
from pathlib  import Path
from typing   import Dict, Tuple, Any, List, Mapping, Generator, TypedDict, ClassVar

from docutils                          import nodes
from docutils.parsers.rst.directives   import flag
from pyTooling.Decorators              import export
from pyEDAA.Reports.Unittesting        import TestcaseStatus, TestsuiteStatus
from pyEDAA.Reports.Unittesting.JUnit  import Testsuite, TestsuiteSummary, Testcase, Document
from sphinx.application                import Sphinx
from sphinx.config                     import Config

from sphinx_reports.Common             import ReportExtensionError
from sphinx_reports.Sphinx             import strip, BaseDirective


class report_DictType(TypedDict):
	xml_report: Path


@export
class UnittestSummary(BaseDirective):
	"""
	This directive will be replaced by a table representing unit test results.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = {
		"reportid":      strip,
		"no-assertions": flag
	}

	directiveName: str = "unittest-summary"
	configPrefix:  str = "unittest"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		f"{configPrefix}_testsuites": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by unittest directives.

	_testSummaries: ClassVar[Dict[str, report_DictType]] = {}

	_reportID:     str
	_noAssertions: bool
	_xmlReport:    Path
	_testsuite:    TestsuiteSummary

	def _CheckOptions(self) -> None:
		"""
		Parse all directive options or use default values.
		"""
		self._reportID = self._ParseStringOption("reportid")
		self._noAssertions = "without-assertions" in self.options

		testSummary = self._testSummaries[self._reportID]
		self._xmlReport = testSummary["xml_report"]

	@classmethod
	def CheckConfiguration(cls, sphinxApplication: Sphinx, sphinxConfiguration: Config) -> None:
		"""
		Check configuration fields and load necessary values.

		:param sphinxApplication:   Sphinx application instance.
		:param sphinxConfiguration: Sphinx configuration instance.
		"""
		cls._CheckConfiguration(sphinxConfiguration)

	@classmethod
	def ReadReports(cls, sphinxApplication: Sphinx) -> None:
		"""
		Read unittest report files.

		:param sphinxApplication:   Sphinx application instance.
		"""
		print(f"[REPORT] Reading unittest reports ...")

	@classmethod
	def _CheckConfiguration(cls, sphinxConfiguration: Config) -> None:
		from sphinx_reports import ReportDomain

		variableName = f"{ReportDomain.name}_{cls.configPrefix}_testsuites"

		try:
			allTestsuites: Dict[str, report_DictType] = sphinxConfiguration[f"{ReportDomain.name}_{cls.configPrefix}_testsuites"]
		except (KeyError, AttributeError) as ex:
			raise ReportExtensionError(f"Configuration option '{variableName}' is not configured.") from ex

		# try:
		# 	testsuiteConfiguration = allTestsuites[self._reportID]
		# except KeyError as ex:
		# 	raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_testsuites: No configuration found for '{self._reportID}'.") from ex

		for reportID, testSummary in allTestsuites.items():
			summaryName = f"conf.py: {variableName}:[{reportID}]"

			try:
				xmlReport = Path(testSummary["xml_report"])
			except KeyError as ex:
				raise ReportExtensionError(f"{summaryName}.xml_report: Configuration is missing.") from ex

			if not xmlReport.exists():
				raise ReportExtensionError(f"{summaryName}.xml_report: Unittest report file '{xmlReport}' doesn't exist.") from FileNotFoundError(xmlReport)

			cls._testSummaries[reportID] = {
				"xml_report": xmlReport
			}

	def _GenerateTestSummaryTable(self) -> nodes.table:
		# Create a table and table header with 8 columns
		columns = [
			("Testsuite / Testcase", None, 500),
			("Testcases", None, 100),
			("Skipped", None, 100),
			("Errored", None, 100),
			("Failed", None, 100),
			("Passed", None, 100),
			("Assertions", None, 100),
			("Runtime (HH:MM:SS.sss)", None, 100),
		]

		# If assertions shouldn't be displayed, remove column from columns list
		if self._noAssertions:
			columns.pop(6)

		table, tableGroup = self._CreateTableHeader(
			identifier=self._reportID,
			columns=columns,
			classes=["report-unittest-table"]
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		def sortedValues(d: Mapping[str, Testsuite]) -> Generator[Testsuite, None, None]:
			for key in sorted(d.keys()):
				yield d[key]

		def convertTestcaseStatusToSymbol(state: TestcaseStatus) -> str:
			if state is TestcaseStatus.Passed:
				return "✅"
			elif state is TestcaseStatus.Unknown:
				return "❓"
			else:
				return "❌"

		def convertTestsuiteStatusToSymbol(state: TestsuiteStatus) -> str:
			if state is TestsuiteStatus.Passed:
				return "✅"
			elif state is TestsuiteStatus.Unknown:
				return "❓"
			else:
				return "❌"

		def formatTimedelta(delta: timedelta) -> str:
			if delta is None:
				return ""

			# Compute by hand, because timedelta._to_microseconds is not officially documented
			microseconds = (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds
			milliseconds = (microseconds + 500) // 1000
			seconds = milliseconds // 1000
			minutes = seconds // 60
			hours = minutes // 60
			return f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}.{milliseconds % 1000:03}"

		def renderRoot(tableBody: nodes.tbody, testsuite: TestsuiteSummary) -> None:
			for ts in sortedValues(testsuite._testsuites):
				renderTestsuite(tableBody, ts, 0)

		def renderTestsuite(tableBody: nodes.tbody, testsuite: Testsuite, level: int) -> None:
			state = convertTestsuiteStatusToSymbol(testsuite._status)

			tableRow = nodes.row("", classes=["report-unittest-table-row", "report-testsuite"])
			tableBody += tableRow

			tableRow += nodes.entry("", nodes.paragraph(text=f"{'  ' * level}{state}{testsuite.Name}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.TestcaseCount}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Skipped}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Errored}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Failed}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Passed}"))
			if not self._noAssertions:
				tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f"{formatTimedelta(testsuite.TotalDuration)}"))

			for ts in sortedValues(testsuite._testsuites):
				renderTestsuite(tableBody, ts, level + 1)

			for testcase in sortedValues(testsuite._testcases):
				renderTestcase(tableBody, testcase, level + 1)

		def renderTestcase(tableBody: nodes.tbody, testcase: Testcase, level: int) -> None:
			state = convertTestcaseStatusToSymbol(testcase._status)

			tableRow =	nodes.row("", classes=["report-unittest-table-row", "report-testcase"])
			tableBody += tableRow

			tableRow += nodes.entry("", nodes.paragraph(text=f"{'  ' * level}{state}{testcase.Name}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Expected}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Covered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
			if not self._noAssertions:
				tableRow += nodes.entry("", nodes.paragraph(text=f"{testcase.AssertionCount}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{formatTimedelta(testcase.TotalDuration)}"))

		renderRoot(tableBody, self._testsuite)

		# # Add a summary row

		return table

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()

		# Assemble a list of Python source files
		try:
			doc = Document(self._xmlReport, parse=True)
		except Exception as ex:
			logger = logging.getLogger(__name__)
			logger.error(f"Caught {ex.__class__.__name__} when reading and parsing '{self._xmlReport}'.\n  {ex}")
			return []

		doc.Aggregate()

		try:
			self._testsuite = doc.ToTestsuiteSummary()
		except Exception as ex:
			logger = logging.getLogger(__name__)
			logger.error(f"Caught {ex.__class__.__name__} when converting to a TestsuiteSummary for JUnit document '{self._xmlReport}'.\n  {ex}")
			return []

		self._testsuite.Aggregate()

		try:
			container = nodes.container()
			container += self._GenerateTestSummaryTable()
		except Exception as ex:
			logger = logging.getLogger(__name__)
			logger.error(f"Caught {ex.__class__.__name__} when generating the document structure for JUnit document '{self._xmlReport}'.\n  {ex}")
			return []

		return [container]
