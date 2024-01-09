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
**A Sphinx domain providing directives to add reports to the Sphinx-based documentation.**

Supported reports:

* :ref:`DOCCOV`
* :ref:`CODECOV`
* :ref:`UNITTEST`
* :ref:`DEP`

"""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2023-2024, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "0.3.0"
__keywords__ =  ["Python3", "Sphinx", "Extension", "Report", "doc-string", "interrogate"]

from typing import Any, Tuple, Dict, Optional as Nullable

from docutils import nodes
from pyTooling.Decorators import export
from sphinx.addnodes import pending_xref
from sphinx.application   import Sphinx
from sphinx.builders import Builder
from sphinx.domains       import Domain
from sphinx.environment import BuildEnvironment


@export
class ReportDomain(Domain):
	"""
	A Sphinx extension providing a ``report`` domain to integrate reports and summaries into a Sphinx-based documentation.

	.. rubric:: New directives:

	* :rst:dir:`doc-coverage`

	.. rubric:: New roles:

	* *None*

	.. rubric:: New indices:

	* *None*

  .. rubric:: Configuration variables

	All configuration variables in :file:`conf.py` are prefixed with ``report_*``:

	* ``report_doccov_packages``

	"""

	name =  "report"  #: The name of this domain
	label = "rpt"     #: The label of this domain

	dependencies = [
	]  #: A list of other extensions this domain depends on.

	from sphinx_reports.CodeCoverage import CodeCoverage
	from sphinx_reports.DocCoverage  import DocStrCoverage
	from sphinx_reports.Unittest     import UnittestSummary

	directives = {
		"code-coverage": CodeCoverage,
		"dependecy":     DocStrCoverage,
		"doc-coverage":  DocStrCoverage,
		"unittest":      UnittestSummary,
	}  #: A dictionary of all directives in this domain.

	roles = {
		# "design":   DesignRole,
	}  #: A dictionary of all roles in this domain.

	indices = {
		# LibraryIndex,
	}  #: A dictionary of all indices in this domain.

	configValues: Dict[str, Tuple[Any, str, Any]] = {
		"designs":  ({}, "env", Dict),
		"defaults": ({}, "env", Dict),
		**DocStrCoverage.configValues
	}  #: A dictionary of all configuration values used by this domain. (name: (default, rebuilt, type))

	initial_data = {
		"reports": {}
	}  #: A dictionary of all global data fields used by this domain.

	@property
	def Reports(self) -> Dict[str, Any]:
		return self.data["reports"]

	@staticmethod
	def ReadReports(sphinxApplication: Sphinx) -> None:
		"""
		Call back for Sphinx ``builder-inited`` event.

		This callback will read the configuration variable ``vhdl_designs`` and parse the found VHDL source files.

		.. seealso::

		   Sphinx *builder-inited* event
		     See http://sphinx-doc.org/extdev/appapi.html#event-builder-inited

		:param sphinxApplication: The Sphinx application.
		"""
		print(f"Callback: builder-inited -> ReadReports")
		print(f"[REPORT] Reading reports ...")


	callbacks = {
		"builder-inited": ReadReports,
		# "source-read": ReadDesigns
	}  #: A dictionary of all callbacks used by this domain.

	def resolve_xref(
		self,
		env: BuildEnvironment,
		fromdocname: str,
		builder: Builder,
		typ: str,
		target: str,
		node: pending_xref,
		contnode: nodes.Element
	) -> Nullable[nodes.Element]:
		raise NotImplementedError()


@export
def setup(sphinxApplication: Sphinx):
	"""
	Extension setup function registering the ``report`` domain in Sphinx.

	:param sphinxApplication: The Sphinx application.
	:return:                  Dictionary containing the extension version and some properties.
	"""
	sphinxApplication.add_domain(ReportDomain)

	# Register callbacks
	for eventName, callback in ReportDomain.callbacks.items():
		sphinxApplication.connect(eventName, callback)

	# Register configuration options supported/needed in Sphinx's 'conf.py'
	for configName, (configDefault, configRebuilt, configTypes) in ReportDomain.configValues.items():
		sphinxApplication.add_config_value(f"{ReportDomain.name}_{configName}", configDefault, configRebuilt, configTypes)

	return {
		"version": __version__,                          # version of the extension
		"env_version": int(__version__.split(".")[0]),   # version of the data structure stored in the environment
		'parallel_read_safe': False,                     # Not yet evaluated, thus false
		'parallel_write_safe': True,                     # Internal data structure is used read-only, thus no problems will occur by parallel writing.
	}


