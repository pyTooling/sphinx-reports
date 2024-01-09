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
from sys     import version_info
from typing  import List

from docstr_coverage                   import analyze, ResultCollection
from docstr_coverage.result_collection import FileCount
from pyTooling.Decorators              import export, readonly

from sphinx_reports.Common                          import ReportExtensionError
from sphinx_reports.DataModel.DocumentationCoverage import ModuleCoverage, PackageCoverage


@export
class DocStrCoverageError(ReportExtensionError):
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
class Analyzer:
	_searchDirectory: Path
	_packageName:     str
	_moduleFiles:     List[Path]
	_coverageReport:  str

	def __init__(self, directory: Path, packageName: str):
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
		self._coverageReport: ResultCollection = analyze(self._moduleFiles)
		return self._coverageReport

	def Convert(self) -> PackageCoverage:
		rootPackageCoverage = PackageCoverage(self._searchDirectory / "__init__.py", self._packageName)

		for key, value in self._coverageReport.files():
			path: Path = key.relative_to(self._searchDirectory)
			perFileResult: FileCount = value.count_aggregate()

			moduleName = path.stem
			modulePath = [p.name for p in path.parents]

			currentCoverageObject = rootPackageCoverage
			for packageName in modulePath[1:]:
				try:
					currentCoverageObject = currentCoverageObject[packageName]
				except KeyError:
					currentCoverageObject = PackageCoverage(path, packageName, currentCoverageObject)

			if moduleName != "__init__":
				currentCoverageObject = ModuleCoverage(path, moduleName, currentCoverageObject)

			currentCoverageObject._expected = perFileResult.needed
			currentCoverageObject._covered = perFileResult.found
			currentCoverageObject._uncovered = perFileResult.missing
			currentCoverageObject._coverage = perFileResult.coverage()

		return rootPackageCoverage
