
import unittest
from unittest.mock import patch
from yummy_app import YummyApp
import gps_service


# ================================================================
# CAP DO 1: Bo test co ban cho san (~35% Coverage)
# ================================================================
class TestEasyLevel(unittest.TestCase):
    """Kiem thu chuc nang co ban tinh tien don hang"""

    def setUp(self):
        self.app = YummyApp()

    def test_calculate_total_for_single_item(self):
        cart = {"pho": 2}
        self.assertEqual(self.app.calculate_order_total(cart), 100000)

    def test_calculate_total_for_multiple_items(self):
        cart = {"pho": 1, "bun": 1}
        self.assertEqual(self.app.calculate_order_total(cart), 95000)

    def test_calculate_total_for_empty_cart(self):
        self.assertEqual(self.app.calculate_order_total({}), 0.0)

    def test_calculate_total_with_zero_quantity(self):
        cart = {"pho": 0}
        self.assertEqual(self.app.calculate_order_total(cart), 0.0)


# ================================================================
# CAP DO 2: TestMediumLevel - 4 test case bat buoc
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """Kiem thu chuc nang ap dung ma khuyen mai"""

    def setUp(self):
        self.app = YummyApp(
            network_status="online",
            os_version=15
        )

    # TC01: Online - ma giam gia hop le
    def test_apply_promo_code_success(self):
        result = self.app.apply_promo_code(
            100000, "GIAM10"
        )
        self.assertEqual(result, 90000.0)

    # TC02: Offline - nem ConnectionError
    def test_apply_promo_code_offline_error(self):
        offline_app = YummyApp(
            network_status="offline",
            os_version=15
        )

        with self.assertRaises(ConnectionError):
            offline_app.apply_promo_code(
                100000, "GIAM10"
            )

    # TC03: Ma dac biet tren OS 15 - thanh cong
    def test_apply_promo_code_special_os15(self):
        result = self.app.apply_promo_code(
            100000, "NEW_OS_ONLY"
        )
        self.assertEqual(result, 80000.0)

    # TC04: Ma dac biet tren OS 14 - nem ValueError
    def test_apply_promo_code_low_os_version(self):
        old_os_app = YummyApp(
            network_status="online",
            os_version=14
        )

        with self.assertRaises(ValueError):
            old_os_app.apply_promo_code(
                100000, "NEW_OS_ONLY"
            )

    # Test bo sung: Ma khuyen mai khong ton tai
    def test_apply_promo_code_invalid_code(self):
        with self.assertRaises(ValueError):
            self.app.apply_promo_code(
                100000, "MA_GIA"
            )


# ================================================================
# CAP DO 3: TestHardLevel - 3 test case Mocking GPS
# ================================================================
class TestHardLevel(unittest.TestCase):
    """Kiem thu dich vu GPS bang ky thuat Mocking"""

    def setUp(self):
        self.app = YummyApp()

    # TC05: GPS trong vung (10.0, 105.0)
    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_success(
        self, mock_get_location
    ):
        mock_get_location.return_value = (10.0, 105.0)

        restaurants = self.app.get_nearby_restaurants()

        self.assertEqual(
            restaurants,
            [
                "Nha hang Pho Ly Quoc Su",
                "Bun cha Huong Lien"
            ]
        )

    # TC06: GPS ngoai vung (20.0, 110.0)
    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_empty_location(
        self, mock_get_location
    ):
        mock_get_location.return_value = (20.0, 110.0)

        restaurants = self.app.get_nearby_restaurants()

        self.assertEqual(restaurants, [])

    # TC07: GPS mat tin hieu
    @patch("yummy_app.gps_service.get_current_location")
    def test_get_nearby_restaurants_signal_lost(
        self, mock_get_location
    ):
        mock_get_location.side_effect = (
            gps_service.GPSSignalLostError()
        )

        result = self.app.get_nearby_restaurants()

        self.assertEqual(
            result,
            "Khong the xac dinh vi tri."
        )


if __name__ == "__main__":
    unittest.main()
