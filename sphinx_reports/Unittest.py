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
# Copyright 2023-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from enum     import Flag
from pathlib  import Path
from typing   import Dict, Tuple, Any, List, Mapping, Generator, TypedDict, ClassVar, Optional as Nullable

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
class ShowTestcases(Flag):
	passed = 1
	failed = 2
	skipped = 4
	excluded = 8
	errors = 16
	aborted = 32

	all = passed | failed | skipped | excluded | errors | aborted
	not_passed = all & ~passed

	def __eq__(self, other):
		if isinstance(other, TestcaseStatus):
			if other is TestcaseStatus.Passed:
				return ShowTestcases.passed in self
			elif other is TestcaseStatus.Failed:
				return ShowTestcases.failed in self
			elif other is TestcaseStatus.Skipped:
				return ShowTestcases.skipped in self
			elif other is TestcaseStatus.Excluded:
				return ShowTestcases.excluded in self
			elif other is TestcaseStatus.Error or other is TestcaseStatus.SetupError:
				return ShowTestcases.errors in self
			elif other is TestcaseStatus.Aborted:
				return ShowTestcases.aborted in self

		return False


@export
class UnittestSummary(BaseDirective):
	"""
	This directive will be replaced by a table representing unit test results.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 6

	option_spec = {
		"class":                  strip,
		"reportid":               strip,
		"testsuite-summary-name": strip,
		"show-testcases":         strip,
		"no-assertions":          flag,
		"hide-testsuite-summary": flag
	}

	directiveName: str = "unittest-summary"
	configPrefix:  str = "unittest"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		f"{configPrefix}_testsuites": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by unittest directives.

	_testSummaries:    ClassVar[Dict[str, report_DictType]] = {}

	_cssClasses:           List[str]
	_reportID:             str
	_noAssertions:         bool
	_hideTestsuiteSummary: bool
	_testsuiteSummaryName: Nullable[str]
	_showTestcases:        ShowTestcases
	_xmlReport:            Path
	_testsuite:            TestsuiteSummary

	def _CheckOptions(self) -> None:
		"""
		Parse all directive options or use default values.
		"""
		cssClasses = self._ParseStringOption("class", "", r"(\w+)?( +\w+)*")
		showTestcases = self._ParseStringOption("show-testcases", "all", r"all|not-passed")

		self._cssClasses = [] if cssClasses == "" else cssClasses.split(" ")
		self._reportID = self._ParseStringOption("reportid")
		self._testsuiteSummaryName = self._ParseStringOption("testsuite-summary-name", "", r".+")
		self._showTestcases = ShowTestcases[showTestcases.replace("-", "_")]
		self._noAssertions = "no-assertions" in self.options
		self._hideTestsuiteSummary = "hide-testsuite-summary" in self.options

		try:
			testSummary = self._testSummaries[self._reportID]
		except KeyError as ex:
			raise ReportExtensionError(f"No unit testing configuration item for '{self._reportID}'.") from ex
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

	def _sortedValues(self, d: Mapping[str, Testsuite]) -> Generator[Testsuite, None, None]:
		for key in sorted(d.keys()):
			yield d[key]

	def _convertTestcaseStatusToSymbol(self, status: TestcaseStatus) -> str:
		if status is TestcaseStatus.Passed:
			return "✅"
		elif status is TestcaseStatus.Failed:
			return "❌"
		elif status is TestcaseStatus.Skipped:
			return "⚠"
		elif status is TestcaseStatus.Aborted:
			return "🚫"
		elif status is TestcaseStatus.Excluded:
			return "➖"
		elif status is TestcaseStatus.Errored:
			return "❗"
		elif status is TestcaseStatus.SetupError:
			return "⛔"
		elif status is TestcaseStatus.Unknown:
			return "❓"
		else:
			return "❌"

	def _convertTestsuiteStatusToSymbol(self, status: TestsuiteStatus) -> str:
		if status is TestsuiteStatus.Passed:
			return "✅"
		elif status is TestsuiteStatus.Failed:
			return "❌"
		elif status is TestsuiteStatus.Skipped:
			return "⚠"
		elif status is TestsuiteStatus.Aborted:
			return "🚫"
		elif status is TestsuiteStatus.Excluded:
			return "➖"
		elif status is TestsuiteStatus.Errored:
			return "❗"
		elif status is TestsuiteStatus.SetupError:
			return "⛔"
		elif status is TestsuiteStatus.Unknown:
			return "❓"
		else:
			return "❌"

	def _formatTimedelta(self, delta: timedelta) -> str:
		if delta is None:
			return ""

		# Compute by hand, because timedelta._to_microseconds is not officially documented
		microseconds = (delta.days * 86_400 + delta.seconds) * 1_000_000 + delta.microseconds
		milliseconds = (microseconds + 500) // 1000
		seconds = milliseconds // 1000
		minutes = seconds // 60
		hours = minutes // 60
		return f"{hours:02}:{minutes % 60:02}:{seconds % 60:02}.{milliseconds % 1000:03}"

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

		cssClasses = ["report-unittest-table", f"report-unittest-{self._reportID}"]
		cssClasses.extend(self._cssClasses)

		table, tableGroup = self._CreateTableHeader(
			identifier=self._reportID,
			columns=columns,
			classes=cssClasses
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		self.renderRoot(tableBody, self._testsuite, self._hideTestsuiteSummary, self._testsuiteSummaryName)

		return table

	def renderRoot(self, tableBody: nodes.tbody, testsuiteSummary: TestsuiteSummary, includeRoot: bool = True, testsuiteSummaryName: Nullable[str] = None) -> None:
		level = 0

		if includeRoot:
			level += 1
			state = self._convertTestsuiteStatusToSymbol(testsuiteSummary._status)

			tableRow = nodes.row("", classes=["report-testsuitesummary", f"testsuitesummary-{testsuiteSummary._status.name.lower()}"])
			tableBody += tableRow

			tableRow += nodes.entry("", nodes.paragraph(text=f"{state}{testsuiteSummary.Name if testsuiteSummaryName == '' else testsuiteSummaryName}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.TestcaseCount}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Skipped}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Errored}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Failed}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Passed}"))
			if not self._noAssertions:
				tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f"{self._formatTimedelta(testsuiteSummary.TotalDuration)}"))

		for ts in self._sortedValues(testsuiteSummary._testsuites):
			self.renderTestsuite(tableBody, ts, level)

		self.renderSummary(tableBody, testsuiteSummary)

	def renderTestsuite(self, tableBody: nodes.tbody, testsuite: Testsuite, level: int) -> None:
		state = self._convertTestsuiteStatusToSymbol(testsuite._status)

		tableRow = nodes.row("", classes=["report-testsuite", f"testsuite-{testsuite._status.name.lower()}"])
		tableBody += tableRow

		tableRow += nodes.entry("", nodes.paragraph(text=f"{'  ' * level}{state}{testsuite.Name}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.TestcaseCount}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Skipped}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Errored}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Failed}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuite.Passed}"))
		if not self._noAssertions:
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f"{self._formatTimedelta(testsuite.TotalDuration)}"))

		for ts in self._sortedValues(testsuite._testsuites):
			self.renderTestsuite(tableBody, ts, level + 1)

		for testcase in self._sortedValues(testsuite._testcases):
			if testcase._status == self._showTestcases:
				self.renderTestcase(tableBody, testcase, level + 1)

	def renderTestcase(self, tableBody: nodes.tbody, testcase: Testcase, level: int) -> None:
		state = self._convertTestcaseStatusToSymbol(testcase._status)

		tableRow =	nodes.row("", classes=["report-testcase", f"testcase-{testcase._status.name.lower()}"])
		tableBody += tableRow

		tableRow += nodes.entry("", nodes.paragraph(text=f"{'  ' * level}{state}{testcase.Name}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Expected}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Covered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		if not self._noAssertions:
			tableRow += nodes.entry("", nodes.paragraph(text=f"{testcase.AssertionCount}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{self._formatTimedelta(testcase.TotalDuration)}"))

	def renderSummary(self, tableBody: nodes.tbody, testsuiteSummary: TestsuiteSummary) -> None:
		state = self._convertTestsuiteStatusToSymbol(testsuiteSummary._status)

		tableRow = nodes.row("", classes=["report-summary", f"testsuitesummary-{testsuiteSummary._status.name.lower()}"])
		tableBody += tableRow

		tableRow += nodes.entry("", nodes.paragraph(text=f"{state} {testsuiteSummary.Status.name.upper()}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.TestcaseCount}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Skipped}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Errored}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Failed}"))
		tableRow += nodes.entry("", nodes.paragraph(text=f"{testsuiteSummary.Passed}"))
		if not self._noAssertions:
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {testsuite.Uncovered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f"{self._formatTimedelta(testsuiteSummary.TotalDuration)}"))

	def run(self) -> List[nodes.Node]:
		container = nodes.container()

		try:
			self._CheckOptions()
		except ReportExtensionError as ex:
			message = f"Caught {ex.__class__.__name__} when checking options for directive '{self.directiveName}'."
			return self._internalError(container, __name__, message, ex)

		# Assemble a list of Python source files
		try:
			doc = Document(self._xmlReport, analyzeAndConvert=True)
		except Exception as ex:
			message = f"Caught {ex.__class__.__name__} when reading and parsing '{self._xmlReport}'."
			return self._internalError(container, __name__, message, ex)

		doc.Aggregate()

		try:
			self._testsuite = doc.ToTestsuiteSummary()
		except Exception as ex:
			message = f"Caught {ex.__class__.__name__} when converting to a TestsuiteSummary for JUnit document '{self._xmlReport}'."
			return self._internalError(container, __name__, message, ex)

		self._testsuite.Aggregate()

		try:
			container += self._GenerateTestSummaryTable()
		except Exception as ex:
			message = f"Caught {ex.__class__.__name__} when generating the document structure for JUnit document '{self._xmlReport}'."
			return self._internalError(container, __name__, message, ex)

		return [container]
