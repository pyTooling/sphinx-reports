.. _DOCCOV:

Documentation Coverage
######################

.. todo:: DocCov: write introduction


Quick Configuration
*******************

This is a quick and minimal configuration. See below detailed explanations.

1. Add ``sphinx-report`` extension to list of extensions in :file:`conf.py`:

   .. code-block:: Python

      # ...
      extensions = [
      # Standard Sphinx extensions
        # ...
      # SphinxContrib extensions
        # ...
      # Other extensions
        # ...
        "sphinx_reports",
      # User defined extensions from _extensions
        # ...
      ]
      # ...

2. Configure one or more Python packages for documentation coverage analysis in :file:`conf.py` by adding a new
   'section' defining some configuration variables. Each package is identified by an ID, which is later referred to by
   the report directive. Here, the ID is called ``src`` (dictionary key). Each package needs 4 configuration entries:

   ``name``
     Name of the Python package[#PkgNameVsPkgDir]_.

   ``directory``
     The directory of the package to analyze.

   ``fail_below``
     An integer value in range 0..100, for when a documentation coverage is considered FAILED.

   ``levels``
     A dictionary of coverage limits, their description and CSS style classes.

   .. code-block:: Python

      # ==============================================================================
      # Sphinx-reports - DocCov
      # ==============================================================================
      report_doccov_packages = {
         "src": {
            "name":       "myPackage",
            "directory":  "../myPackage",
            "fail_below": 80,
            "levels": {
               30:  {"class": "doccov-below30",  "desc": "almost undocumented"},
               50:  {"class": "doccov-below50",  "desc": "poorly documented"},
               80:  {"class": "doccov-below80",  "desc": "roughly documented"},
               90:  {"class": "doccov-below90",  "desc": "well documented"},
               100: {"class": "doccov-below100", "desc": "excellent documented"},
            },
         }
      }


.. rubric:: Footnotes

.. [#PkgNameVsPkgDir] Toplevel Python packages can reside in a directory not matching the package name. This is possible
   because the toplevel package name is set in the package installation description. This is not good practice, but
   possible and unfortunately widely used. E.g. ``src`` as directory name. See setuptools, etc. for more details.
