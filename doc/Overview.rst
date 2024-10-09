.. _OVER:

Overview
########


.. _OVER/Setup:

General Extension Setup
***********************

To use the *sphinx-reports* extension in your Sphinx documentation project, the ``sphinx_reports`` package must be
downloaded and :ref:`installed from PyPI <INSTALL/pip/install>` in your environment. The installation page also shows,
how to :ref:`update <INSTALL/pip/update>` the package from PyPI using ``pip``.

At next, it's recommended to add ``sphinx_reports`` to your documentation's :file:`doc/requirements.txt`. As
modification to the package might bring braking changes, it's recommended to specify a package version (range/limit).

See the following :file:`doc/requirements.txt` file as an example with commonly used extensions:

.. code-block::

   -r ../requirements.txt

   # Enforce latest version on ReadTheDocs
   sphinx ~= 8.0
   docutils ~= 0.21

   # ReadTheDocs Theme
   sphinx_rtd_theme ~= 3.0

   # Sphinx Extenstions
   sphinxcontrib-mermaid ~= 0.9.2
   autoapi ~= 2.0.1
   sphinx_design ~= 0.6.1
   sphinx-copybutton ~= 0.5.2
   sphinx_autodoc_typehints ~= 2.5
   sphinx_reports ~= 1.0

Finally, the extension needs to be enabled in Sphinx's :file:`conf.py`, so the extension is loaded by Sphinx.

The following code snippets shows a list of commonly enabled extensions, including ``sphinx_report``:

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
        "sphinx_reports",
      # User defined extensions
        # ...
      ]
