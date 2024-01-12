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
from sphinx_reports.DataModel.Unittest import Testsuite
from sphinx_reports.Adapter.JUnit      import Analyzer


class package_DictType(TypedDict):
	name: str
	directory: str


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
	_testsuite:   Testsuite

	def _CheckOptions(self) -> None:
		# Parse all directive options or use default values
		self._reportID = self._ParseStringOption("reportid")

	def _CheckConfiguration(self) -> None:
		from sphinx_reports import ReportDomain

		# Check configuration fields and load necessary values
		try:
			allTestsuites: Dict[str, package_DictType] = self.config[f"{ReportDomain.name}_{self.configPrefix}_testsuites"]
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

	def _GenerateCoverageTable(self) -> nodes.table:
		# Create a table and table header with 5 columns
		table, tableGroup = self._PrepareTable(
			identifier=self._reportID,
			columns={
				"Filename": 500,
				"Total": 100,
				"Covered": 100,
				"Missing": 100,
				"Coverage in %": 100
			},
			classes=["report-unittest-table"]
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		def sortedValues(d: Mapping[str, Testsuite]) -> Generator[Testsuite, None, None]:
			for key in sorted(d.keys()):
				yield d[key]

		def renderlevel(tableBody: nodes.tbody, packageCoverage: Testsuite, level: int = 0) -> None:
			tableBody += nodes.row(
				"",
				nodes.entry("", nodes.paragraph(text=f"{' '*level}{packageCoverage.Name} ({packageCoverage.File})")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Expected}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Covered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Uncovered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Coverage:.1%}")),
				classes=["report-unittest-table-row", self._ConvertToColor(packageCoverage.Coverage, "class")],
				# style="background: rgba(  0, 200,  82, .2);"
			)

			for package in sortedValues(packageCoverage._packages):
				renderlevel(tableBody, package, level + 1)

			for module in sortedValues(packageCoverage._modules):
				tableBody += nodes.row(
					"",
					nodes.entry("", nodes.paragraph(text=f"{' '*level}{module.Name} ({module.File})")),
					nodes.entry("", nodes.paragraph(text=f"{module.Expected}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Covered}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Uncovered}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Coverage :.1%}")),
					classes=["report-unittest-table-row"],
					# style="background: rgba(  0, 200,  82, .2);"
				)

		renderlevel(tableBody, self._testsuite)

		# Add a summary row
		tableBody += nodes.row(
			"",
			nodes.entry("", nodes.paragraph(text=f"Overall ({self._testsuite.FileCount} files):")),
			nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Expected}")),
			nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Covered}")),
			nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Uncovered}")),
			nodes.entry("", nodes.paragraph(text=f"{self._testsuite.Coverage:.1%}"),
									# classes=[self._ConvertToColor(self._coverage.coverage(), "class")]
									),
			classes=["report-unittest-summary-row"]
		)

		return table

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()
		self._CheckConfiguration()

		# Assemble a list of Python source files
		analyzer = Analyzer(self._packageName, self._xmlReport)
		self._testsuite = analyzer.Convert()
		# self._testsuite.Aggregate()

		container = nodes.container()

		if LegendPosition.top in self._legend:
			container += self._CreateLegend(identifier="legend1", classes=["report-unittest-legend"])

		container += self._GenerateCoverageTable()

		if LegendPosition.bottom in self._legend:
			container += self._CreateLegend(identifier="legend2", classes=["report-unittest-legend"])

		return [container]
