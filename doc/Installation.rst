.. _INSTALL:

Installation/Updates
####################

.. _INSTALL/pip:

Using PIP to Install from PyPI
******************************

The following instruction are using PIP (Package Installer for Python) as a package manager and PyPI (Python Package
Index) as a source of Python packages.

Installing a Wheel Package from PyPI using PIP
==============================================

Users of pyTooling can select if the want to install a basic variant of pyTooling. See :ref:`DEP` for more
details.

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. code-block:: bash

         # Basic sphinx-reports package
         pip3 install sphinx_reports

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         # Basic sphinx-reports package
         pip install sphinx_reports

Developers can install further dependencies for documentation generation (``doc``) or running unit tests (``test``) or
just all (``all``) dependencies.

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. tab-set::

         .. tab-item:: With Documentation Dependencies
           :sync: Doc

            .. code-block:: bash

               # Install with dependencies to generate documentation
               pip3 install sphinx_reports[doc]

         .. tab-item:: With Unit Testing Dependencies
           :sync: Unit

            .. code-block:: bash

               # Install with dependencies to run unit tests
               pip3 install sphinx_reports[test]

         .. tab-item:: All Developer Dependencies
           :sync: All

            .. code-block:: bash

               # Install with all developer dependencies
               pip install sphinx_reports[all]

   .. tab-item:: Windows
      :sync: Windows

      .. tab-set::

         .. tab-item:: With Documentation Dependencies
           :sync: Doc

            .. code-block:: powershell

               # Install with dependencies to generate documentation
               pip install sphinx_reports[doc]

         .. tab-item:: With Unit Testing Dependencies
           :sync: Unit

            .. code-block:: powershell

               # Install with dependencies to run unit tests
               pip install sphinx_reports[test]

         .. tab-item:: All Developer Dependencies
           :sync: All

            .. code-block:: powershell

               # Install with all developer dependencies
               pip install sphinx_reports[all]


Updating from PyPI using PIP
============================

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. code-block:: bash

         pip install -U sphinx_reports

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 install -U sphinx_reports


Uninstallation using PIP
========================

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. code-block:: bash

         pip uninstall sphinx_reports

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         pip3 uninstall sphinx_reports


.. _INSTALL/setup:

Using ``setup.py`` (legacy)
***************************

See sections above on how to use PIP.

Installation using ``setup.py``
===============================

.. code-block:: bash

   setup.py install


.. _INSTALL/building:

Local Packaging and Installation via PIP
****************************************

For development and bug fixing it might be handy to create a local wheel package and also install it locally on the
development machine. The following instructions will create a local wheel package (``*.whl``) and then use PIP to
install it. As a user might have a sphinx-reports installation from PyPI, it's recommended to uninstall any previous
sphinx-reports packages. (This step is also needed if installing an updated local wheel file with same version number. PIP
will not detect a new version and thus not overwrite/reinstall the updated package contents.)

Ensure :ref:`packaging requirements <DEP/packaging>` are installed.

.. tab-set::

   .. tab-item:: Linux/MacOS
      :sync: Linux

      .. code-block:: bash

         cd <sphinx-reports>

         # Package the code in a wheel (*.whl)
         python -m build --wheel

         # Uninstall the old package
         python -m pip uninstall -y sphinx_reports

         # Install from wheel
         python -m pip install ./dist/sphinx_reports-4.1.0-py3-none-any.whl

   .. tab-item:: Windows
      :sync: Windows

      .. code-block:: powershell

         cd <sphinx-reports>

         # Package the code in a wheel (*.whl)
         py -m build --wheel

         # Uninstall the old package
         py -m pip uninstall -y sphinx_reports

         # Install from wheel
         py -m pip install .\dist\sphinx_reports-4.1.0-py3-none-any.whl
