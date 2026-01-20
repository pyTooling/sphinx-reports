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
# Copyright 2023-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
**Helper functions and derived classes from Sphinx.**
"""
from re     import match as re_match
from typing import Optional as Nullable, Tuple, List

from docutils              import nodes
from sphinx.directives     import ObjectDescription
from pyTooling.Decorators  import export
from sphinx.util.logging   import getLogger

from sphinx_reports.Common import ReportExtensionError, LegendStyle


@export
def strip(option: str) -> str:
	return option.strip()


@export
def stripAndNormalize(option: str) -> str:
	return option.strip().lower()


@export
class BaseDirective(ObjectDescription):
	has_content: bool = False
	"""
	A boolean; ``True`` if content is allowed.

	Client code must handle the case where content is required but not supplied (an empty content list will be supplied).
	"""

	required_arguments = 0
	"""Number of required directive arguments."""

	optional_arguments = 0
	"""Number of optional arguments after the required arguments."""

	final_argument_whitespace = False
	"""A boolean, indicating if the final argument may contain whitespace."""

	option_spec = {}
	"""
	Mapping of option names to validator functions.

	A dictionary, mapping known option names to conversion functions such as :class:`int` or :class:`float`
	(default: {}, no options). Several conversion functions are defined in the ``directives/__init__.py`` module.

	Option conversion functions take a single parameter, the option argument (a string or :class:`None`), validate it
	and/or convert it to the appropriate form. Conversion functions may raise :exc:`ValueError` and
	:exc:`TypeError` exceptions.
	"""

	directiveName: str

	def _ParseBooleanOption(self, optionName: str, default: Nullable[bool] = None) -> bool:
		try:
			option = self.options[optionName]
		except KeyError as ex:
			if default is not None:
				return default
			else:
				raise ReportExtensionError(f"{self.directiveName}: Required option '{optionName}' not found for directive.") from ex

		if option in ("yes", "true"):
			return True
		elif option in ("no", "false"):
			return False
		else:
			raise ReportExtensionError(f"{self.directiveName}::{optionName}: '{option}' not supported for a boolean value (yes/true, no/false).")

	def _ParseStringOption(self, optionName: str, default: Nullable[str] = None, regexp: str = "\\w+") -> str:
		try:
			option: str = self.options[optionName]
		except KeyError as ex:
			if default is not None:
				return default
			else:
				raise ReportExtensionError(f"{self.directiveName}: Required option '{optionName}' not found for directive.") from ex

		if re_match(regexp, option):
			return option
		else:
			raise ReportExtensionError(f"{self.directiveName}::{optionName}: '{option}' not an accepted value for regexp '{regexp}'.")

	def _ParseLegendStyle(self, optionName: str, default: Nullable[LegendStyle] = None) -> LegendStyle:
		try:
			option: str = self.options[optionName]
		except KeyError as ex:
			if default is not None:
				return default
			else:
				raise ReportExtensionError(f"{self.directiveName}: Required option '{optionName}' not found for directive.") from ex

		identifier = option.lower().replace("-", "_")

		try:
			return LegendStyle[identifier]
		except KeyError as ex:
			raise ReportExtensionError(f"{self.directiveName}::{optionName}: Value '{option}' (transformed: '{identifier}') is not a valid member of 'LegendStyle'.") from ex

	def _CreateSingleTableHeader(self, columns: List[Tuple[str, Nullable[int]]], identifier: str, classes: List[str]) -> nodes.tgroup:
		table = nodes.table("", identifier=identifier, classes=classes)
		table += (tableGroup := nodes.tgroup(cols=(len(columns))))

		# Setup column specifications
		for _, width in columns:
			tableGroup += nodes.colspec(colwidth=width)

		tableGroup += (tableHeader := nodes.thead())
		tableHeader += (headerRow := nodes.row())

		# Setup header row
		for columnTitle, _ in columns:
			headerRow += nodes.entry("", nodes.Text(columnTitle))

		return tableGroup

	def _CreateDoubleRowTableHeader(self, columns: List[Tuple[str, Nullable[List[Tuple[str, int]]], Nullable[int]]], identifier: str, classes: List[str]) -> Tuple[nodes.table, nodes.tgroup]:
		columnCount = sum(len(groupColumn[1]) if groupColumn[1] is not None else 1 for groupColumn in columns)

		# Create table with N columns
		table = nodes.table("", identifier=identifier, classes=classes)
		table += (tableGroup := nodes.tgroup(cols=columnCount))

		# Setup column specifications
		for _, more, width in columns:
			if more is None:
				tableGroup += nodes.colspec(colwidth=width)
			else:
				for _, width in more:
					tableGroup += nodes.colspec(colwidth=width)
		tableGroup += (tableHeader := nodes.thead())
		tableHeader += (headerRow1 := nodes.row())

		# Setup primary header row
		for columnTitle, more, _ in columns:
			if more is None:
				headerRow1 += nodes.entry("", nodes.Text(columnTitle), morerows=1)
			else:
				headerRow1 += nodes.entry("", nodes.Text(columnTitle), morecols=(morecols := len(more) - 1))
				for i in range(morecols):
					headerRow1 += None

		# Setup secondary header row
		tableHeader += (headerRow2 := nodes.row())
		for columnTitle, more, _ in columns:
			if more is None:
				headerRow2 += None
			else:
				for columnTitle, _ in more:
					headerRow2 += nodes.entry("", nodes.Text(columnTitle))

		return tableGroup

	def _CreateRotatedTableHeader(self, columns: List[Tuple[str, Nullable[List[str]]]], identifier: str, classes: List[str]) -> nodes.tgroup:
		table = nodes.table("", identifier=identifier, classes=classes)
		table += (tableGroup := nodes.tgroup(cols=len(columns)))

		# Setup column specifications
		for i, (_, width) in enumerate(columns):
			tableGroup += nodes.colspec(classes=[f"col-{i}"])

		tableGroup += (tableHeader := nodes.thead())
		tableHeader += (headerRow := nodes.row())

		# Setup header row
		for columnTitle, classes in columns:
			span = nodes.inline("", text=columnTitle)
			div = nodes.container("", span)
			headerRow += nodes.entry("", div, classes=[] if classes is None else classes)

		return tableGroup

	def _internalError(self, container: nodes.container, location: str, message: str, exception: Exception) -> List[nodes.Node]:
		logger = getLogger(location)
		logger.error(f"{message}")
		logger.error(f"  {exception.__class__.__name__}: {exception}")
		if exception.__cause__ is not None:
			logger.error(f"    {exception.__cause__.__class__.__name__}: {exception.__cause__}")
		logger.exception(exception)

		container += nodes.paragraph(text=message)

		return [container]
