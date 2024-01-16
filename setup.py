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
"""Package installer for 'A Sphinx extension providing reports and summaries embedded in documentation pages'."""
from setuptools          import setup

from pathlib             import Path
from pyTooling.Packaging import DescribePythonPackageHostedOnGitHub, DEFAULT_CLASSIFIERS

gitHubNamespace =        "pyTooling"
packageName =            "sphinx_reports"
packageDirectory =       packageName.replace(".", "/")
packageInformationFile = Path(f"{packageDirectory}/__init__.py")

setup(**DescribePythonPackageHostedOnGitHub(
	packageName=packageName,
	description="A Sphinx extension providing reports and summaries embedded in documentation pages.",
	gitHubNamespace=gitHubNamespace,
	sourceFileWithVersion=packageInformationFile,
	classifiers=list(DEFAULT_CLASSIFIERS) + [
		"Framework :: Sphinx",
		"Framework :: Sphinx :: Domain",
		"Framework :: Sphinx :: Extension",
		"Topic :: Documentation :: Sphinx",
		"Topic :: Software Development :: Documentation",
		"Topic :: Software Development :: Quality Assurance",
		"Topic :: Software Development :: Testing :: Unit",
	],
	developmentStatus="beta",
	pythonVersions=("3.9", "3.10", "3.11", "3.12"),
	dataFiles={
		"sphinx_reports": ["static/*.css"]
	}
))
