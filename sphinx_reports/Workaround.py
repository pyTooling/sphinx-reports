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
Workarounds for Sphinx and Docutils problems.
"""
from docutils.nodes      import table
from docutils.transforms import Transform
from sphinx.util.logging import getLogger

logger = getLogger(__name__)

class FixLatexTableWidths(Transform):
	default_priority = 500

	def apply(self):
		sphinxEnvironment = self.document.settings.env

		if sphinxEnvironment.app.builder.format != "latex":
			return

		# search for all table nodes
		for tableNode in self.document.findall(table):
			if (cssClasses := tableNode.get("classes", None)) is None:
				continue

			if "report-unittest-table" in cssClasses:
				if 'colwidths-given' not in cssClasses:
					cssClasses.append('colwidths-given')
					
					logger.info("Applied 'colwidths-given' to a table via FixLatexTableWidths transform.", location=tableNode)
