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
**A Sphinx extension providing code coverage details embedded in documentation pages.**
"""
from pathlib import Path

from coverage.results             import Numbers
from pyTooling.Configuration.JSON import Configuration
from pyTooling.Decorators         import export, readonly

from sphinx_reports.Common                 import ReportExtensionError
from sphinx_reports.DataModel.CodeCoverage import PackageCoverage, ModuleCoverage, AggregatedCoverage


@export
class CodeCoverageError(ReportExtensionError):
	pass


@export
class Analyzer:
	_packageName:    str
	_coverageReport: Configuration

	def __init__(self, packageName: str, jsonCoverageFile: Path) -> None:
		if not jsonCoverageFile.exists():
			raise CodeCoverageError(f"JSON coverage report '{jsonCoverageFile}' not found.") from FileNotFoundError(jsonCoverageFile)

		self._packageName = packageName
		self._coverageReport = Configuration(jsonCoverageFile)

		# if int(self._coverageReport["format"]) != 2:
		# 	raise CodeCoverageError(f"File format of '{jsonCoverageFile}' is not supported.")

	@readonly
	def PackageName(self) -> str:
		return self._packageName

	@readonly
	def JSONCoverageFile(self) -> Path:
		return self._coverageReport.ConfigFile

	@readonly
	def CoverageReport(self) -> Configuration:
		return self._coverageReport

	def Convert(self) -> PackageCoverage:
		rootPackageCoverage = PackageCoverage(self._packageName, Path("__init__.py"))

		for statusRecord in self._coverageReport["files"]:
			moduleFile = Path(statusRecord.Key)
			coverageSummary = statusRecord["summary"]

			moduleName = moduleFile.stem
			modulePath = moduleFile.parent.parts[1:]

			currentCoverageObject: AggregatedCoverage = rootPackageCoverage
			for packageName in modulePath:
				try:
					currentCoverageObject = currentCoverageObject[packageName]
				except KeyError:
					currentCoverageObject = PackageCoverage(packageName, moduleFile, currentCoverageObject)

			if moduleName != "__init__":
				currentCoverageObject = ModuleCoverage(moduleName, moduleFile, currentCoverageObject)

			currentCoverageObject._totalStatements =    int(coverageSummary["num_statements"])
			currentCoverageObject._excludedStatements = int(coverageSummary["excluded_lines"])
			currentCoverageObject._coveredStatements =  int(coverageSummary["covered_lines"])
			currentCoverageObject._missingStatements =  int(coverageSummary["missing_lines"])

			currentCoverageObject._totalBranches =   int(coverageSummary["num_branches"])
			currentCoverageObject._coveredBranches = int(coverageSummary["covered_branches"])
			currentCoverageObject._partialBranches = int(coverageSummary["num_partial_branches"])
			currentCoverageObject._missingBranches = int(coverageSummary["missing_branches"])

			currentCoverageObject._coverage = float(coverageSummary["percent_covered"]) / 100.0

		return rootPackageCoverage
