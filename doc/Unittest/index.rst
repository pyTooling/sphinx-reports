.. _UNITTEST:

Unit Test Summary
#################

.. grid:: 2

   .. grid-item::
      :columns: 6

      The :rst:dir:`report:unittest-summary` directive generates a unittest report summary table. The unittest report
      file(s) need to be configured in Sphinx's ``conf.py`` for pre-analysis and data aggregation
      (:ref:`see below <UNITTEST/Config>` for details). This also allows the directive to supports multiple unittest
      reports per Sphinx documentation. Each unittest report is referenced by the
      :rst:dir:`report <report:unittest-summary:reportid>` option, which matches the dictionary key used in the
      configuration file.

      .. rubric:: Minimal Example

      .. admonition:: :file:`Unittest.rst`

         .. code-block:: ReST

            .. report:unittest-summary::
               :reportid: src

      .. rubric:: Options

      Additional options are offered for fine-tuning and styling of the report:

      :rst:dir:`reportid <report:unittest-summary:reportid>`
        Reference the unittest report file and settings as listed in :file:`conf.py`.

      :rst:dir:`testsuite-summary-name <report:unittest-summary:testsuite-summary-name>` (optional)
        Override the TestsuiteSummary's name.

      :rst:dir:`show-testcases <report:unittest-summary:show-testcases>` (optional)
        Select if all testcases or only flawed testcases should be listed per testsuite.

      :rst:dir:`no-assertions <report:unittest-summary:no-assertions>` (optional)
        If flag is present, no assertion column will be shown.

      :rst:dir:`hide-testsuite-summary <report:unittest-summary:hide-testsuite-summary>` (optional)
        If this flag is present, hide the summary row.

      :rst:dir:`class <report:unittest-summary:class>` (optional)
        User-defined CSS class name(s), which are applied on the HTML table.

      .. rubric:: Supported Unittest Formats

      Reading unittest summary reports in XML format is based on `pyEDAA.Reports <https://edaa-org.github.io/pyEDAA.Reports>`__.
      It supports Any JUnit XML files and derived dialects. So any XML file format can be used to visualize the results
      in a Sphinx documentation.

      Explicitly, the following report sources have been tested:

      * `pytest <https://github.com/pytest-dev/pytest>`__
      * `OSVVM-Scripts <https://github.com/OSVVM/OSVVM-Scripts>`__

      .. rubric:: Future Ideas

      It's planned to display a per testsuite and maybe per testcase report on a separate Sphinx document (separate HTML
      page).

      .. #:term:`Unittests` checks if a source code was used during execution. Usually, testcases are run by a testcase
         execution framework like `pytest <https://github.com/pytest-dev/pytest>`__.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Only Testsuites

            .. image:: ../_static/Unittest_OnlyTestsuites.png

         .. tab-item:: Testsuites and Testcases
            :selected:

            .. image:: ../_static/Unittest.png


.. _UNITTEST/Config:

Configuration Entries in :file:`conf.py`
****************************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      See the :ref:`overview page <OVER>` on how to setup and enable the *sphinx-reports* extension in general.

      Configure one or more unittest reports in :file:`conf.py` by adding a new *section* defining some
      configuration variables. Each unittest report is identified by an ID, which is later referred to by the report
      directive or legend directive. Here, the ID is called ``src`` (dictionary key). Each analysis report needs 4
      configuration entries:

      ``name``
        Name of the Python package.
      ``xml_report``
        The unittest report as XML file.

   .. grid-item::
      :columns: 6

      .. card:: Configuration

         .. code-block:: Python

            # ==============================================================================
            # Sphinx-reports - Unittest
            # ==============================================================================
            report_codecov_packages = {
               "src": {
                  "name":       "myPackage",
                  "xml_report": "../report/unit/unittest.xml",
               }
            }


.. _UNITTEST/Example:

Example Document
****************

he following :file:`Unittest.rst` document is an example on how to use the :rst:dir:`report:unittest-summary`
directive. The first file consists of three parts:

1. A page title (headline)
2. The :rst:dir:`report:code-coverage` directive to generate the report table.
3. A footer

The second file shows how to integrate that document into the navigation bar / *toc-tree*.

.. admonition:: :file:`Unittest.rst`

   .. code-block:: ReST

      Unittest Summary Report
      #######################

      .. report:unittest-summary::
         :reportid: src
         :show-testcases: not-passed
         :no-assertions:

      ----------

      Unittest report generated with `pytest <https://github.com/pytest-dev/pytest>`__ and visualized by
      `sphinx-reports <https://github.com/pyTooling/sphinx-reports>`__.


.. admonition:: :file:`index.rst`

   .. code-block:: ReST

      .. toctree::
         :caption: References and Reports
         :hidden:

         Python Class Reference <sphinx_reports/sphinx_reports>
         Unittest
         CodeCoverage
         DocCoverage
         Static Type Check Report ➚ <typing/index>

      .. toctree::
         :caption: Appendix
         :hidden:


.. _UNITTEST/Directives:

Sphinx Directives
*****************

The following directives are provided for visualizing unittest reports.

.. rst:directive:: report:unittest-summary

   Generate a table summarizing the unittest results per testsuite and testcase. The testsuite hierarchy is visualized
   by indentation.

   .. rst:directive:option:: class

      Optional: A list of space separated user-defined CSS class names.

      The CSS classes are applied on the HTML ``<table>`` tag.

   .. rst:directive:option:: reportid

      An identifier referencing a dictionary entry (key) in the configuration variable ``report_unittest_testsuites``
      defined in :file:`conf.py`.

   .. rst:directive:option:: testsuite-summary-name

      Optional: Override the TestsuiteSummary's name.

   .. rst:directive:option:: show-testcases

      Optional: Select if all testcases (``all``) or only flawed testcases (``not-passed``) should be listed per
      testsuite.

   .. rst:directive:option:: no-assertions

      Optional: If flag is present, no assertion column will be shown.

   .. rst:directive:option:: hide-testsuite-summary

      Optional: if this flag is present, hide the summary row.



.. _UNITTEST/Roles:

Sphinx Roles
************

*There are no roles defined.*



.. _UNITTEST/Styling:

Custom CSS Styling
******************

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. rubric:: Table Styling

      The ``table``-tag has 2 additional CSS classes:

      ``report-unittest-table``
        Allows selecting the ``table`` tag, but only for unittest reports.
      ``report-unittest-%reportid%``
        Allows selecting one specific unittest report. ``%reportid%`` gets replaced by the reportid used in the
        option field of the directive. Here it got replaced by ``src``.

      .. rubric:: Row Styling

      The ``tr``-tag (table row) has 2 additional CSS classes:

      ``report-testsuite``/``report-testcase``/``report-summary``
        This class indicated if the row refers to a testsuite, testcase or the overall coverage summary (last row).
      ``report-%status%``
        Depending on the testsuite or testcase status, a representing CSS class is added.

   .. grid-item::
      :columns: 6

      .. card:: Generated HTML Code (condensed)

         .. code-block:: html

            <table class="report-unittest-table report-unittest-src">
              <thead>
                <tr>
                  <th> ..... </th>
                  .....
                  <th> ..... </th>
                </tr>
              </thead>
              <tbody>
                <tr class="report-testsuite report-passed"> ..... </tr>
                <tr class="report-testcase report-skipped"> ..... </tr>
                .....
                <tr class="report-summary report-passed"> ..... </tr>
              </tbody>
            </table>

      .. card:: Example CSS Rules

         .. code-block:: css

            table.report-unittest-table > thead > tr {
               background: #ebebeb;
            }

            table.report-unittest-table > tbody > tr.report-summary.report-passed {
               font-weight: bold;
            }
