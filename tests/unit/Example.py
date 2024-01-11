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
"""Unit tests for the data model."""
from pathlib  import Path
from unittest import TestCase

from sphinx_reports.Adapter.DocStrCoverage import Analyzer
from sphinx_reports.DataModel.DocumentationCoverage import ClassCoverage, ModuleCoverage, PackageCoverage

if __name__ == "__main__":
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Coverage(TestCase):
	def test_Undocumented(self) -> None:
		packageName = "undocumented"
		packageDirectory = Path(f"tests/packages/{packageName}")

		analyzer = Analyzer(packageName, packageDirectory)
		analyzer.Analyze()
		coverage = analyzer.Convert()
		coverage.Aggregate()

		self.assertEqual(0, coverage.AggregatedTotal)
		self.assertEqual(0, coverage.AggregatedExcluded)
		self.assertEqual(0, coverage.AggregatedIgnored)
		self.assertEqual(12, coverage.AggregatedExpected)
		self.assertEqual(0, coverage.AggregatedCovered)
		self.assertEqual(12, coverage.AggregatedUncovered)
		self.assertEqual(0.0, coverage.AggregatedCoverage)

		self.assertEqual(0, coverage.Total)
		self.assertEqual(0, coverage.Excluded)
		self.assertEqual(0, coverage.Ignored)
		self.assertEqual(6, coverage.Expected)
		self.assertEqual(0, coverage.Covered)
		self.assertEqual(6, coverage.Uncovered)
		self.assertEqual(0.0, coverage.Coverage)

	def test_Partial(self) -> None:
		packageName = "partially"
		packageDirectory = Path(f"tests/packages/{packageName}")

		analyzer = Analyzer(packageName, packageDirectory)
		analyzer.Analyze()
		coverage = analyzer.Convert()
		coverage.Aggregate()

		self.assertEqual(0, coverage.AggregatedTotal)
		self.assertEqual(0, coverage.AggregatedExcluded)
		self.assertEqual(0, coverage.AggregatedIgnored)
		self.assertEqual(12, coverage.AggregatedExpected)
		self.assertEqual(5, coverage.AggregatedCovered)
		self.assertEqual(7, coverage.AggregatedUncovered)
		self.assertAlmostEqual(0.417, coverage.AggregatedCoverage, 3)

		self.assertEqual(0, coverage.Total)
		self.assertEqual(0, coverage.Excluded)
		self.assertEqual(0, coverage.Ignored)
		self.assertEqual(6, coverage.Expected)
		self.assertEqual(3, coverage.Covered)
		self.assertEqual(3, coverage.Uncovered)
		self.assertEqual(0.5, coverage.Coverage)

	def test_Documented(self) -> None:
		packageName = "documented"
		packageDirectory = Path(f"tests/packages/{packageName}")

		analyzer = Analyzer(packageName, packageDirectory)
		analyzer.Analyze()
		coverage = analyzer.Convert()
		coverage.Aggregate()

		self.assertEqual(0, coverage.AggregatedTotal)
		self.assertEqual(0, coverage.AggregatedExcluded)
		self.assertEqual(0, coverage.AggregatedIgnored)
		self.assertEqual(12, coverage.AggregatedExpected)
		self.assertEqual(12, coverage.AggregatedCovered)
		self.assertEqual(0, coverage.AggregatedUncovered)
		self.assertEqual(1.0, coverage.AggregatedCoverage)

		self.assertEqual(0, coverage.Total)
		self.assertEqual(0, coverage.Excluded)
		self.assertEqual(0, coverage.Ignored)
		self.assertEqual(6, coverage.Expected)
		self.assertEqual(6, coverage.Covered)
		self.assertEqual(0, coverage.Uncovered)
		self.assertEqual(1.0, coverage.Coverage)
