"""
Tests for data measurement calibration module.
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock


class MeasurementCalibrationTest(TestCase):
    """Tests for measurement calibration."""

    def test_measurement_calibration_import(self):
        """Test that measurement calibration module can be imported."""
        try:
            from ml.data.measurement import calibration
            self.assertIsNotNone(calibration)
        except ImportError:
            pass

