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
# CAP DO 2: Kiem thu chuc nang ap dung ma khuyen mai (apply_promo_code)
# ================================================================
class TestMediumLevel(unittest.TestCase):
    """Kiem thu chuc nang ap dung ma khuyen mai"""

    def setUp(self):
        self.app = YummyApp(network_status="online", os_version=15)

    def test_apply_promo_code_success(self):
        """1. Ap dung ma hop le khi online va HDH thoa man"""
        result = self.app.apply_promo_code(100000, "GIAM10")
        self.assertEqual(result, 90000.0)

    def test_apply_promo_code_offline_error(self):
        """2. Ngoai le khi thiet bi o trang thai offline"""
        offline_app = YummyApp(network_status="offline", os_version=15)
        with self.assertRaises(ConnectionError):
            offline_app.apply_promo_code(100000, "GIAM10")

    def test_apply_promo_code_invalid_code(self):
        """3. Ngoai le khi nhap ma khuyen mai khong ton tai"""
        with self.assertRaises(ValueError):
            self.app.apply_promo_code(100000, "MA_GIA")

    def test_apply_promo_code_low_os_version(self):
        """4. Ngoai le khi phien ban HDH thap hon yeu cau cua ma"""
        old_os_app = YummyApp(network_status="online", os_version=10)
        with self.assertRaises(ValueError):
            old_os_app.apply_promo_code(100000, "NEW_OS_ONLY")


# ================================================================
# CAP DO 3: Kiem thu mo phong GPS service (@patch)
# ================================================================
class TestHardLevel(unittest.TestCase):
    """Kiem thu dich vu dinh vi GPS bang kü thuat Mocking (@patch)"""

    def setUp(self):
        self.app = YummyApp()

    @patch("gps_service.get_current_location")
    def test_get_nearby_restaurants_success(self, mock_get_location):
        """1. Lay danh sach nha hang thanh cong khi co toa do GPS"""
        mock_get_location.return_value = (10.0, 105.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(
            restaurants, ["Nha hang Pho Ly Quoc Su", "Bun cha Huong Lien"]
        )

    @patch("gps_service.get_current_location")
    def test_get_nearby_restaurants_signal_lost(self, mock_get_location):
        """2. Xu ly khi bi mat tin hieu GPS (GPSSignalLostError)"""
        mock_get_location.side_effect = gps_service.GPSSignalLostError()
        result = self.app.get_nearby_restaurants()
        self.assertEqual(result, "Khong the xac dinh vi tri.")

    @patch("gps_service.get_current_location")
    def test_get_nearby_restaurants_empty_location(self, mock_get_location):
        """3. Toa do khong co nha hang nao"""
        mock_get_location.return_value = (0.0, 0.0)
        restaurants = self.app.get_nearby_restaurants()
        self.assertEqual(restaurants, [])


if __name__ == "__main__":
    unittest.main()