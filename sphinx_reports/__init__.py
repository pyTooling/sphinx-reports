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
__version__ =   "0.4.0"
__keywords__ =  ["Python3", "Sphinx", "Extension", "Report", "doc-string", "interrogate"]

from hashlib              import md5
from importlib.resources  import files
from pathlib              import Path
from typing               import Any, Tuple, Dict, Optional as Nullable, TypedDict, List, Callable

from docutils             import nodes
from sphinx.addnodes      import pending_xref
from sphinx.application   import Sphinx
from sphinx.builders      import Builder
from sphinx.domains       import Domain
from sphinx.environment   import BuildEnvironment
from pyTooling.Decorators import export

from .                    import static as ResourcePackage
from .Common              import ReadResourceFile


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

	* ``report_codecov_packages``
	* ``report_doccov_packages``

	"""

	name =  "report"  #: The name of this domain
	label = "rpt"     #: The label of this domain

	dependencies: List[str] = [
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

	indices = [
		# LibraryIndex,
	]  #: A list of all indices in this domain.

	configValues: Dict[str, Tuple[Any, str, Any]] = {
		"designs":  ({}, "env", Dict),
		"defaults": ({}, "env", Dict),
		**DocStrCoverage.configValues,
		**CodeCoverage.configValues
	}  #: A dictionary of all configuration values used by this domain. (name: (default, rebuilt, type))

	initial_data = {
		"reports": {}
	}  #: A dictionary of all global data fields used by this domain.

	@property
	def Reports(self) -> Dict[str, Any]:
		return self.data["reports"]

	@staticmethod
	def AddCSSFiles(sphinxApplication: Sphinx) -> None:
		"""
		Call back for Sphinx ``builder-inited`` event.

		This callback will copy the CSS file(s) to the build directory.

		.. seealso::

		   Sphinx *builder-inited* event
		     See https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events

		:param sphinxApplication: The Sphinx application.
		"""
		# Create a new static path for this extension
		staticDirectory = (Path(sphinxApplication.outdir) / "_report_static").resolve()
		staticDirectory.mkdir(exist_ok=True)
		sphinxApplication.config.html_static_path.append(str(staticDirectory))

		# Read the CSS content from package resources and hash it
		cssFilename = "sphinx-reports.css"
		cssContent = ReadResourceFile(ResourcePackage, cssFilename)

		# Compute md5 hash of CSS file
		hash = md5(cssContent.encode("utf8")).hexdigest()

		# Write the CSS file into output directory
		cssFile = staticDirectory / f"sphinx-reports.{hash}.css"
		sphinxApplication.add_css_file(cssFile.name)

		if not cssFile.exists():
			# Purge old CSS files
			for file in staticDirectory.glob("*.css"):
				file.unlink()

			# Write CSS content
			cssFile.write_text(cssContent, encoding="utf8")

	@staticmethod
	def ReadReports(sphinxApplication: Sphinx) -> None:
		"""
		Call back for Sphinx ``builder-inited`` event.

		This callback will read the configuration variable ``vhdl_designs`` and parse the found VHDL source files.

		.. seealso::

		   Sphinx *builder-inited* event
		     See https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events

		:param sphinxApplication: The Sphinx application.
		"""
		print(f"Callback: builder-inited -> ReadReports")
		print(f"[REPORT] Reading reports ...")


	callbacks: Dict[str, List[Callable]] = {
		"builder-inited": [AddCSSFiles, ReadReports],
	}  #: A dictionary of all `events/callbacks <https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events>`__ used by this domain.

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


class setup_ReturnType(TypedDict):
	version: str
	env_version: int
	parallel_read_safe: bool
	parallel_write_safe: bool


@export
def setup(sphinxApplication: Sphinx) -> setup_ReturnType:
	"""
	Extension setup function registering the ``report`` domain in Sphinx.

	It will execute these steps:

	* register domains, directives and roles.
	* connect events (register callbacks)
	* register configuration variables for :file:`conf.py`

	:param sphinxApplication: The Sphinx application.
	:return:                  Dictionary containing the extension version and some properties.
	"""
	sphinxApplication.add_domain(ReportDomain)

	# Register callbacks
	for eventName, callbacks in ReportDomain.callbacks.items():
		for callback in callbacks:
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


