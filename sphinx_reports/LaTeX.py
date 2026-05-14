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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from textwrap import dedent
from typing import Tuple

from sphinx.writers.latex  import LaTeXTranslator

from pyTooling.Decorators import export
from sphinx_reports.Common import visitFunc, departFunc
from sphinx_reports.Node   import Landscape


__all__ = ["translateLandscape"]


@export
def visit_Landscape(translator: LaTeXTranslator, node: Landscape) -> None:
	"""
	Call back function for visiting a :class:`Landscape`.

	This function begins a ``landscape`` environment in LaTeX.

	:param translator: The LaTeX translator instance.
	:param node:       The current node being visited.
	"""
	translator.body.append(dedent("""\
		\\begin{landscape}
		  \\begingroup
		    \\setlength{\\textwidth}{\\textheight}
		    \\setlength{\\linewidth}{\\textwidth}
		    \\setlength{\\hsize}{\\textwidth}
		""")
	)

@export
def depart_Landscape(translator: LaTeXTranslator, node: Landscape) -> None:
	"""
	Call back function for departing a :class:`Landscape`.

	This function ends a ``landscape`` environment in LaTeX.

	:param translator: The LaTeX translator instance.
	:param node:       The current node being departed.
	"""
	translator.body.append(dedent("""\
		  \\endgroup
		\\end{landscape}
		""")
	)


translateLandscape: Tuple[visitFunc, departFunc] = (visit_Landscape, depart_Landscape)
"""A tuple combining both ``visit_*`` and ``depart_*`` call back functions for a :class:`Landscape` node."""
