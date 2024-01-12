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

from sphinx_reports.Common                          import ReportExtensionError, LegendPosition
from sphinx_reports.Sphinx                          import strip, BaseDirective
from sphinx_reports.DataModel.DocumentationCoverage import PackageCoverage, AggregatedCoverage
from sphinx_reports.Adapter.DocStrCoverage          import Analyzer


class package_DictType(TypedDict):
	name: str
	directory: str
	fail_below: int
	levels: Dict[int, Dict[str, str]]


@export
class UnittestSummary(BaseDirective):
	"""
	This directive will be replaced by a table representing unit test results.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = {
		"packageid": strip,
		"legend":    strip,
	}

	directiveName: str = "unittest-summary"
	configPrefix:  str = "unittest"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		"packages": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by this domain. (name: (default, rebuilt, type))

	_packageID:   str
	_legend:      LegendPosition
	_packageName: str
	_directory:   Path
	_failBelow:   float
	_levels:      Dict[int, Dict[str, str]]
	_coverage:    PackageCoverage

	def _CheckOptions(self) -> None:
		# Parse all directive options or use default values
		self._packageID = self._ParseStringOption("packageid")
		self._legend = self._ParseLegendOption("legend", LegendPosition.bottom)

	def _CheckConfiguration(self) -> None:
		# Check configuration fields and load necessary values
		try:
			allPackages: Dict[str, package_DictType] = self.config[f"{self.configPrefix}_packages"]
		except (KeyError, AttributeError) as ex:
			raise ReportExtensionError(f"Configuration option '{self.configPrefix}_packages' is not configured.") from ex

		try:
			packageConfiguration = allPackages[self._packageID]
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {self.configPrefix}_packages: No configuration found for '{self._packageID}'.") from ex

		try:
			self._packageName = packageConfiguration["name"]
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.name: Configuration is missing.") from ex

		try:
			self._directory = Path(packageConfiguration["directory"])
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.directory: Configuration is missing.") from ex

		if not self._directory.exists():
			raise ReportExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.directory: Directory doesn't exist.") from FileNotFoundError(self._directory)

		try:
			self._failBelow = int(packageConfiguration["fail_below"]) / 100
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.fail_below: Configuration is missing.") from ex

		if not (0.0 <= self._failBelow <= 100.0):
			raise ReportExtensionError(
				f"conf.py: {self.configPrefix}_packages:{self._packageID}.fail_below: Is out of range 0..100.")

		self._levels = {
			30:  {"class": "report-cov-below30",  "background": "rgba(101,  31, 255, .2)", "desc": "almost undocumented"},
			50:  {"class": "report-cov-below50",  "background": "rgba(255,  82,  82, .2)", "desc": "poorly documented"},
			80:  {"class": "report-cov-below80",  "background": "rgba(255, 145,   0, .2)", "desc": "roughly documented"},
			90:  {"class": "report-cov-below90",  "background": "rgba(  0, 200,  82, .2)", "desc": "well documented"},
			100: {"class": "report-cov-below100", "background": "rgba(  0, 200,  82, .2)", "desc": "excellent documented"},
		}

	def _ConvertToColor(self, currentLevel: float, configKey: str) -> str:
		for levelLimit, levelConfig in self._levels.items():
			if (currentLevel * 100) < levelLimit:
				return levelConfig[configKey]

		return self._levels[100][configKey]

	def _GenerateCoverageTable(self) -> nodes.table:
		# Create a table and table header with 5 columns
		table, tableGroup = self._PrepareTable(
			identifier=self._packageID,
			columns={
				"Filename": 500,
				"Total": 100,
				"Covered": 100,
				"Missing": 100,
				"Coverage in %": 100
			},
			classes=["report-doccov-table"]
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		def sortedValues(d: Mapping[str, AggregatedCoverage]) -> Generator[AggregatedCoverage, None, None]:
			for key in sorted(d.keys()):
				yield d[key]

		def renderlevel(tableBody: nodes.tbody, packageCoverage: PackageCoverage, level: int = 0) -> None:
			tableBody += nodes.row(
				"",
				nodes.entry("", nodes.paragraph(text=f"{' '*level}{packageCoverage.Name} ({packageCoverage.File})")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Expected}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Covered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Uncovered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Coverage:.1%}")),
				classes=["report-doccov-table-row", self._ConvertToColor(packageCoverage.Coverage, "class")],
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
					classes=["report-doccov-table-row", self._ConvertToColor(module.Coverage, "class")],
					# style="background: rgba(  0, 200,  82, .2);"
				)

		renderlevel(tableBody, self._coverage)

		# Add a summary row
		tableBody += nodes.row(
			"",
			nodes.entry("", nodes.paragraph(text=f"Overall ({self._coverage.FileCount} files):")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.Expected}")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.Covered}")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.Uncovered}")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.Coverage:.1%}"),
				# classes=[self._ConvertToColor(self._coverage.coverage(), "class")]
			),
			classes=["report-doccov-summary-row", self._ConvertToColor(self._coverage.AggregatedCoverage, "class")]
		)

		return table

	def _CreateLegend(self, identifier: str, classes: Iterable[str]) -> List[nodes.Element]:
		rubric = nodes.rubric("", text="Legend")

		table = nodes.table("", id=identifier, classes=classes)

		tableGroup = nodes.tgroup(cols=2)
		table += tableGroup

		tableRow = nodes.row()
		tableGroup += nodes.colspec(colwidth=300)
		tableRow += nodes.entry("", nodes.paragraph(text="%"))
		tableGroup += nodes.colspec(colwidth=300)
		tableRow += nodes.entry("", nodes.paragraph(text="Coverage Level"))
		tableGroup += nodes.thead("", tableRow)

		tableBody = nodes.tbody()
		tableGroup += tableBody

		for level, config in self._levels.items():
			tableBody += nodes.row(
				"",
				nodes.entry("", nodes.paragraph(text=f"≤{level}%")),
				nodes.entry("", nodes.paragraph(text=config["desc"])),
				classes=["report-doccov-legend-row", self._ConvertToColor((level - 1) / 100, "class")]
			)

		return [rubric, table]

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()
		self._CheckConfiguration()

		# Assemble a list of Python source files
		analyzer = Analyzer(self._packageName, self._directory)
		analyzer.Analyze()
		self._coverage = analyzer.Convert()
		# self._coverage.CalculateCoverage()
		self._coverage.Aggregate()

		container = nodes.container()

		if LegendPosition.top in self._legend:
			container += self._CreateLegend(identifier="legend1", classes=["report-doccov-legend"])

		container += self._GenerateCoverageTable()

		if LegendPosition.bottom in self._legend:
			container += self._CreateLegend(identifier="legend2", classes=["report-doccov-legend"])

		return [container]
