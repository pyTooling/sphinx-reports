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
# Copyright 2023-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from pathlib import Path
from typing  import Optional as Nullable, Dict, Union, Generic, TypeVar

from pyTooling.Decorators                        import export, readonly
from pyEDAA.Reports.DocumentationCoverage.Python import PackageCoverage


_ParentType = TypeVar("_ParentType", bound="Base")


@export
class Base(Generic[_ParentType]):
	_name:      str
	_parent:    Nullable[_ParentType]

	def __init__(self, name: str, parent: Nullable[_ParentType] = None) -> None:
		self._name =   name
		self._parent = parent

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Parent(self) -> Nullable[_ParentType]:
		return self._parent


@export
class Coverage(Base[_ParentType], Generic[_ParentType]):
	_file:               Path

	_totalStatements:    int
	_excludedStatements: int
	_coveredStatements:  int
	_missingStatements:  int
	_totalBranches:      int
	_partialBranches:    int

	_coverage:           float

	def __init__(self, name: str, file: Path, parent: Nullable[_ParentType] = None) -> None:
		super().__init__(name, parent)
		self._file = file

		self._totalStatements =    0
		self._excludedStatements = 0
		self._coveredStatements =  0
		self._missingStatements =  0

		self._totalBranches =      0
		self._coveredBranches =    0
		self._partialBranches =    0
		self._missingBranches =    0

		self._coverage = -1.0

	@readonly
	def File(self) -> Path:
		return self._file

	@readonly
	def TotalStatements(self) -> int:
		return self._totalStatements

	@readonly
	def ExcludedStatements(self) -> int:
		return self._excludedStatements

	@readonly
	def CoveredStatements(self) -> int:
		return self._coveredStatements

	@readonly
	def MissingStatements(self) -> int:
		return self._missingStatements

	@readonly
	def StatementCoverage(self) -> float:
		if self._totalStatements <= 0:
			return 0.0

		return self._coveredStatements / self._totalStatements

	@readonly
	def TotalBranches(self) -> int:
		return self._totalBranches

	@readonly
	def CoveredBranches(self) -> int:
		return self._coveredBranches

	@readonly
	def PartialBranches(self) -> int:
		return self._partialBranches

	@readonly
	def MissingBranches(self) -> int:
		return self._missingBranches

	@readonly
	def BranchCoverage(self) -> float:
		if self._totalBranches <= 0:
			return 0.0

		return (self._coveredBranches + self._partialBranches) / self._totalBranches

	@readonly
	def Coverage(self) -> float:
		return self._coverage


@export
class ModuleCoverage(Coverage["PackageCoverage"]):
	def __init__(self, name: str, file: Path, parent: Nullable["PackageCoverage"] = None) -> None:
		super().__init__(name, file, parent)

		if parent is not None:
			parent._modules[name] = self


@export
class PackageCoverage(Coverage["PackageCoverage"]):
	_modules:   Dict[str, ModuleCoverage]
	_packages:  Dict[str, "PackageCoverage"]

	def __init__(self, name: str, file: Path, parent: Nullable["PackageCoverage"] = None) -> None:
		super().__init__(name, file, parent)

		if parent is not None:
			parent._packages[name] = self

		self._modules =   {}
		self._packages =  {}

	@readonly
	def FileCount(self) -> int:
		return self.TotalModuleCount

	@readonly
	def PackageCount(self) -> int:
		return len(self._packages)

	@readonly
	def ModuleCount(self) -> int:
		return 1 + len(self._modules)

	@readonly
	def TotalPackageCount(self) -> int:
		return 1 + sum(p.TotalPackageCount for p in self._packages.values())

	@readonly
	def TotalModuleCount(self) -> int:
		return 1 + sum(p.TotalModuleCount for p in self._packages.values()) + len(self._modules)

	@readonly
	def Packages(self) -> Dict[str, "PackageCoverage"]:
		return self._packages

	@readonly
	def Modules(self) -> Dict[str, ModuleCoverage]:
		return self._modules

	@readonly
	def AggregatedTotalStatements(self) -> int:
		return (
			self._totalStatements +
			sum(p.AggregatedTotalStatements for p in self._packages.values()) +
			sum(m._totalStatements for m in self._modules.values())
		)

	@readonly
	def AggregatedExcludedStatements(self) -> int:
		return (
			self._excludedStatements +
			sum(p.AggregatedExcludedStatements for p in self._packages.values()) +
			sum(m._excludedStatements for m in self._modules.values())
		)

	@readonly
	def AggregatedCoveredStatements(self) -> int:
		return (
			self._coveredStatements +
			sum(p.AggregatedCoveredStatements for p in self._packages.values()) +
			sum(m._coveredStatements for m in self._modules.values())
		)

	@readonly
	def AggregatedMissingStatements(self) -> int:
		return (
			self._missingStatements +
			sum(p.AggregatedMissingStatements for p in self._packages.values()) +
			sum(m._missingStatements for m in self._modules.values())
		)

	@readonly
	def AggregatedStatementCoverage(self) -> float:
		return self.AggregatedCoveredStatements / self.AggregatedTotalStatements

	@readonly
	def AggregatedTotalBranches(self) -> int:
		return (
			self._totalBranches +
			sum(p.AggregatedTotalBranches for p in self._packages.values()) +
			sum(m._totalBranches for m in self._modules.values())
		)

	@readonly
	def AggregatedCoveredBranches(self) -> int:
		return (
			self._coveredBranches +
			sum(p.AggregatedCoveredBranches for p in self._packages.values()) +
			sum(m._coveredBranches for m in self._modules.values())
		)

	@readonly
	def AggregatedPartialBranches(self) -> int:
		return (
			self._partialBranches +
			sum(p.AggregatedPartialBranches for p in self._packages.values()) +
			sum(m._partialBranches for m in self._modules.values())
		)

	@readonly
	def AggregatedMissingBranches(self) -> int:
		return (
			self._missingBranches +
			sum(p.AggregatedMissingBranches for p in self._packages.values()) +
			sum(m._missingBranches for m in self._modules.values())
		)

	@readonly
	def AggregatedBranchCoverage(self) -> float:
		return (self.AggregatedCoveredBranches + self.AggregatedPartialBranches) / self.AggregatedTotalBranches

	def __getitem__(self, key: str) -> Union["PackageCoverage", ModuleCoverage]:
		try:
			return self._modules[key]
		except KeyError:
			return self._packages[key]
