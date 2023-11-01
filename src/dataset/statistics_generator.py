import numpy as np
import tensorflow as tf
from typing import Union


class RunningStats:
    """
    Maintains running statistics including mean, variance, min, max,
    shape, data type, and an example of the data points.
    """

    def __init__(self):
        self.clear()

    def clear(self):
        """
        Reset all statistical data.
        """
        self.n = 0
        self.mean = None
        self.M2 = None
        self.min = None
        self.max = None
        self.shape = None
        self.dtype = None
        self.example = None

    def push(self, x: np.ndarray):
        """
        Update the statistics with a new data point.

        Args:
        - x (np.ndarray): A new data point.
        """
        # Store the shape, data type, and example of the first data point
        if self.n == 0:
            self.shape = x.shape
            self.dtype = str(x.dtype)
            self.example = x

            self.mean = np.zeros_like(x)
            self.M2 = np.zeros_like(x)
            self.min = np.full_like(x, np.inf)
            self.max = np.full_like(x, -np.inf)

        self.n += 1

        # Update mean, M2 for variance, min, and max
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2
        self.min = np.minimum(self.min, x)
        self.max = np.maximum(self.max, x)

    def _get_safe_value(self, value, default=0):
        """
        Return the value if it's not None, otherwise return default.

        Args:
        - value: Value to check.
        - default: Default value to return if value is None.

        Returns:
        - Value or default.
        """
        return value if value is not None else default

    def get_mean(self) -> np.ndarray:
        return self._get_safe_value(self.mean)

    def get_variance(self) -> np.ndarray:
        if self.n > 1:
            return self._get_safe_value(self.M2 / (self.n - 1))
        return self._get_safe_value(self.M2)

    def get_standard_deviation(self) -> np.ndarray:
        return np.sqrt(self.get_variance())

    def get_min(self) -> np.ndarray:
        return self._get_safe_value(self.min)

    def get_max(self) -> np.ndarray:
        return self._get_safe_value(self.max)

    def get_averages(self) -> dict:
        """
        Calculate the averages of the statistical properties.

        Returns:
        - A dictionary containing average statistics.
        """
        return {
            "shape": self.shape,
            "type": self.dtype,
            "average_mean": np.mean(self.get_mean()),
            "average_variance": np.mean(self.get_variance()),
            "average_std_dev": np.mean(self.get_standard_deviation()),
            "average_min": np.mean(self.get_min()),
            "average_max": np.mean(self.get_max()),
        }

    def to_dict(self) -> dict:
        """
        Convert the RunningStats to a dictionary format.

        Returns:
        - A dictionary containing the statistics.
        """
        serialize_array = lambda x: x.tolist() if isinstance(x, np.ndarray) else x
        averages = self.get_averages()

        return {
            "averages": {
                key: serialize_array(value) for key, value in averages.items()
            },
            "full": {
                "mean": serialize_array(self.get_mean()),
                "variance": serialize_array(self.get_variance()),
                "std_dev": serialize_array(self.get_standard_deviation()),
                "min": serialize_array(self.get_min()),
                "max": serialize_array(self.get_max()),
                "shape": self.shape,
                "dtype": str(self.dtype),
                "example": serialize_array(self.example),
            },
        }


class RunningStatsDatapoints:
    """
    Maintains running statistics for a dataset, including features and labels.
    """

    def __init__(self):
        self.features = RunningStats()
        self.labels = RunningStats()
        self.n = 0

    def update(self, feature: np.ndarray, label: np.ndarray):
        """
        Update the statistics with new feature and label data points.

        Args:
        - feature (np.ndarray): A feature data point.
        - label (np.ndarray): A label data point.
        """
        self.features.push(feature)
        self.labels.push(label)
        self.n += 1

    def get_feature_stats(self) -> dict:
        return self.features.to_dict()

    def get_label_stats(self) -> dict:
        return self.labels.to_dict()

    def __str__(self) -> str:
        """
        Create a string representation of the statistics.

        Returns:
        - A formatted string of the statistics.
        """
        feature_averages = self.features.get_averages()
        label_averages = self.labels.get_averages()

        features_str = "Features Averages:\n" + "\n".join(
            f"{key}: {value}" for key, value in feature_averages.items()
        )
        labels_str = "Labels Averages:\n" + "\n".join(
            f"{key}: {value}" for key, value in label_averages.items()
        )

        return features_str + "\n" + labels_str

    def to_dict(self, reduced: bool = False) -> dict:
        """
        Create a dictionary representation of the statistics.

        Args:
        - reduced (bool): Whether to return only the average statistics.

        Returns:
        - A dictionary containing the statistics.
        """
        if reduced:
            return {
                "samples": self.n,
                "features": self.features.get_averages(),
                "labels": self.labels.get_averages(),
            }

        return {
            "samples": self.n,
            "features": self.get_feature_stats(),
            "labels": self.get_label_stats(),
        }


def calculate_dataset_running_stats(
    dataset: tf.data.Dataset,
    feature_dims: Union[int, tuple] = None,
    label_dims: Union[int, tuple] = None,
) -> RunningStatsDatapoints:
    """
    Calculate running statistics for a TensorFlow dataset.

    Args:
    - dataset (tf.data.Dataset): A TensorFlow dataset.
    - feature_dims (Union[int, tuple]): Dimensions of a feature.
    - label_dims (Union[int, tuple]): Dimensions of a label.

    Returns:
    - RunningStatsDatapoints: An object containing the statistics.
    """
    stats = RunningStatsDatapoints()

    for features, labels in dataset:
        features_numpy, labels_numpy = features.numpy(), labels.numpy()

        if feature_dims and label_dims:
            for feature, label in zip(features_numpy, labels_numpy):
                stats.update(feature.reshape(feature_dims), label.reshape(label_dims))
        else:
            stats.update(features_numpy, labels_numpy)

    return stats
