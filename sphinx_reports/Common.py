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
**Common exceptions, classes and helper functions.**
"""
from enum                        import Flag
from importlib.resources         import files
from sys                         import version_info
from types                       import ModuleType
from typing                      import List, Union

from pyTooling.Decorators        import export
from sphinx.errors               import ExtensionError


@export
class ReportExtensionError(ExtensionError):
	# WORKAROUND: for Python <3.11
	# Implementing a dummy method for Python versions before
	__notes__: List[str]
	if version_info < (3, 11):  # pragma: no cover
		def add_note(self, message: str) -> None:
			try:
				self.__notes__.append(message)
			except AttributeError:
				self.__notes__ = [message]


@export
class LegendStyle(Flag):
	Default = 0
	Table = 1

	Horizontal = 1024
	Vertical = 2048

	horizontal_table = Table | Horizontal
	vertical_table =   Table | Vertical
