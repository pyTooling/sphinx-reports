from importlib.metadata import metadata as importlib_metadata

from packaging import metadata
from pyTooling.Decorators import export, readonly

from sphinx_reports.DataModel.Dependency import Distribution

# Further Reading:
# * https://stackoverflow.com/questions/17194301/is-there-any-way-to-show-the-dependency-trees-for-pip-packages
# * https://www.python.org/success-stories/building-a-dependency-graph-of-our-python-codebase/
# * https://github.com/thebjorn/pydeps
# * https://docs.python.org/3/library/importlib.metadata.html


@export
class DependencyScanner:
	_distribution: Distribution

	def __init__(self, distributionName: str):
		md1 = importlib_metadata(distributionName)

		self._distribution = Distribution(distributionName)

	@readonly
	def Distribution(self) -> Distribution:
		return self._distribution
