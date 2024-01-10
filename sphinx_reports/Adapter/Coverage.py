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

from pyTooling.Configuration.JSON import Configuration
from pyTooling.Decorators              import export, readonly

from sphinx_reports.Common                          import ReportExtensionError
from sphinx_reports.DataModel.DocumentationCoverage import ModuleCoverage, PackageCoverage, AggregatedCoverage


@export
class CodeCoverageError(ReportExtensionError):
	pass


@export
class Analyzer:
	_packageName: str
	_htmlReportDirectory: Path

	def __init__(self, htmlReportDirectory: Path, packageName: str):
		self._packageName = packageName
		self._htmlReportDirectory = htmlReportDirectory

		self._ReadReportStatus(self._htmlReportDirectory / "status.json")

	def _ReadReportStatus(self, jsonFile: Path):
		status = Configuration(jsonFile)

		if int(status["format"]) != 2:
			raise CodeCoverageError(f"File format of '{jsonFile}' is not supported.")

		for statusRecord in status["files"]:
			fileID = statusRecord.Key

			moduleFile = Path(statusRecord["index"]["relative_filename"])
			reportFile = Path(statusRecord["index"]["html_filename"])
			coverageStatus = [int(i) for i in statusRecord["index"]["nums"]]

			print(fileID, moduleFile, reportFile, coverageStatus)
