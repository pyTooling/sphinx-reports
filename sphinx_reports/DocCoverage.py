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
from pathlib              import Path
from typing               import Dict, Tuple, Any, List, Mapping, Generator, TypedDict, Union, ClassVar

from docutils             import nodes
from sphinx.application   import Sphinx
from sphinx.config        import Config
from pyTooling.Decorators import export
from pyEDAA.Reports.DocumentationCoverage.Python import DocStrCoverage as DocStrCovAnalyzer
from pyEDAA.Reports.DocumentationCoverage.Python import PackageCoverage, AggregatedCoverage

from sphinx_reports.Common                          import ReportExtensionError, LegendStyle
from sphinx_reports.Sphinx                          import strip, BaseDirective


class package_DictType(TypedDict):
	name:       str
	directory:  Path
	fail_below: int
	levels:     Union[str, Dict[Union[int, str], Dict[str, str]]]


@export
class DocCoverageBase(BaseDirective):
	option_spec = {
		"packageid": strip,
	}

	defaultCoverageDefinitions = {
		"default": {
			30:      {"class": "report-cov-below30",  "desc": "almost undocumented"},
			50:      {"class": "report-cov-below50",  "desc": "poorly documented"},
			80:      {"class": "report-cov-below80",  "desc": "roughly documented"},
			90:      {"class": "report-cov-below90",  "desc": "well documented"},
			100:     {"class": "report-cov-below100", "desc": "excellent documented"},
			"error": {"class": "report-cov-error",    "desc": "internal error"},
		}
	}

	configPrefix:  str = "doccov"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		f"{configPrefix}_packages": ({}, "env", Dict),
		f"{configPrefix}_levels": (defaultCoverageDefinitions, "env", Dict),
	}  #: A dictionary of all configuration values used by documentation coverage directives.

	_coverageLevelDefinitions: ClassVar[Dict[str, Dict[Union[int, str], Dict[str, str]]]] = {}
	_packageConfigurations:    ClassVar[Dict[str, package_DictType]] = {}

	_packageID:   str
	_levels:      Dict[Union[int, str], Dict[str, str]]

	def _CheckOptions(self) -> None:
		# Parse all directive options or use default values
		self._packageID = self._ParseStringOption("packageid")

	@classmethod
	def CheckConfiguration(cls, sphinxApplication: Sphinx, sphinxConfiguration: Config) -> None:
		"""
		Check configuration fields and load necessary values.

		:param sphinxApplication:   Sphinx application instance.
		:param sphinxConfiguration: Sphinx configuration instance.
		"""
		cls._CheckLevelsConfiguration(sphinxConfiguration)
		cls._CheckPackagesConfiguration(sphinxConfiguration)

	@classmethod
	def _CheckLevelsConfiguration(cls, sphinxConfiguration: Config) -> None:
		from sphinx_reports import ReportDomain

		variableName = f"{ReportDomain.name}_{cls.configPrefix}_levels"

		try:
			coverageLevelDefinitions: Dict[str, package_DictType] = sphinxConfiguration[f"{ReportDomain.name}_{cls.configPrefix}_levels"]
		except (KeyError, AttributeError) as ex:
			raise ReportExtensionError(f"Configuration option '{variableName}' is not configured.") from ex

		if "default" not in coverageLevelDefinitions:
			cls._coverageLevelDefinitions["default"] = cls.defaultCoverageDefinitions["default"]

		for key, coverageLevelDefinition in coverageLevelDefinitions.items():
			configurationName = f"conf.py: {variableName}:[{key}]"

			if 100 not in coverageLevelDefinition:
				raise ReportExtensionError(f"{configurationName}[100]: Configuration is missing.")
			elif "error" not in coverageLevelDefinition:
				raise ReportExtensionError(f"{configurationName}[error]: Configuration is missing.")

			cls._coverageLevelDefinitions[key] = {}

			for level, levelConfig in coverageLevelDefinition.items():
				try:
					if isinstance(level, str):
						if level != "error":
							raise ReportExtensionError(f"{configurationName}[{level}]: Level is a keyword, but not 'error'.")
					elif not (0.0 <= int(level) <= 100.0):
						raise ReportExtensionError(f"{configurationName}[{level}]: Level is out of range 0..100.")
				except ValueError as ex:
					raise ReportExtensionError(f"{configurationName}[{level}]: Level is not a keyword or an integer in range 0..100.") from ex

				try:
					cssClass = levelConfig["class"]
				except KeyError as ex:
					raise ReportExtensionError(f"{configurationName}[{level}].class: CSS class is missing.") from ex

				try:
					description = levelConfig["desc"]
				except KeyError as ex:
					raise ReportExtensionError(f"{configurationName}[{level}].desc: Description is missing.") from ex

				cls._coverageLevelDefinitions[key][level] = {
					"class": cssClass,
					"desc": description
				}

	@classmethod
	def _CheckPackagesConfiguration(cls, sphinxConfiguration: Config) -> None:
		from sphinx_reports import ReportDomain

		variableName = f"{ReportDomain.name}_{cls.configPrefix}_packages"

		try:
			allPackages: Dict[str, package_DictType] = sphinxConfiguration[f"{ReportDomain.name}_{cls.configPrefix}_packages"]
		except (KeyError, AttributeError) as ex:
			raise ReportExtensionError(f"Configuration option '{variableName}' is not configured.") from ex

		for packageID, packageConfiguration in allPackages.items():
			configurationName = f"conf.py: {variableName}:[{packageID}]"

			try:
				packageName = packageConfiguration["name"]
			except KeyError as ex:
				raise ReportExtensionError(f"{configurationName}.name: Configuration is missing.") from ex

			try:
				directory = Path(packageConfiguration["directory"])
			except KeyError as ex:
				raise ReportExtensionError(f"{configurationName}.directory: Configuration is missing.") from ex

			if not directory.exists():
				raise ReportExtensionError(f"{configurationName}.directory: Directory '{directory}' doesn't exist.") from FileNotFoundError(directory)

			try:
				failBelow = int(packageConfiguration["fail_below"]) / 100
			except KeyError as ex:
				raise ReportExtensionError(f"{configurationName}.fail_below: Configuration is missing.") from ex
			except ValueError as ex:
				raise ReportExtensionError(f"{configurationName}.fail_below: '{packageConfiguration['fail_below']}' is not an integer in range 0..100.") from ex

			if not (0.0 <= failBelow <= 100.0):
				raise ReportExtensionError(f"{configurationName}.fail_below: Is out of range 0..100.")

			try:
				levels = packageConfiguration["levels"]
			except KeyError as ex:
				raise ReportExtensionError(f"{configurationName}.levels: Configuration is missing.") from ex

			if isinstance(levels, str):
				try:
					levelDefinition = cls._coverageLevelDefinitions[levels]
				except KeyError as ex:
					raise ReportExtensionError(f"{configurationName}.levels: Referenced coverage levels '{levels}' are not defined in conf.py variable '{variableName}'.") from ex
			elif isinstance(levels, dict):
				if 100 not in packageConfiguration["levels"]:
					raise ReportExtensionError(f"{configurationName}.levels[100]: Configuration is missing.")
				elif "error" not in packageConfiguration["levels"]:
					raise ReportExtensionError(f"{configurationName}.levels[error]: Configuration is missing.")

				levelDefinition = {}
				for x, y in packageConfiguration["levels"].items():
					pass
			else:
				raise ReportExtensionError(f"")

			cls._packageConfigurations[packageID] = {
				"name": packageName,
				"directory": directory,
				"fail_below": failBelow,
				"levels": levelDefinition
			}

	def _ConvertToColor(self, currentLevel: float, configKey: str) -> str:
		if currentLevel < 0.0:
			return self._levels["error"][configKey]

		for levelLimit, levelConfig in self._levels.items():
			if isinstance(levelLimit, int) and (currentLevel * 100) < levelLimit:
				return levelConfig[configKey]

		return self._levels[100][configKey]


@export
class DocCoverage(DocCoverageBase):
	"""
	This directive will be replaced by a table representing documentation coverage.
	"""
	directiveName: str = "docstr-coverage"

	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = DocCoverageBase.option_spec

	_packageName: str
	_directory:   Path
	_failBelow:   float
	_coverage:    PackageCoverage

	def _CheckOptions(self) -> None:
		"""
		Parse all directive options or use default values.
		"""
		super()._CheckOptions()

		packageConfiguration = self._packageConfigurations[self._packageID]
		self._packageName = packageConfiguration["name"]
		self._directory =   packageConfiguration["directory"]
		self._failBelow =   packageConfiguration["fail_below"]
		self._levels =      packageConfiguration["levels"]

	def _GenerateCoverageTable(self) -> nodes.table:
		# Create a table and table header with 5 columns
		table, tableGroup = self._CreateTableHeader(
			identifier=self._packageID,
			columns=[
				("Filename", None, 500),
				("Total", None, 100),
				("Covered", None, 100),
				("Missing", None, 100),
				("Coverage in %", None, 100)
			],
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
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Expected}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Covered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Uncovered}")),
				nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Coverage:.1%}")),
				classes=[
					"report-doccov-table-row",
					"report-doccov-package",
					self._ConvertToColor(packageCoverage.Coverage, "class")
				],
			)

			for package in sortedValues(packageCoverage._packages):
				renderlevel(tableBody, package, level + 1)

			for module in sortedValues(packageCoverage._modules):
				tableBody += nodes.row(
					"",
					nodes.entry("", nodes.paragraph(text=f"{' '*(level+1)}  {module.Name}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Expected}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Covered}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Uncovered}")),
					nodes.entry("", nodes.paragraph(text=f"{module.Coverage :.1%}")),
					classes=[
						"report-doccov-table-row",
						"report-doccov-module",
						self._ConvertToColor(module.Coverage, "class")
					],
				)

		renderlevel(tableBody, self._coverage)

		# Add a summary row
		tableBody += nodes.row(
			"",
			nodes.entry("", nodes.paragraph(text=f"Overall ({self._coverage.FileCount} files):")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.AggregatedExpected}")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.AggregatedCovered}")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.AggregatedUncovered}")),
			nodes.entry("", nodes.paragraph(text=f"{self._coverage.AggregatedCoverage:.1%}"),
				# classes=[self._ConvertToColor(self._coverage.coverage(), "class")]
			),
			classes=[
				"report-doccov-table-row",
				"report-doccov-summary",
				self._ConvertToColor(self._coverage.AggregatedCoverage, "class")
			]
		)

		return table


@export
class DocStrCoverage(DocCoverage):
	def run(self) -> List[nodes.Node]:
		self._CheckOptions()

		# Assemble a list of Python source files
		docStrCov = DocStrCovAnalyzer(self._packageName, self._directory)
		docStrCov.Analyze()
		self._coverage = docStrCov.Convert()
		# self._coverage.CalculateCoverage()
		self._coverage.Aggregate()

		container = nodes.container()
		container += self._GenerateCoverageTable()

		return [container]


@export
class DocCoverageLegend(DocCoverageBase):
	"""
	This directive will be replaced by a legend table representing coverage levels.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = DocCoverageBase.option_spec | {
		"style": strip
	}

	directiveName: str = "doc-coverage-legend"

	_style: LegendStyle

	def _CheckOptions(self) -> None:
		# Parse all directive options or use default values
		super()._CheckOptions()

		self._style = self._ParseLegendStyle("style", LegendStyle.horizontal_table)

		packageConfiguration = self._packageConfigurations[self._packageID]
		self._levels = packageConfiguration["levels"]

	def _CreateHorizontalLegendTable(self, identifier: str, classes: List[str]) -> nodes.table:
		columns = [("Documentation Coverage:", None, 300)]
		for level in self._levels:
			if isinstance(level, int):
				columns.append((f"≤{level} %", None, 200))

		table, tableGroup = self._CreateTableHeader(columns, identifier=identifier, classes=classes)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		legendRow = nodes.row("", classes=["report-doccov-legend-row"])
		legendRow += nodes.entry("", nodes.paragraph(text="Coverage Level:"))
		tableBody += legendRow
		for level, config in self._levels.items():
			if isinstance(level, int):
				legendRow += nodes.entry("", nodes.paragraph(text=config["desc"]), classes=[self._ConvertToColor((level - 1) / 100, "class")])

		return table

	def _CreateVerticalLegendTable(self, identifier: str, classes: List[str]) -> nodes.table:
		table, tableGroup = self._CreateTableHeader([
				("Documentation Coverage", None, 300),
				("Coverage Level", None, 300)
			],
			identifier=identifier,
			classes=classes
		)

		tableBody = nodes.tbody()
		tableGroup += tableBody

		for level, config in self._levels.items():
			if isinstance(level, int):
				tableBody += nodes.row(
					"",
					nodes.entry("", nodes.paragraph(text=f"≤{level} %")),
					nodes.entry("", nodes.paragraph(text=config["desc"])),
					classes=["report-doccov-legend-row", self._ConvertToColor((level - 1) / 100, "class")]
				)

		return table

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()

		container = nodes.container()
		if LegendStyle.Table in self._style:
			if LegendStyle.Horizontal in self._style:
				container += self._CreateHorizontalLegendTable(identifier=f"{self._packageID}-legend", classes=["report-doccov-legend"])
			elif LegendStyle.Vertical in self._style:
				container += self._CreateVerticalLegendTable(identifier=f"{self._packageID}-legend", classes=["report-doccov-legend"])
			else:
				container += nodes.paragraph(text=f"Unsupported legend style.")
		else:
			container += nodes.paragraph(text=f"Unsupported legend style.")

		return [container]
