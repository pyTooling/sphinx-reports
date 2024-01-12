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
from pathlib import Path
from typing  import List

from docstr_coverage                   import analyze, ResultCollection
from docstr_coverage.result_collection import FileCount
from pyTooling.Decorators              import export, readonly

from sphinx_reports.Common                          import ReportExtensionError
from sphinx_reports.DataModel.DocumentationCoverage import ModuleCoverage, PackageCoverage, AggregatedCoverage


@export
class DocStrCoverageError(ReportExtensionError):
	pass


@export
class Analyzer:
	_packageName:     str
	_searchDirectory: Path
	_moduleFiles:     List[Path]
	_coverageReport:  ResultCollection

	def __init__(self, packageName: str, directory: Path) -> None:
		self._searchDirectory = directory
		self._packageName = packageName
		self._moduleFiles = []

		if directory.exists():
			self._moduleFiles.extend(directory.glob("**/*.py"))
		else:
			raise DocStrCoverageError(f"Package source directory '{directory}' does not exist.") \
				from FileNotFoundError(directory)

	@readonly
	def SearchDirectories(self) -> Path:
		return self._searchDirectory

	@readonly
	def PackageName(self) -> str:
		return self._packageName

	@readonly
	def ModuleFiles(self) -> List[Path]:
		return self._moduleFiles

	@readonly
	def CoverageReport(self) -> ResultCollection:
		return self._coverageReport

	def Analyze(self) -> ResultCollection:
		self._coverageReport: ResultCollection = analyze(self._moduleFiles, show_progress=False)
		return self._coverageReport

	def Convert(self) -> PackageCoverage:
		rootPackageCoverage = PackageCoverage(self._packageName, self._searchDirectory / "__init__.py")

		for key, value in self._coverageReport.files():
			path: Path = key.relative_to(self._searchDirectory)
			perFileResult: FileCount = value.count_aggregate()

			moduleName = path.stem
			modulePath = path.parent.parts

			currentCoverageObject: AggregatedCoverage = rootPackageCoverage
			for packageName in modulePath:
				try:
					currentCoverageObject = currentCoverageObject[packageName]
				except KeyError:
					currentCoverageObject = PackageCoverage(packageName, path, currentCoverageObject)

			if moduleName != "__init__":
				currentCoverageObject = ModuleCoverage(moduleName, path, currentCoverageObject)

			currentCoverageObject._expected = perFileResult.needed
			currentCoverageObject._covered = perFileResult.found
			currentCoverageObject._uncovered = perFileResult.missing

			if currentCoverageObject._expected != 0:
				currentCoverageObject._coverage = currentCoverageObject._covered / currentCoverageObject._expected
			else:
				currentCoverageObject._coverage = 1.0

			if currentCoverageObject._uncovered != currentCoverageObject._expected - currentCoverageObject._covered:
				currentCoverageObject._coverage = -2.0

		return rootPackageCoverage
