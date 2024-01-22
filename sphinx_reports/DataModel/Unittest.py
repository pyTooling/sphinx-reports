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
from datetime import timedelta
from enum     import Flag
from typing   import Optional as Nullable, Dict, Union, Tuple

from pyTooling.Decorators import export, readonly

from sphinx_reports.Common import ReportExtensionError


@export
class UnittestError(ReportExtensionError):
	pass


@export
class TestcaseState(Flag):
	Unknown = 0
	Failed = 1
	Error = 2
	Skipped = 3
	Passed = 4


@export
class Base:
	_name:  str
	_state: TestcaseState
	_time:  timedelta

	def __init__(self, name: str, time: timedelta) -> None:
		self._name = name
		self._state = TestcaseState.Unknown
		self._time = time

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def State(self) -> TestcaseState:
		return self._state

	@readonly
	def Time(self) -> timedelta:
		return self._time


@export
class Test(Base):
	def __init__(self, name: str) -> None:
		super().__init__(name)


@export
class Testcase(Base):
	_tests: Dict[str, Test]

	_assertions: int

	def __init__(self, name: str, time: timedelta) -> None:
		super().__init__(name, time)

		self._tests = {}
		self._assertions = 0

	@readonly
	def Assertions(self) -> int:
		return self._assertions


@export
class TestsuiteBase(Base):
	_testsuites: Dict[str, "Testsuite"]

	_tests:   int
	_skipped: int
	_errored: int
	_failed:  int
	_passed:  int

	def __init__(self, name: str, time: timedelta) -> None:
		super().__init__(name, time)

		self._testsuites = {}

		self._tests =   0
		self._skipped = 0
		self._errored = 0
		self._failed =  0
		self._passed =  0

	def __getitem__(self, key: str) -> "Testsuite":
		return self._testsuites[key]

	def __contains__(self, key: str) -> bool:
		return key in self._testsuites

	@readonly
	def Testsuites(self) -> Dict[str, "Testsuite"]:
		return self._testsuites

	@readonly
	def Tests(self) -> int:
		return self._tests

	@readonly
	def Skipped(self) -> int:
		return self._skipped

	@readonly
	def Errored(self) -> int:
		return self._errored

	@readonly
	def Failed(self) -> int:
		return self._failed

	@readonly
	def Passed(self) -> int:
		return self._passed

	def Aggregate(self) -> Tuple[int, int, int, int, int]:
		tests = 0
		skipped = 0
		errored = 0
		failed = 0
		passed = 0

		for testsuite in self._testsuites.values():
			t, s, e, f, p = testsuite.Aggregate()
			tests += t
			skipped += s
			errored += e
			failed += f
			passed += p

		return tests, skipped, errored, failed, passed


@export
class Testsuite(TestsuiteBase):
	_testcases:  Dict[str, Testcase]

	def __init__(self, name: str, time: timedelta) -> None:
		super().__init__(name, time)

		self._testcases = {}

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

	def Aggregate(self) -> Tuple[int, int, int, int, int]:
		tests, skipped, errored, failed, passed = super().Aggregate()

		for testcase in self._testcases.values():
			if testcase._state is TestcaseState.Passed:
				tests += 1
				passed += 1
			elif testcase._state is TestcaseState.Failed:
				tests += 1
				failed += 1
			elif testcase._state is TestcaseState.Skipped:
				tests += 1
				skipped += 1
			elif testcase._state is TestcaseState.Error:
				tests += 1
				errored += 1
			elif testcase._state is TestcaseState.Unknown:
				raise UnittestError(f"Found testcase '{testcase._name}' with unknown state.")

		self._tests = tests
		self._skipped = skipped
		self._errored = errored
		self._failed = failed
		self._passed = passed

		if errored > 0:
			self._state = TestcaseState.Error
		elif failed > 0:
			self._state = TestcaseState.Failed
		elif tests - skipped == passed:
			self._state = TestcaseState.Passed
		elif tests == skipped:
			self._state = TestcaseState.Skipped
		else:
			self._state = TestcaseState.Unknown

		return tests, skipped, errored, failed, passed


@export
class TestsuiteSummary(TestsuiteBase):
	_time: float

	def __init__(self, name: str, time: timedelta):
		super().__init__(name, time)

	def Aggregate(self) -> Tuple[int, int, int, int, int]:
		tests, skipped, errored, failed, passed = super().Aggregate()

		self._tests = tests
		self._skipped = skipped
		self._errored = errored
		self._failed = failed
		self._passed = passed

		if errored > 0:
			self._state = TestcaseState.Error
		elif failed > 0:
			self._state = TestcaseState.Failed
		elif tests - skipped == passed:
			self._state = TestcaseState.Passed
		elif tests == skipped:
			self._state = TestcaseState.Skipped
		else:
			self._state = TestcaseState.Unknown

		return tests, skipped, errored, failed, passed
