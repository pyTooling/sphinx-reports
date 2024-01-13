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

from enum   import Flag
from typing import Optional as Nullable, Iterable, Dict, Union, Tuple, List

from pyTooling.Decorators import export, readonly


@export
class TestState(Flag):
	Unknown = 0
	Passed = 1
	Failed = 2
	Skipped = 3


@export
class Base:
	_name:       str

	def __init__(self, name: str) -> None:
		self._name = name

	@readonly
	def Name(self) -> str:
		return self._name


@export
class Test(Base):
	def __init__(self, name: str) -> None:
		super().__init__(name)


@export
class Testcase(Base):
	_tests: Dict[str, Test]

	def __init__(self, name: str) -> None:
		super().__init__(name)

		self._tests = {}


@export
class TestsuiteBase(Base):
	_testsuites: Dict[str, "Testsuite"]

	def __init__(self, name: str) -> None:
		super().__init__(name)

		self._testsuites = {}

	def __getitem__(self, key: str) -> "Testsuite":
		return self._testsuites[key]

	def __contains__(self, key: str) -> bool:
		return key in self._testsuites

	@readonly
	def Testsuites(self) -> Dict[str, "Testsuite"]:
		return self._testsuites


@export
class Testsuite(TestsuiteBase):
	_testcases:  Dict[str, Testcase]

	def __init__(self, name: str) -> None:
		super().__init__(name)

		self._testcases =  {}

	def __getitem__(self, key: str) -> Union["Testsuite", Testcase]:
		try:
			return self._testsuites[key]
		except KeyError:
			return self._testcases[key]

	def __contains__(self, key: str) -> bool:
		if key not in self._testsuites:
			return key in self._testcases

		return False

	@readonly
	def Testcases(self) -> Dict[str, Testcase]:
		return self._testcases


@export
class TestsuiteSummary(TestsuiteBase):
	pass
