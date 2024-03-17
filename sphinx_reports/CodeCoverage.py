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
from typing  import Dict, Tuple, Any, List, Iterable, Mapping, Generator, TypedDict, Union, Optional as Nullable, \
	ClassVar

from docutils                              import nodes
from docutils.parsers.rst.directives       import flag
from sphinx.addnodes                       import toctree
from sphinx.application                    import Sphinx
from sphinx.config                         import Config
from sphinx.directives.code                import LiteralIncludeReader
from sphinx.util.docutils                  import new_document
from pyTooling.Decorators                  import export

from sphinx_reports.Common                 import ReportExtensionError, LegendStyle
from sphinx_reports.Sphinx                 import strip, BaseDirective
from sphinx_reports.DataModel.CodeCoverage import PackageCoverage, AggregatedCoverage, ModuleCoverage
from sphinx_reports.Adapter.Coverage       import Analyzer


class package_DictType(TypedDict):
	name:        str
	json_report: Path
	fail_below:  int
	levels:      Union[str, Dict[Union[int, str], Dict[str, str]]]


@export
class CodeCoverageBase(BaseDirective):
	option_spec = {
		"packageid": strip
	}

	defaultCoverageDefinitions = {
		"default": {
			30:      {"class": "report-cov-below30",  "desc": "almost unused"},
			50:      {"class": "report-cov-below50",  "desc": "poorly used"},
			80:      {"class": "report-cov-below80",  "desc": "somehow used"},
			90:      {"class": "report-cov-below90",  "desc": "well used"},
			100:     {"class": "report-cov-below100", "desc": "excellently used"},
			"error": {"class": "report-cov-error",    "desc": "internal error"},
		}
	}

	configPrefix:  str = "codecov"
	configValues:  Dict[str, Tuple[Any, str, Any]] = {
		f"{configPrefix}_packages": ({}, "env", Dict),
		f"{configPrefix}_levels": (defaultCoverageDefinitions, "env", Dict),
	}  #: A dictionary of all configuration values used by code coverage directives.

	_coverageLevelDefinitions: ClassVar[Dict[str, Dict[Union[int, str], Dict[str, str]]]] = {}
	_packageConfigurations:    ClassVar[Dict[str, package_DictType]] = {}

	_packageID:        str
	_levels:           Dict[Union[int, str], Dict[str, str]]

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
	def ReadReports(cls, sphinxApplication: Sphinx) -> None:
		"""
		Read code coverage report files.

		:param sphinxApplication:   Sphinx application instance.
		"""
		print(f"[REPORT] Reading code coverage reports ...")

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

		# try:
		# 	packageConfiguration = allPackages[self._packageID]
		# except KeyError as ex:
		# 	raise ReportExtensionError(f"conf.py: {ReportDomain.name}_{cls.configPrefix}_packages: No configuration found for '{self._packageID}'.") from ex

		for packageID, packageConfiguration in allPackages.items():
			configurationName = f"conf.py: {variableName}:[{packageID}]"

			try:
				packageName = packageConfiguration["name"]
			except KeyError as ex:
				raise ReportExtensionError(f"{configurationName}.name: Configuration is missing.") from ex

			try:
				jsonReport = Path(packageConfiguration["json_report"])
			except KeyError as ex:
				raise ReportExtensionError(f"{configurationName}.json_report: Configuration is missing.") from ex

			if not jsonReport.exists():
				raise ReportExtensionError(f"{configurationName}.json_report: Coverage report file '{jsonReport}' doesn't exist.") from FileNotFoundError(jsonReport)

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
					raise ReportExtensionError(
						f"{configurationName}.levels: Referenced coverage levels '{levels}' are not defined in conf.py variable '{variableName}'.") from ex
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
				"json_report": jsonReport,
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
class CodeCoverage(CodeCoverageBase):
	"""
	This directive will be replaced by a table representing code coverage.
	"""
	directiveName: str = "code-coverage"

	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = CodeCoverageBase.option_spec | {
		"no-branch-coverage": flag
	}

	_noBranchCoverage: bool
	_packageName:      str
	_jsonReport:       Path
	_failBelow:        float
	_coverage:         PackageCoverage

	def _CheckOptions(self) -> None:
		"""
		Parse all directive options or use default values.
		"""
		super()._CheckOptions()

		self._noBranchCoverage = "no-branch-coverage" in self.options

		packageConfiguration = self._packageConfigurations[self._packageID]
		self._packageName = packageConfiguration["name"]
		self._jsonReport =  packageConfiguration["json_report"]
		self._failBelow =   packageConfiguration["fail_below"]
		self._levels =      packageConfiguration["levels"]

	def _GenerateCoverageTable(self) -> nodes.table:
		# Create a table and table header with 10 columns
		columns = [
			("Package",   [(" Module", 500)], None),
			("Statments", [("Total", 100), ("Excluded", 100), ("Covered", 100), ("Missing", 100)], None),
			("Branches" , [("Total", 100), ("Covered", 100), ("Partial", 100), ("Missing", 100)], None),
			("Coverage",  [("in %", 100)], None)
		]

		if self._noBranchCoverage:
			columns.pop(2)

		table, tableGroup = self._CreateTableHeader(
			identifier=self._packageID,
			columns=columns,
			classes=["report-codecov-table"]
		)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		def sortedValues(d: Mapping[str, AggregatedCoverage]) -> Generator[AggregatedCoverage, None, None]:
			for key in sorted(d.keys()):
				yield d[key]

		def renderlevel(tableBody: nodes.tbody, packageCoverage: PackageCoverage, level: int = 0) -> None:
			tableRow = nodes.row("", classes=[
				"report-codecov-table-row",
				"report-codecov-package",
				self._ConvertToColor(packageCoverage.Coverage, "class")
			])
			tableBody += tableRow

			tableRow += nodes.entry("", nodes.paragraph(text=f"{' ' * level}📦{packageCoverage.Name}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.TotalStatements}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.ExcludedStatements}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.CoveredStatements}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.MissingStatements}"))
			if not self._noBranchCoverage:
				tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.TotalBranches}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.CoveredBranches}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.PartialBranches}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.MissingBranches}"))
			tableRow += nodes.entry("", nodes.paragraph(text=f"{packageCoverage.Coverage:.1%}"))

			for package in sortedValues(packageCoverage._packages):
				renderlevel(tableBody, package, level + 1)

			for module in sortedValues(packageCoverage._modules):
				tableRow = nodes.row("", classes=[
					"report-codecov-table-row",
					"report-codecov-module",
					self._ConvertToColor(module.Coverage, "class")
				])
				tableBody += tableRow

				tableRow += nodes.entry("", nodes.paragraph(text=f"{' ' * (level + 1)}  {module.Name}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{module.TotalStatements}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{module.ExcludedStatements}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{module.CoveredStatements}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{module.MissingStatements}"))
				if not self._noBranchCoverage:
					tableRow += nodes.entry("", nodes.paragraph(text=f"{module.TotalBranches}"))
					tableRow += nodes.entry("", nodes.paragraph(text=f"{module.CoveredBranches}"))
					tableRow += nodes.entry("", nodes.paragraph(text=f"{module.PartialBranches}"))
					tableRow += nodes.entry("", nodes.paragraph(text=f"{module.MissingBranches}"))
				tableRow += nodes.entry("", nodes.paragraph(text=f"{module.Coverage :.1%}"))

		renderlevel(tableBody, self._coverage)

		# Add a summary row
		tableRow = nodes.row("", classes=[
			"report-codecov-table-row",
			"report-codecov-summary",
			self._ConvertToColor(self._coverage.Coverage, "class")
		])
		tableBody += tableRow

		tableRow += nodes.entry("", nodes.paragraph(text=f"Overall ({self._coverage.FileCount} files):"))
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedExpected}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedCovered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedCovered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedCovered}")),
		if not self._noBranchCoverage:
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedCovered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedCovered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedCovered}")),
			tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedUncovered}")),
		tableRow += nodes.entry("", nodes.paragraph(text=f""))  # {self._coverage.AggregatedCoverage:.1%}")),

		return table

	def _CreatePages(self) -> None:
		def handlePackage(package: PackageCoverage) -> None:
			for pack in package._packages.values():
				if handlePackage(pack):
					return True

			for module in package._modules.values():
				if handleModule(module):
					return True

		def handleModule(module: ModuleCoverage) -> None:
			doc = new_document("dummy")

			rootSection = nodes.section(ids=["foo"])
			doc += rootSection

			title = nodes.title(text=f"{module.Name}")
			rootSection += title
			rootSection += nodes.paragraph(text="some text")

			docname = f"coverage/{module.Name}"
			self.env.titles[docname] = title
			self.env.longtitles[docname] = title

			return True

		handlePackage(self._coverage)

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()

		# Assemble a list of Python source files
		analyzer = Analyzer(self._packageName, self._jsonReport)
		self._coverage = analyzer.Convert()
		# self._coverage.Aggregate()

		self._CreatePages()

		container = nodes.container()
		container += self._GenerateCoverageTable()

		docName = self.env.docname
		docParent = docName[:docName.rindex("/")]

		subnode = toctree()
		subnode['parent'] = docName

		# (title, ref) pairs, where ref may be a document, or an external link,
		# and title may be None if the document's title is to be used
		subnode['entries'] =       []
		subnode['includefiles'] =  []
		subnode['maxdepth'] =      -1  # self.options.get('maxdepth', -1)
		subnode['caption'] =       None  # self.options.get('caption')
		subnode['glob'] =          None  # 'glob' in self.options
		subnode['hidden'] =        True  # 'hidden' in self.options
		subnode['includehidden'] = False  # 'includehidden' in self.options
		subnode['numbered'] =      0  # self.options.get('numbered', 0)
		subnode['titlesonly'] =    False  # 'titlesonly' in self.options
		self.set_source_info(subnode)

		wrappernode = nodes.compound(classes=['toctree-wrapper'])
		wrappernode.append(subnode)
		self.add_name(wrappernode)

		for entry in (
			"sphinx_reports",
			"sphinx_reports.Adapter",
			"sphinx_reports.Adapter.Coverage",
			"sphinx_reports.Adapter.DocStrCoverage",
			"sphinx_reports.Adapter.JUnit",
			"sphinx_reports.DataModel",
			"sphinx_reports.DataModel.CodeCoverage",
			"sphinx_reports.DataModel.DocumentationCoverage",
			"sphinx_reports.DataModel.Unittest",
			"sphinx_reports.static",
			"sphinx_reports.CodeCoverage",
			"sphinx_reports.Common",
			"sphinx_reports.DocCoverage",
			"sphinx_reports.Sphinx",
			"sphinx_reports.Unittest",
		):
			moduleDocumentName = f"{docParent}/{entry}"
			moduleDocumentTitle = entry

			subnode["entries"].append((moduleDocumentTitle, moduleDocumentName))
			subnode["includefiles"].append(moduleDocumentName)

		return [container, wrappernode]


@export
class CodeCoverageLegend(CodeCoverageBase):
	"""
	This directive will be replaced by a legend table representing coverage levels.
	"""
	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = CodeCoverageBase.option_spec | {
		"style": strip
	}

	directiveName: str = "code-coverage-legend"

	_style: LegendStyle

	def _CheckOptions(self) -> None:
		# Parse all directive options or use default values
		super()._CheckOptions()

		self._style = self._ParseLegendStyle("style", LegendStyle.horizontal_table)

		packageConfiguration = self._packageConfigurations[self._packageID]
		self._levels = packageConfiguration["levels"]

	def _CreateHorizontalLegendTable(self, identifier: str, classes: List[str]) -> nodes.table:
		columns = [("Code Coverage:", None, 300)]
		for level in self._levels:
			if isinstance(level, int):
				columns.append((f"≤{level} %", None, 200))

		table, tableGroup = self._CreateTableHeader(columns, identifier=identifier, classes=classes)
		tableBody = nodes.tbody()
		tableGroup += tableBody

		legendRow = nodes.row("", classes=["report-codecov-legend-row"])
		legendRow += nodes.entry("", nodes.paragraph(text="Coverage Level:"))
		tableBody += legendRow
		for level, config in self._levels.items():
			if isinstance(level, int):
				legendRow += nodes.entry("", nodes.paragraph(text=config["desc"]), classes=[self._ConvertToColor((level - 1) / 100, "class")])

		legendRow = nodes.row("", classes=["report-codecov-legend-row"])
		legendRow += nodes.entry("", nodes.paragraph(text="Coverage Level:"))
		tableBody += legendRow
		for level, config in self._levels.items():
			if isinstance(level, int):
				legendRow += nodes.entry("", nodes.paragraph(text=config["desc"]), classes=[self._ConvertToColor((level - 1) / 100, "class")])

		return table

	def _CreateVerticalLegendTable(self, identifier: str, classes: List[str]) -> nodes.table:
		table, tableGroup = self._CreateTableHeader([
				("Code Coverage", None, 300),
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
					classes=["report-codecov-legend-row", self._ConvertToColor((level - 1) / 100, "class")]
				)

		return table

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()

		container = nodes.container()
		if LegendStyle.Table in self._style:
			if LegendStyle.Horizontal in self._style:
				container += self._CreateHorizontalLegendTable(identifier=f"{self._packageID}-legend", classes=["report-codecov-legend"])
			elif LegendStyle.Vertical in self._style:
				container += self._CreateVerticalLegendTable(identifier=f"{self._packageID}-legend", classes=["report-codecov-legend"])
			else:
				container += nodes.paragraph(text=f"Unsupported legend style.")
		else:
			container += nodes.paragraph(text=f"Unsupported legend style.")

		return [container]



@export
class ModuleCoverage(CodeCoverageBase):
	"""
	This directive will be replaced by highlighted source code.
	"""
	directiveName: str = "module-coverage"

	has_content = False
	required_arguments = 0
	optional_arguments = 2

	option_spec = CodeCoverageBase.option_spec | {
		"module": strip
	}

	_packageName:      str
	_moduleName:       str
	_jsonReport:       Path

	def _CheckOptions(self) -> None:
		"""
		Parse all directive options or use default values.
		"""
		super()._CheckOptions()

		self._moduleName = self._ParseStringOption("module")

		packageConfiguration = self._packageConfigurations[self._packageID]
		self._packageName = packageConfiguration["name"]
		self._jsonReport =  packageConfiguration["json_report"]

	def run(self) -> List[nodes.Node]:
		self._CheckOptions()

		# Assemble a list of Python source files
		analyzer = Analyzer(self._packageName, self._jsonReport)
		self._coverage = analyzer.Convert()

		sourceFile = "../../sphinx_reports/__init__.py"

		container = nodes.container()
		container += nodes.paragraph(text=f"Code coverage of {self._moduleName}")

		location = self.state_machine.get_source_and_line(self.lineno)
		rel_filename, filename = self.env.relfn2path(sourceFile)
		self.env.note_dependency(rel_filename)

		reader = LiteralIncludeReader(filename, {"tab-width": 2}, self.config)
		text, lines = reader.read(location=location)

		literalBlock: nodes.Element = nodes.literal_block(text, text, source=filename)
		literalBlock["language"] = "codecov"
		literalBlock['highlight_args'] = extra_args = {}
		extra_args['hl_lines'] = [i for i in range(10, 20)]
		self.set_source_info(literalBlock)

		container += literalBlock

		return [container]
