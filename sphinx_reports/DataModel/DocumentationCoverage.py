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
from typing  import Optional as Nullable, Iterable, Dict, Union

from pyTooling.Decorators import export, readonly


@export
class CoverageState(Flag):
	Unknown = 0
	Covered = 1
	Empty = 2

	Weak = 16
	Detailed = 32

	Parameters = 128
	ReturnValue = 256
	Exceptions = 512
	TypeHints = 1024

	Ignored = 4096
	Excluded = 8192


@export
class Coverage:
	_name:      str
	_parent:    "Coverage"

	_total:     int
	_excluded:  int
	_ignored:   int
	_expected:  int
	_covered:   int
	_uncovered: int

	_coverage:  float

	def __init__(self, name: str, parent: Nullable["Coverage"] = None):
		self._name =   name
		self._parent = parent

		self._total =     0
		self._excluded =  0
		self._ignored =   0
		self._expected =  0
		self._covered =   0
		self._uncovered = 0

		self._coverage = -1.0

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Parent(self) -> "Coverage":
		return self._parent

	@readonly
	def Total(self) -> int:
		return self._total

	@readonly
	def Excluded(self) -> int:
		return self._excluded

	@readonly
	def Ignored(self) -> int:
		return self._ignored

	@readonly
	def Expected(self) -> int:
		return self._expected

	@readonly
	def Covered(self) -> int:
		return self._covered

	@readonly
	def Uncovered(self) -> int:
		return self._uncovered

	@readonly
	def Coverage(self) -> float:
		return self._coverage

	def CalculateCoverage(self):
		self._uncovered = self._expected - self._covered
		if self._expected != 0:
			self._coverage = self._covered / self._expected
		else:
			self._coverage = 1.0

	def _CountCoverage(self, iterator: Iterable[CoverageState]):
		total =    0
		excluded = 0
		ignored =  0
		expected = 0
		covered =  0
		for coverageState in iterator:
			if coverageState is CoverageState.Unknown:
				raise Exception(f"")

			total += 1

			if CoverageState.Excluded in coverageState:
				excluded += 1
			elif CoverageState.Ignored in coverageState:
				ignored += 1

			expected += 1
			if CoverageState.Covered in coverageState:
				covered += 1

		return total, excluded, ignored, expected, covered


@export
class AggregatedCoverage(Coverage):
	_aggregatedTotal:     int
	_aggregatedExcluded:  int
	_aggregatedIgnored:   int
	_aggregatedExpected:  int
	_aggregatedCovered:   int
	_aggregatedUncovered: int

	_aggregatedCoverage:  float

	@readonly
	def AggregatedTotal(self) -> int:
		return self._aggregatedTotal

	@readonly
	def AggregatedExcluded(self) -> int:
		return self._aggregatedExcluded

	@readonly
	def AggregatedIgnored(self) -> int:
		return self._aggregatedIgnored

	@readonly
	def AggregatedExpected(self) -> int:
		return self._aggregatedExpected

	@readonly
	def AggregatedCovered(self) -> int:
		return self._aggregatedCovered

	@readonly
	def AggregatedUncovered(self) -> int:
		return self._aggregatedUncovered

	@readonly
	def AggregatedCoverage(self) -> float:
		return self._aggregatedCoverage

	def Aggregate(self) -> None:
		assert self._aggregatedUncovered == self._aggregatedExpected - self._aggregatedCovered

		if self._aggregatedExpected != 0:
			self._aggregatedCoverage = self._aggregatedCovered / self._aggregatedExpected
		else:
			self._aggregatedCoverage = 1.0


@export
class ClassCoverage(Coverage):
	_fields:  Dict[str, CoverageState]
	_methods: Dict[str, CoverageState]
	_classes: Dict[str, "ClassCoverage"]

	def __init__(self, name: str, parent: Union["PackageCoverage", "ClassCoverage", None] = None):
		super().__init__(name, parent)

		if parent is not None:
			parent._classes[name] = self

		self._fields =  {}
		self._methods = {}
		self._classes = {}

	def CalculateCoverage(self):
		for cls in self._classes.values():
			cls.CalculateCoverage()

		self._total, self._excluded, self._ignored, self._expected, self._covered = \
			self._CountCoverage(zip(
				self._fields.values(),
				self._methods.values()
			))

		super().CalculateCoverage()


@export
class ModuleCoverage(AggregatedCoverage):
	_file:      Path
	_name:      str
	_variables: Dict[str, CoverageState]
	_functions: Dict[str, CoverageState]
	_classes:   Dict[str, ClassCoverage]

	def __init__(self, file: Path, name: str, parent: Nullable["PackageCoverage"] = None):
		super().__init__(name, parent)

		if parent is not None:
			parent._modules[name] = self

		self._file =      file
		self._name =      name
		self._variables = {}
		self._functions = {}
		self._classes =   {}

	@readonly
	def File(self) -> Path:
		return self._file

	def CalculateCoverage(self):
		for cls in self._classes.values():
			cls.CalculateCoverage()

		self._total, self._excluded, self._ignored, self._expected, self._covered = \
			self._CountCoverage(zip(
				self._variables.values(),
				self._functions.values()
			))

		super().CalculateCoverage()

	def Aggregate(self) -> None:
		self._aggregatedTotal =     self._total
		self._aggregatedExcluded =  self._excluded
		self._aggregatedIgnored =   self._ignored
		self._aggregatedExpected =  self._expected
		self._aggregatedCovered =   self._covered
		self._aggregatedUncovered = self._uncovered

		for cls in self._classes.values():
			self._aggregatedTotal +=     cls._total
			self._aggregatedExcluded +=  cls._excluded
			self._aggregatedIgnored +=   cls._ignored
			self._aggregatedExpected +=  cls._expected
			self._aggregatedCovered +=   cls._covered
			self._aggregatedUncovered += cls._uncovered

		super().Aggregate()


@export
class PackageCoverage(AggregatedCoverage):
	_file:      Path
	_fileCount: int
	_variables: Dict[str, CoverageState]
	_functions: Dict[str, CoverageState]
	_classes:   Dict[str, ClassCoverage]
	_modules:   Dict[str, ModuleCoverage]
	_packages:  Dict[str, "PackageCoverage"]

	def __init__(self, file: Path, name: str, parent: Nullable["PackageCoverage"] = None):
		super().__init__(name, parent)

		if parent is not None:
			parent._packages[name] = self

		self._file =      file
		self._fileCount = 1
		self._variables = {}
		self._functions = {}
		self._classes =   {}
		self._modules =   {}
		self._packages =  {}

	@readonly
	def File(self) -> Path:
		return self._file

	@readonly
	def FileCount(self) -> int:
		return self._fileCount

	def __getitem__(self, key: str) -> Union["PackageCoverage", ModuleCoverage]:
		try:
			return self._modules[key]
		except KeyError:
			return self._packages[key]

	def CalculateCoverage(self):
		for cls in self._classes.values():
			cls.CalculateCoverage()

		for mod in self._modules.values():
			mod.CalculateCoverage()

		for pkg in self._packages.values():
			pkg.CalculateCoverage()

		self._total, self._excluded, self._ignored, self._expected, self._covered = \
			self._CountCoverage(zip(
				self._variables.values(),
				self._functions.values()
			))

		super().CalculateCoverage()

	def Aggregate(self) -> None:
		self._fileCount =           len(self._modules) + 1
		self._aggregatedTotal =     self._total
		self._aggregatedExcluded =  self._excluded
		self._aggregatedIgnored =   self._ignored
		self._aggregatedExpected =  self._expected
		self._aggregatedCovered =   self._covered
		self._aggregatedUncovered = self._uncovered

		for pkg in self._packages.values():
			pkg.Aggregate()
			self._fileCount +=           pkg._fileCount
			self._aggregatedTotal +=     pkg._total
			self._aggregatedExcluded +=  pkg._excluded
			self._aggregatedIgnored +=   pkg._ignored
			self._aggregatedExpected +=  pkg._expected
			self._aggregatedCovered +=   pkg._covered
			self._aggregatedUncovered += pkg._uncovered

		for mod in self._modules.values():
			mod.Aggregate()
			self._aggregatedTotal +=     mod._total
			self._aggregatedExcluded +=  mod._excluded
			self._aggregatedIgnored +=   mod._ignored
			self._aggregatedExpected +=  mod._expected
			self._aggregatedCovered +=   mod._covered
			self._aggregatedUncovered += mod._uncovered

		super().Aggregate()