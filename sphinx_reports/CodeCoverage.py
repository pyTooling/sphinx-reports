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
**Report code coverage as Sphinx documentation page(s).**
"""
from pathlib import Path
from typing  import Dict, Tuple, Any, List, Iterable, Mapping, Generator, TypedDict, Union

from docutils             import nodes
from pyTooling.Decorators import export

from sphinx_reports.Common                 import ReportExtensionError, LegendPosition
from sphinx_reports.Sphinx                 import strip, BaseDirective
from sphinx_reports.DataModel.CodeCoverage import PackageCoverage, AggregatedCoverage
from sphinx_reports.Adapter.Coverage       import Analyzer


class package_DictType(TypedDict):
	name:        str
	json_report: str
	fail_below:  int
	levels:      Dict[Union[int, str], Dict[str, str]]


@export
class CodeCoverage(BaseDirective):
	"""
	This directive will be replaced by a table representing code coverage.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = {
		"packageid": strip,
		"legend":    strip,
	}

	directiveName: str = "code-coverage"
	configPrefix:  str = "codecov"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		f"{configPrefix}_packages": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by this domain. (name: (default, rebuilt, type))

	_packageID:   str
	_legend:      LegendPosition
	_packageName: str
	_jsonReport:  Path
	_failBelow:   float
	_levels:      Dict[Union[int, str], Dict[str, str]]
	_coverage:    PackageCoverage

	def _CheckOptions(self) -> None:
		# Parse all directive options or use default values
		self._packageID = self._ParseStringOption("packageid")
		self._legend = self._ParseLegendOption("legend", LegendPosition.bottom)

	def _CheckConfiguration(self) -> None:
		from sphinx_reports import ReportDomain

		# Check configuration fields and load necessary values
		try:
			allPackages: Dict[str, package_DictType] = self.config[f"{ReportDomain.name}_{self.configPrefix}_packages"]
		except (KeyError, AttributeError) as ex:
			raise ReportExtensionError(f"Configuration option '{ReportDomain.name}_{self.configPrefix}_packages' is not configured.") from ex

		try:
			packageConfiguration = allPackages[self._packageID]
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages: No configuration found for '{self._packageID}'.") from ex

		try:
			self._packageName = packageConfiguration["name"]
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.name: Configuration is missing.") from ex

		try:
			self._jsonReport = Path(packageConfiguration["json_report"])
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.json_report: Configuration is missing.") from ex

		if not self._jsonReport.exists():
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.json_report: Coverage report file '{self._jsonReport}' doesn't exist.") from FileNotFoundError(self._jsonReport)

		try:
			self._failBelow = int(packageConfiguration["fail_below"]) / 100
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.fail_below: Configuration is missing.") from ex
		except ValueError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.fail_below: '{packageConfiguration['fail_below']}' is not an integer in range 0..100.") from ex

		if not (0.0 <= self._failBelow <= 100.0):
			raise ReportExtensionError(
				f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.fail_below: Is out of range 0..100.")

		try:
			levels = packageConfiguration["levels"]
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels: Configuration is missing.") from ex

		if 100 not in packageConfiguration["levels"]:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels[100]: Configuration is missing.")

		if "error" not in packageConfiguration["levels"]:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels[error]: Configuration is missing.")

		self._levels = {}
		for level, levelConfig in levels.items():
			try:
				if isinstance(level, str):
					if level != "error":
						raise ReportExtensionError(
							f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels: Level is a keyword, but not 'error'.")
				elif not (0.0 <= int(level) <= 100.0):
					raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels: Level is out of range 0..100.")
			except ValueError as ex:
				raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels: Level is not a keyword or an integer in range 0..100.") from ex

			try:
				cssClass = levelConfig["class"]
			except KeyError as ex:
				raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels[level].class: CSS class is missing.") from ex

			try:
				description = levelConfig["desc"]
			except KeyError as ex:
				raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.levels[level].desc: Description is missing.") from ex

			self._levels[level] = {"class": cssClass, "desc": description}

	def _ConvertToColor(self, currentLevel: float, configKey: str) -> str:
		if currentLevel < 0.0:
			return self._levels["error"][configKey]

		for levelLimit, levelConfig in self._levels.items():
			if isinstance(levelLimit, int) and (currentLevel * 100) < levelLimit:
				return levelConfig[configKey]

		return self._levels[100][configKey]

	def _GenerateCoverageTable(self) -> nodes.table:
		# Create a table and table header with 5 columns
		table, tableGroup = self._PrepareTable(
			identifier=self._packageID,
			columns={
				"Module": 500,
				"Total Statements": 100,
				"Excluded Statements": 100,
				"Covered Statements": 100,
				"Missing Statements": 100,
				"Total Branches": 100,
				"Covered Branches": 100,
				"Partial Branches": 100,
				"Missing Branches": 100,
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
				nodes.entry("", nodes.paragraph(text=f"{' '*level}📦{packageCoverage.Name}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.TotalStatements}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.ExcludedStatements}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.CoveredStatements}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.MissingStatements}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.TotalBranches}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.CoveredBranches}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.PartialBranches}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.MissingBranches}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Coverage:.1%}")),
				classes=["report-doccov-table-row", self._ConvertToColor(packageCoverage.Coverage, "class")],
				# style="background: rgba(  0, 200,  82, .2);"
			)

			for package in sortedValues(packageCoverage._packages):
				renderlevel(tableBody, package, level + 1)

			for module in sortedValues(packageCoverage._modules):
				tableBody += nodes.row(
					"",
					nodes.entry("", nodes.paragraph(text=f"{' '*(level+1)}  {module.Name}")),
					nodes.entry("", nodes.paragraph(text=f"{module.TotalStatements}")),
					nodes.entry("", nodes.paragraph(text=f"{module.ExcludedStatements}")),
					nodes.entry("", nodes.paragraph(text=f"{module.CoveredStatements}")),
					nodes.entry("", nodes.paragraph(text=f"{module.MissingStatements}")),
					nodes.entry("", nodes.paragraph(text=f"{module.TotalBranches}")),
					nodes.entry("", nodes.paragraph(text=f"{module.CoveredBranches}")),
					nodes.entry("", nodes.paragraph(text=f"{module.PartialBranches}")),
					nodes.entry("", nodes.paragraph(text=f"{module.MissingBranches}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Coverage :.1%}")),
					classes=["report-doccov-table-row", self._ConvertToColor(module.Coverage, "class")],
					# style="background: rgba(  0, 200,  82, .2);"
				)

		renderlevel(tableBody, self._coverage)

		# Add a summary row
		tableBody += nodes.row(
			"",
			nodes.entry("", nodes.paragraph(text=f"Overall ({self._coverage.FileCount} files):")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedExpected}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedCovered}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedCovered}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedCovered}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedCovered}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedCovered}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedCovered}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedUncovered}")),
			nodes.entry("", nodes.paragraph(text=f"")),  # {self._coverage.AggregatedCoverage:.1%}")),
				# classes=[self._ConvertToColor(self._coverage.coverage(), "class")]
			classes=["report-doccov-summary-row", self._ConvertToColor(self._coverage.Coverage, "class")]  # self._coverage.AggregatedCoverage, "class")]
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
			if isinstance(level, int):
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
		analyzer = Analyzer(self._packageName, self._jsonReport)
		self._coverage = analyzer.Convert()
		# self._coverage.Aggregate()

		container = nodes.container()

		if LegendPosition.top in self._legend:
			container += self._CreateLegend(identifier="legend1", classes=["report-doccov-legend"])

		container += self._GenerateCoverageTable()

		if LegendPosition.bottom in self._legend:
			container += self._CreateLegend(identifier="legend2", classes=["report-doccov-legend"])

		return [container]
