from django.test import TestCase
import numpy as np
from kmtshi.coordinates import great_circle_distance
from astropy.coordinates import SkyCoord
from astropy import units

seed = 10129041
np.random.seed(seed)


class CoordinatesTestCase(TestCase):
    def test_great_circle_distance(self):
        # Some simple test cases along the equator
        np.testing.assert_allclose(great_circle_distance(0, 0, 100, 0), 100.0, atol=1e-5)
        np.testing.assert_allclose(great_circle_distance(0, 0, 181, 0), 179.0, atol=1e-5)

        # Test along longitudinal lines
        np.testing.assert_allclose(great_circle_distance(0, 0, 0, 10), 10, atol=1e-5)
        np.testing.assert_allclose(great_circle_distance(0, 75, 180, 75), 30.0, atol=1e-5)

        # Test a few points against astropy
        for i in range(100):
            test_ra = np.random.uniform(0, 360, size=2)
            test_dec = np.random.uniform(-90, 90, size=2)
            astropy_coord1 = SkyCoord(test_ra[0], test_dec[0], unit=(units.deg, units.deg))
            astropy_coord2 = SkyCoord(test_ra[1], test_dec[1], unit=(units.deg, units.deg))
            np.testing.assert_allclose(astropy_coord1.separation(astropy_coord2).deg,
                                       great_circle_distance(test_ra[0], test_dec[0],
                                                             test_ra[1], test_dec[1]))
