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
**Abstract documentation coverage data model for Python code.**
"""

from enum    import Flag
from pathlib import Path
from typing import Optional as Nullable, Iterable, Dict, Union, Tuple

from pyTooling.Decorators import export, readonly


@export
class Coverage:
	_name:      str
	_parent:    Nullable["Coverage"]

	def __init__(self, name: str, parent: Nullable["Coverage"] = None) -> None:
		self._name =   name
		self._parent = parent

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Parent(self) -> Nullable["Coverage"]:
		return self._parent


@export
class AggregatedCoverage(Coverage):
	_file:                Path

	def __init__(self, name: str, file: Path, parent: Nullable["Coverage"] = None) -> None:
		super().__init__(name, parent)
		self._file = file

	@readonly
	def File(self) -> Path:
		return self._file


@export
class ModuleCoverage(AggregatedCoverage):
	_coverage:  float

	def __init__(self, name: str, file: Path, parent: Nullable["PackageCoverage"] = None) -> None:
		super().__init__(name, file, parent)

		if parent is not None:
			parent._modules[name] = self

		self._coverage = -1.0

	@readonly
	def Coverage(self) -> float:
		return self._coverage


@export
class PackageCoverage(AggregatedCoverage):
	_fileCount: int

	_modules:   Dict[str, ModuleCoverage]
	_packages:  Dict[str, "PackageCoverage"]

	_coverage:  float

	def __init__(self, file: Path, name: str, parent: Nullable["PackageCoverage"] = None) -> None:
		super().__init__(name, file, parent)

		if parent is not None:
			parent._packages[name] = self

		self._fileCount = 1
		self._modules =   {}
		self._packages =  {}
		self._coverage = -1.0

	@readonly
	def FileCount(self) -> int:
		return self._fileCount

	@readonly
	def Modules(self) -> Dict[str, ModuleCoverage]:
		return self._modules

	@readonly
	def Packages(self) -> Dict[str, "PackageCoverage"]:
		return self._packages

	@readonly
	def Coverage(self) -> float:
		return self._coverage

	def __getitem__(self, key: str) -> Union["PackageCoverage", ModuleCoverage]:
		try:
			return self._modules[key]
		except KeyError:
			return self._packages[key]
