.. _OVER:

Overview
########

The *sphinx-reports* extension provides a new domain called ``report``, which adds new RestructuredText directives and
roles.

These are described in the following categories:

* ✅ :ref:`UNITTEST`
* ✅ :ref:`CODECOV`
* ✅ :ref:`DOCCOV`
* 🚧 :ref:`DEP`

.. _OVER/Setup:

General Extension Setup
***********************

To use the *sphinx-reports* extension in your Sphinx documentation project, the ``sphinx_reports`` package needs be
downloaded and :ref:`installed from PyPI <INSTALL/pip/install>` in your environment. *Sphinx-reports*'s
:ref:`installation <INSTALL>` page also shows how to :ref:`update <INSTALL/pip/update>` the package from PyPI using
``pip``.

At next, it's recommended to add ``sphinx_reports`` to your documentation's :file:`doc/requirements.txt`. As updates and
modifications to the ``sphinx_reports`` package might introduce braking changes, it's recommended to specify a package
version (range/limit). Usually, the major version number is fixed, because according to `SemVer.org <https://semver.org/>`__
a breaking change needs to increment the major version number.

See the following :file:`doc/requirements.txt` file as an example with commonly used extensions:

.. admonition:: :file:`doc/requirements.txt`

   .. code-block::

      -r ../requirements.txt

      # Enforce latest version on ReadTheDocs
      sphinx ~= 9.1
      docutils ~= 0.22

      # ReadTheDocs Theme
      sphinx_rtd_theme ~= 3.1

      # Sphinx Extenstions
      sphinxcontrib-mermaid ~= 2.0
      autoapi ~= 2.0.1
      sphinx_design ~= 0.7.0
      sphinx-copybutton ~= 0.5.0
      sphinx_autodoc_typehints ~= 3.6
      sphinx_reports ~= 1.0             # <= new entry

Finally, the extension needs to be enabled in Sphinx's :file:`conf.py`, so the extension is loaded by Sphinx.

The following code snippets shows a list of commonly enabled extensions, including ``sphinx_report``:

.. admonition:: :file:`conf.py`

   .. code-block:: Python

      # ==============================================================================
      # Extensions
      # ==============================================================================
      extensions = [
      # Standard Sphinx extensions
        "sphinx.ext.autodoc",
        "sphinx.ext.extlinks",
        "sphinx.ext.intersphinx",
        "sphinx.ext.inheritance_diagram",
        "sphinx.ext.todo",
        "sphinx.ext.graphviz",
        "sphinx.ext.mathjax",
        "sphinx.ext.ifconfig",
        "sphinx.ext.viewcode",
      # SphinxContrib extensions
        "sphinxcontrib.mermaid",
      # Other extensions
        "autoapi.sphinx",
        "sphinx_design",
        "sphinx_copybutton",
        "sphinx_autodoc_typehints",
        "sphinx_reports",             # <= new entry
      # User defined extensions
        # ...
      ]
