.. _CODECOV:

Code Coverage
#############

:term:`Code Coverage` checks if a source code was used during execution. Usually, testcases are run by a testcase
execution framework like `pytest <https://github.com/pytest-dev/pytest>`__, which also offers to instrument the code for
code coverage collection using the ``pytest-cov`` plugin. For Python, coverage collection is usually based on
`Coverage.py <https://github.com/nedbat/coveragepy>`__, which supports statement and branch coverage collection.


.. _CODECOV/Quick:

Quick Configuration
*******************

See the :ref:`overview page <OVER>` on how to setup and enable the Sphinx extension in general.

.. note:: This is a quick and minimal configuration. See below detailed explanations.

1. Configure one or more coverage analysis reports in :file:`conf.py` by adding a new 'section' defining some
   configuration variables. Each analysis report is identified by an ID, which is later referred to by the report
   directive. Here, the ID is called ``src`` (dictionary key). Each analysis report needs 4 configuration entries:

   ``name``
     Name of the Python package [#PkgNameVsPkgDir]_.

   ``json_report``
     The code coverage report as JSON file as generated by *Coverage.py*.

   ``fail_below``
     An integer value in range 0..100, for when a code coverage is considered FAILED.

   ``levels``
     A dictionary of coverage limits, their description and CSS style classes.

   .. code-block:: Python

      # ==============================================================================
      # Sphinx-reports - CodeCov
      # ==============================================================================
      report_codecov_packages = {
         "src": {
            "name":        "myPackage",
            "json_report": "../report/coverage/coverage.json",
            "fail_below":  80,
            "levels": {
               30:      {"class": "report-cov-below30",  "desc": "almost unused"},
               50:      {"class": "report-cov-below50",  "desc": "poorly used"},
               80:      {"class": "report-cov-below80",  "desc": "medium used"},
               90:      {"class": "report-cov-below90",  "desc": "well well"},
               100:     {"class": "report-cov-below100", "desc": "excellent used"},
               "error": {"class": "report-cov-error",    "desc": "internal error"},
            },
         }
      }

2. Add the :rst:dir:`report:code-coverage` directive into your Restructured Text (ReST) document.

   .. code-block:: ReST

      .. report:code-coverage::
         :packageid: src


.. _CODECOV/Example:

Example Document
****************

The following ``coverage/index`` document is an example on how this documentation uses the :rst:dir:`report:code-coverage`
directive. The first file consists of three parts: At first, a headline; at second second a short introduction paragraph
and at third, the report generating directive. The second file shows how to integrate that document into the navigation
bar.

.. admonition:: :file:`coverage/index.rst`

   .. code-block:: ReST

      Code Coverage Report
      ####################

      Code coverage generated by `Coverage.py <https://github.com/nedbat/coveragepy>`__.

      .. report:code-coverage::
         :packageid: src

.. admonition:: :file:`index.rst`

   .. code-block:: ReST

      .. toctree::
         :caption: References and Reports
         :hidden:

         sphinx_reports/sphinx_reports
         unittests/index
         coverage/index
         Doc. Coverage Report <DocCoverage>
         Static Type Check Report ➚ <typing/index>

      .. toctree::
         :caption: Appendix
         :hidden:


.. _CODECOV/Directives:

Directives
**********

.. rst:directive:: report:code-coverage

   Add a table summarizing the code coverage per Python source code file (packages and/or modules).

   .. rst:directive:option:: packageid

      An identifier referencing a dictionary entry in the configuration variable ``report_codecov_packages`` defined in
      :file:`conf.py`.

   .. rst:directive:option:: no-branch-coverage

      If flag is present, no branch coverage columns are shown. Only statement coverage columns are present.

.. rst:directive:: report:code-coverage-legend

   .. rst:directive:option:: style

      Specifies the legend style. Default is ``horizontal-table``.

      Possible values:

      * ``default``
      * ``horizontal-table``
      * ``vertical-table``



.. _CODECOV/Roles:

Roles
*****

*There are no roles defined.*

---------------------------------

.. rubric:: Footnotes

.. [#PkgNameVsPkgDir] Toplevel Python packages can reside in a directory not matching the package name. This is possible
   because the toplevel package name is set in the package installation description. This is not good practice, but
   possible and unfortunately widely used. E.g. ``src`` as directory name. See setuptools, etc. for more details.
