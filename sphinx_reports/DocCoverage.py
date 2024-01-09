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
**Report documentation coverage as Sphinx documentation page(s).**
"""
from pathlib import Path
from typing  import Dict, Tuple, Any, List, Iterable, Mapping, Generator

from docutils             import nodes
from pyTooling.Decorators import export

from sphinx_reports.Common                          import ReportExtensionError
from sphinx_reports.Sphinx                          import strip, LegendPosition, BaseDirective
from sphinx_reports.DataModel.DocumentationCoverage import PackageCoverage
from sphinx_reports.Adapter.DocStrCoverage          import Analyzer


@export
class DocCoverage(BaseDirective):
	"""
	This directive will be replaced by a table representing documentation coverage.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = {
		"packageid": strip,
		"legend":    strip,
	}

	directiveName: str = "docstr-coverage"
	configPrefix:  str = "doccov"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		f"{configPrefix}_packages": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by this domain. (name: (default, rebuilt, type))

	_packageID:   str
	_legend:      LegendPosition
	_packageName: str
	_directory:   Path
	_failBelow:   float
	_levels:      Dict[int, Dict[str, str]]
	_coverage:    PackageCoverage

	def _CheckOptions(self):
		# Parse all directive options or use default values
		self._packageID = self._ParseStringOption("packageid")
		self._legend = self._ParseLegendOption("legend", LegendPosition.Bottom)

	def _CheckConfiguration(self):
		from sphinx_reports import ReportDomain

		# Check configuration fields and load necessary values
		try:
			allPackages = self.config[f"{ReportDomain.name}_{self.configPrefix}_packages"]
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
			self._directory = Path(packageConfiguration["directory"])
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.directory: Configuration is missing.") from ex

		if not self._directory.exists():
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.directory: Directory doesn't exist.") from FileNotFoundError(self._directory)

		try:
			self._failBelow = int(packageConfiguration["fail_below"]) / 100
		except KeyError as ex:
			raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.fail_below: Configuration is missing.") from ex

		if not (0.0 <= self._failBelow <= 100.0):
			raise ReportExtensionError(
				f"conf.py: {ReportDomain.name}_{self.configPrefix}_packages:{self._packageID}.fail_below: Is out of range 0..100.")

		self._levels = {
			30:  {"class": "doccov-below30",  "background": "rgba(101,  31, 255, .2)", "desc": "almost undocumented"},
			50:  {"class": "doccov-below50",  "background": "rgba(255,  82,  82, .2)", "desc": "poorly documented"},
			80:  {"class": "doccov-below80",  "background": "rgba(255, 145,   0, .2)", "desc": "roughly documented"},
			90:  {"class": "doccov-below90",  "background": "rgba(  0, 200,  82, .2)", "desc": "well documented"},
			100: {"class": "doccov-below100", "background": "rgba(  0, 200,  82, .2)", "desc": "excellent documented"},
		}

	def _ConvertToColor(self, currentLevel, configKey):
		for levelLimit, levelConfig in self._levels.items():
			if (currentLevel * 100) < levelLimit:
				return levelConfig[configKey]
		else:
			return self._levels[100][configKey]

	def _GenerateCoverageTable(self) -> nodes.table:
		# Create a table and table header with 5 columns
		table, tableGroup = self._PrepareTable(
			id=self._packageID,
			columns={
				"Filename": 500,
				"Total": 100,
				"Covered": 100,
				"Missing": 100,
				"Coverage in %": 100
			},
			classes=["doccov-table"]
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		def sortedValues(d: Mapping) -> Generator[Any, None, None]:
			for key in sorted(d.keys()):
				yield d[key]

		def renderlevel(tableBody: nodes.tbody, packageCoverage: PackageCoverage, level: int = 0):
			tableBody += nodes.row(
				"",
				nodes.entry("", nodes.paragraph(text=f"{' '*level}{packageCoverage.Name} ({packageCoverage.File})")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Expected}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Covered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Uncovered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Coverage:.1%}")),
				classes=["doccov-table-row", self._ConvertToColor(packageCoverage.Coverage, "class")],
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
					classes=["doccov-table-row", self._ConvertToColor(module.Coverage, "class")],
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
			classes=["doccov-summary-row", self._ConvertToColor(self._coverage.AggregatedCoverage, "class")]
		)

		return table

	def _CreateLegend(self, id: str, classes: Iterable[str]) -> List[nodes.Element]:
		rubric = nodes.rubric("", text="Legend")

		table = nodes.table("", id=id, classes=classes)

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
				classes=["doccov-legend-row", self._ConvertToColor((level - 1) / 100, "class")]
			)

		return [rubric, table]


@export
class DocStrCoverage(DocCoverage):
	def run(self):
		self._CheckOptions()
		self._CheckConfiguration()

		# Assemble a list of Python source files
		analyzer = Analyzer(self._directory, self._packageName)
		analyzer.Analyze()
		self._coverage = analyzer.Convert()
		# self._coverage.CalculateCoverage()
		self._coverage.Aggregate()

		container = nodes.container()

		if LegendPosition.Top in self._legend:
			container += self._CreateLegend(id="legend1", classes=["doccov-legend"])

		container += self._GenerateCoverageTable()

		if LegendPosition.Bottom in self._legend:
			container += self._CreateLegend(id="legend2", classes=["doccov-legend"])

		return [container]
