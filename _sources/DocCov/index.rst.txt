.. _DOCCOV:

Documentation Coverage
######################

.. grid:: 2

   .. grid-item::
      :columns: 6

      The :rst:dir:`report:doc-coverage` directive generates a documentation coverage report summary table. The
      documentation coverage reports need to be configured in Sphinx's ``conf.py`` for pre-analysis and data aggregation
      (:ref:`see below <DOCCOV/Config>` for details). This also allows the directive to supports multiple documentation
      coverage reports per Sphinx documentation. Each documentation coverage report is referenced by the
      :rst:dir:`reportid <report:doc-coverage:reportid>` option, which matches the dictionary key used in the
      configuration file.

      .. rubric:: Minimal Example

      .. admonition:: :file:`DocCoverage.rst`

         .. code-block:: ReST

            .. report:doc-coverage::
               :reportid: src

      .. rubric:: Options

      Additional options are offered for fine-tuning and styling of the report:

      :rst:dir:`reportid <report:doc-coverage:reportid>`
        Reference the documentation coverage report file and settings as listed in :file:`conf.py`.

      :rst:dir:`class <report:doc-coverage:class>` (optional)
        User-defined CSS class name(s), which are applied on the HTML table.

      .. rubric:: Supported Documentation Coverage Formats

      Currently, the documentation coverage is collected and measured by
      `"""docstr_coverage""" <https://github.com/HunterMcGushion/docstr_coverage>`__.

      .. rubric:: Future Ideas

      It's planned to check if `interrogate <https://github.com/econchick/interrogate>`__ could be supported too.

      It's planned to display a per package and per module documentation coverage on a separate Sphinx document (separate HTML
      page) with syntax highlighting and colored background visualizing the coverage status.


   .. grid-item::
      :columns: 6

      .. card:: Documentation Coverage

         .. image:: ../_static/DocCoverage.png


.. _DOCCOV/Config:

Configuration Entries in :file:`conf.py`
****************************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      See the :ref:`overview page <OVER>` on how to setup and enable the *sphinx-reports* extension in general.

      Configure one or more coverage analysis reports in :file:`conf.py` by adding a new *section* defining some
      configuration variables. Each analysis report is identified by an ID, which is later referred to by the report
      directive or legend directive. Here, the ID is called ``src`` (dictionary key). Each analysis report needs 4
      configuration entries:

      ``name``
        Name of the Python package [#PkgNameVsPkgDir]_.

      ``directory``
        The directory of the package to analyze.

      ``fail_below``
        An integer value in range 0..100, for when a documentation coverage is considered FAILED.

      ``levels``
        Either a predefined color palett name (like ``"default"``), or |br|
        a dictionary of coverage limits, their description and CSS style classes.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Simple Configuration

            .. code-block:: Python

               # ==============================================================================
               # Sphinx-reports - DocCov
               # ==============================================================================
               report_doccov_packages = {
                  "src": {
                     "name":       "myPackage",
                     "directory":  "../myPackage",
                     "fail_below": 80,
                     "levels":     "default"
                  }
               }

         .. tab-item:: Complex Configuration

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
                        30:      {"class": "report-cov-below30",  "desc": "almost undocumented"},
                        50:      {"class": "report-cov-below50",  "desc": "poorly documented"},
                        80:      {"class": "report-cov-below80",  "desc": "roughly documented"},
                        90:      {"class": "report-cov-below90",  "desc": "well documented"},
                        100:     {"class": "report-cov-below100", "desc": "excellent documented"},
                        "error": {"class": "report-cov-error",    "desc": "internal error"},
                     }
                  }
               }


.. _DOCCOV/Example:

Example Document
****************

The following :file:`DocCoverage.rst` document is an example on how to use the :rst:dir:`report:doc-coverage`
directive. The first file consists of three parts:

1. A page title (headline)
2. A grid from `sphinx{design} <https://sphinx-design.readthedocs.io/>`__ so :rst:dir:`report:doc-coverage` and
   :rst:dir:`report:doc-coverage-legend` can be displayed side-by-side
3. A footer

The second file shows how to integrate that document into the navigation bar / *toc-tree*.


.. admonition:: :file:`DocCoverage.rst`

   .. code-block:: ReST

      .. _DOCCOV:

      Documentation Coverage Report
      #############################

      .. grid:: 2

         .. grid-item::
            :columns: 5

            .. report:doc-coverage::
               :reportid: src

         .. grid-item::
            :columns: 7

            .. report:doc-coverage-legend::
               :reportid: src
               :style: vertical-table

      ----------

      Documentation coverage generated with `"""docstr-coverage""" <https://github.com/HunterMcGushion/docstr_coverage>`__
      and visualized by `sphinx-reports <https://github.com/pyTooling/sphinx-reports>`__.

.. admonition:: :file:`index.rst`

   .. code-block:: ReST

      .. toctree::
         :caption: References and Reports
         :hidden:

         Python Class Reference <sphinx_reports/sphinx_reports>
         Unittest
         CodeCoverage
         Doc. Coverage Report <DocCoverage>
         Static Type Check Report ➚ <typing/index>

      .. toctree::
         :caption: Appendix
         :hidden:


.. _DOCCOV/Directives:

Sphinx Directives
*****************

The following directives are provided for visualizing documentation coverage reports.

.. rst:directive:: report:doc-coverage

   Generate a table summarizing the documentation coverage per Python source code file (packages and/or modules). The
   package hierarchy is visualized by indentation and a 📦 symbol.

   .. rst:directive:option:: class

      Optional: A list of space separated user-defined CSS class names.

      The CSS classes are applied on the HTML ``<table>`` tag.

   .. rst:directive:option:: reportid

      An identifier referencing a dictionary entry (key) in the configuration variable ``report_doccov_packages``
      defined in :file:`conf.py`.

.. rst:directive:: report:doc-coverage-legend

   Generate a table showing the color palett applied to a documentation coverage summary table.

   Each documentation coverage report could potentially use its own color palett. Therefore, the ``reportid`` options
   should use the same values.

   .. rst:directive:option:: class

      Optional: A list of space separated user-defined CSS class names.

      The CSS classes are applied on the HTML ``<table>`` tag.

   .. rst:directive:option:: style

      Specifies the legend style. Default is ``horizontal-table``.

      Possible values:

      * ``default``
      * ``horizontal-table``
      * ``vertical-table``


.. _DOCCOV/Roles:

Sphinx Roles
************

*There are no roles defined.*


.. _DOCCOV/ColorPalett:

Color Paletts
*************

.. grid:: 2

   .. grid-item::
      :columns: 6

      The default color palett can be changed by:

      * setting a different predefined color palett name.
      * specifying a new list of coverage level which also define a corresponding CSS class name.
      * overriding the existing CSS rules with different colors and styles.

      .. rubric:: ``default`` palett

      The ``default`` palett defines 12 levels: ≤10%, ≤20%, ≤30%, ≤40%, ≤50%, ≤60%, ≤70%, ≤80%, ≤85%, ≤90%, ≤95%, ≤100%
      from blue via red, orange, yellow to green.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: default

            .. image:: ../_static/DocCoverage-Legend.png
               :width: 350 px


.. _DOCCOV/Styling:

Custom CSS Styling
******************

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. rubric:: Table Styling

      The ``table``-tag has 2 additional CSS classes:

      ``report-doccov-table``
        Allows selecting the ``table`` tag, but only for documentation coverage reports.
      ``report-doccov-%reportid%``
        Allows selecting one specific documentation coverage report. ``%reportid%`` gets replaced by the reportid used in the
        option field of the directive. Here it got replaced by ``src``.

      .. rubric:: Row Styling

      The ``tr``-tag (table row) has 2 additional CSS classes:

      ``report-package``/``report-module``/``report-summary``
        This class indicated if the row refers to a Python package, Python module or the overall coverage summary (last
        row).
      ``report-below-%percentage%``
        Depending on the coverage in percent, a CSS class is added according to the color palett configuration.

   .. grid-item::
      :columns: 6

      .. card:: Generated HTML Code (condensed)

         .. code-block:: html

            <table class="report-doccov-table report-doccov-src">
              <thead>
                <tr>
                  <th> ..... </th>
                  .....
                  <th> ..... </th>
                </tr>
              </thead>
              <tbody>
                <tr class="report-package report-below-30"> ..... </tr>
                <tr class="report-module report-below-70"> ..... </tr>
                .....
                <tr class="report-summary report-below-50"> ..... </tr>
              </tbody>
            </table>

      .. card:: Example CSS Rules

         .. code-block:: css

            table.report-doccov-table > thead > tr,
            table.report-doccov-legend > thead > tr {
               background: #ebebeb;
            }

            table.report-doccov-table > tbody > tr.report-cov-below95,
            table.report-doccov-legend > tbody > tr.report-cov-below95 {
               background: hsl(90 75% 75%);
            }

            table.report-doccov-table > tbody > tr.report-summary {
               font-weight: bold;
            }

---------------------------------

.. rubric:: Footnotes

.. [#PkgNameVsPkgDir] Toplevel Python packages can reside in a directory not matching the package name. This is possible
   because the toplevel package name is set in the package installation description. This is not good practice, but
   possible and unfortunately widely used. E.g. ``src`` as directory name. See setuptools, etc. for more details.
