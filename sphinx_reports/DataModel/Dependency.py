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
""""""
from typing import List, Iterable

from pyTooling.Decorators import export, readonly


@export
class VersionSpecifier:
	_spec: str

	def __init__(self, spec: str):
		self._spec = spec


@export
class License:
	_name: str

	def __init__(self, name: str):
		self._name = name


@export
class Distribution:
	_name:         str
	_packages:     List[str]
	_version:      VersionSpecifier
	_licenses:     List[License]
	_dependencies: List["Distribution"]

	def __init__(self, name: str):
		self._name = name

		self._packages = []
		self._version = None
		self._licenses = []
		self._dependencies = []

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Version(self) -> VersionSpecifier:
		return self._version

	@readonly
	def Licenses(self) -> Iterable[License]:
		return self._licenses
