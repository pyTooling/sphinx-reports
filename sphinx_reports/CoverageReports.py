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
**A Sphinx extension providing coverage details embedded in documentation pages.**
"""
from enum    import Flag
from re      import match
from pathlib import Path
from sys     import version_info
from typing  import Dict, Tuple, Any, List, Optional as Nullable, Iterable, Mapping, Generator

from docutils             import nodes
from pyTooling.Decorators import export
from sphinx.application   import Sphinx
from sphinx.directives    import ObjectDescription

from sphinx_reports.DataModel      import PackageCoverage
from sphinx_reports.DocStrCoverage import Analyzer


@export
class ExtensionError(Exception):
	# WORKAROUND: for Python <3.11
	# Implementing a dummy method for Python versions before
	__notes__: List[str]
	if version_info < (3, 11):  # pragma: no cover
		def add_note(self, message: str):
			try:
				self.__notes__.append(message)
			except AttributeError:
				self.__notes__ = [message]


@export
def strip(option: str):
	return option.strip().lower()


@export
class LegendPosition(Flag):
	NoLegend = 0
	Top = 1
	Bottom = 2
	Both = 3


@export
class BaseDirective(ObjectDescription):
	has_content: bool = False
	"""
	A boolean; ``True`` if content is allowed.

	Client code must handle the case where content is required but not supplied (an empty content list will be supplied).
	"""

	required_arguments = 0
	"""Number of required directive arguments."""

	optional_arguments = 0
	"""Number of optional arguments after the required arguments."""

	final_argument_whitespace = False
	"""A boolean, indicating if the final argument may contain whitespace."""

	option_spec = None
	"""
	Mapping of option names to validator functions.

	A dictionary, mapping known option names to conversion functions such as :class:`int` or :class:`float`
	(default: {}, no options). Several conversion functions are defined in the ``directives/__init__.py`` module.

	Option conversion functions take a single parameter, the option argument (a string or :class:`None`), validate it
	and/or convert it to the appropriate form. Conversion functions may raise :exc:`ValueError` and
	:exc:`TypeError` exceptions.
	"""

	directiveName: str

	def _ParseBooleanOption(self, optionName: str, default: Nullable[bool] = None) -> bool:
		try:
			option = self.options[optionName]
		except KeyError as ex:
			if default is not None:
				return default
			else:
				raise ExtensionError(f"{self.directiveName}: Required option '{optionName}' not found for directive.") from ex

		if option in ("yes", "true"):
			return True
		elif option in ("no", "false"):
			return False
		else:
			raise ExtensionError(f"{self.directiveName}::{optionName}: '{option}' not supported for a boolean value (yes/true, no/false).")

	def _ParseStringOption(self, optionName: str, default: Nullable[str] = None, regexp: str = "\\w+") -> str:
		try:
			option = self.options[optionName]
		except KeyError as ex:
			if default is not None:
				return default
			else:
				raise ExtensionError(f"{self.directiveName}: Required option '{optionName}' not found for directive.") from ex

		if match(regexp, option):
			return option
		else:
			raise ExtensionError(f"{self.directiveName}::{optionName}: '{option}' not an accepted value for regexp '{regexp}'.")

	def _ParseLegendOption(self, optionName: str, default: Nullable[LegendPosition] = None) -> LegendPosition:
		try:
			option = self.options[optionName]
		except KeyError as ex:
			if default is not None:
				return default
			else:
				raise ExtensionError(f"{self.directiveName}: Required option '{optionName}' not found for directive.") from ex

		try:
			return LegendPosition[option]
		except KeyError as ex:
			raise ExtensionError(f"{self.directiveName}::{optionName}: Value '{option}' is not a valid member of 'LegendPosition'.") from ex

	def _PrepareTable(self, columns: Dict[str, int], id: str, classes: List[str]) -> Tuple[nodes.table, nodes.tgroup]:
		table = nodes.table("", id=id, classes=classes)

		tableGroup = nodes.tgroup(cols=(len(columns)))
		table += tableGroup

		tableRow = nodes.row()
		for columnTitle, width in columns.items():
			tableGroup += nodes.colspec(colwidth=width)
			tableRow += nodes.entry("", nodes.paragraph(text=columnTitle))

		tableGroup += nodes.thead("", tableRow)

		return table, tableGroup


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
		"legend": strip,
	}

	directiveName: str = "docstr-coverage"
	configPrefix: str = "doccov"
	configValues: Dict[str, Tuple[Any, str, Any]] = {
		"packages": ({}, "env", Dict)
	}  #: A dictionary of all configuration values used by this domain. (name: (default, rebuilt, type))

	_packageID: str
	_legend:    LegendPosition
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
		# Check configuration fields and load necessary values
		try:
			allPackages = self.config[f"{self.configPrefix}_packages"]
		except (KeyError, AttributeError) as ex:
			raise ExtensionError(f"Configuration option '{self.configPrefix}_packages' is not configured.") from ex

		try:
			packageConfiguration = allPackages[self._packageID]
		except KeyError as ex:
			raise ExtensionError(f"conf.py: {self.configPrefix}_packages: No configuration found for '{self._packageID}'.") from ex

		try:
			self._packageName = packageConfiguration["name"]
		except KeyError as ex:
			raise ExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.name: Configuration is missing.") from ex

		try:
			self._directory = Path(packageConfiguration["directory"])
		except KeyError as ex:
			raise ExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.directory: Configuration is missing.") from ex

		if not self._directory.exists():
			raise ExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.directory: Directory doesn't exist.") from FileNotFoundError(self._directory)

		try:
			self._failBelow = int(packageConfiguration["fail_below"]) / 100
		except KeyError as ex:
			raise ExtensionError(f"conf.py: {self.configPrefix}_packages:{self._packageID}.fail_below: Configuration is missing.") from ex

		if not (0.0 <= self._failBelow <= 100.0):
			raise ExtensionError(
				f"conf.py: {self.configPrefix}_packages:{self._packageID}.fail_below: Is out of range 0..100.")

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
					nodes.entry("", nodes.paragraph(text=f"{module.Coverage:.1%}")),
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


@export
def setup(sphinxApplication: Sphinx):
	"""
	Extension setup function registering the VHDL domain in Sphinx.

	:param sphinxApplication: The Sphinx application.
	:return:                  Dictionary containing the extension version and some properties.
	"""
	sphinxApplication.add_directive("doc-coverage", DocStrCoverage)

	for configName, (configDefault, configRebuilt, configTypes) in DocStrCoverage.configValues.items():
		sphinxApplication.add_config_value(f"{DocStrCoverage.configPrefix}_{configName}", configDefault, configRebuilt, configTypes)

	return {
		"version": __version__,                          # version of the extension
		"env_version": int(__version__.split(".")[0]),   # version of the data structure stored in the environment
		'parallel_read_safe': False,                     # Not yet evaluated, thus false
		'parallel_write_safe': True,                     # Internal data structure is used read-only, thus no problems will occur by parallel writing.
	}
