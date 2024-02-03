from importlib.metadata import metadata as importlib_metadata

from packaging import metadata
from pyTooling.Decorators import export, readonly

from sphinx_reports.DataModel.Dependency import Distribution


@export
class DependencyScanner:
	_distribution: Distribution

	def __init__(self, distributionName: str):
		md1 = importlib_metadata(distributionName)

		self._distribution = Distribution(distributionName)

	@readonly
	def Distribution(self) -> Distribution:
		return self._distribution
