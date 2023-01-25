import unittest
from PokeAlarm.Utilities.PvpUtils import get_pvp_info


class TestGetPvpInfo(unittest.TestCase):
    def test_eevee_a1_d15_s15_l14(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(133, 0, 1, 15, 15, 14)

        self.assertEqual(100.0, g_rating, msg="great league rating")
        self.assertEqual(134, g_id, msg="great league pokemon")
        self.assertEqual(1500, g_cp, msg="great league combat power")
        self.assertEqual(18, g_level, msg="great league level")
        self.assertEqual((41, 0), g_candy, msg="great league candy / xl")
        self.assertEqual(15200, g_stardust, msg="great league stardust")

        self.assertEqual(100.0, u_rating, msg="ultra league rating")
        self.assertEqual(136, u_id, msg="ultra league pokemon")
        self.assertEqual(2498, u_cp, msg="ultra league combat power")
        self.assertEqual(31, u_level, msg="ultra league level")
        self.assertEqual((173, 0), u_candy, msg="ultra league candy / xl")
        self.assertEqual(109600, u_stardust, msg="ultra league stardust")

    def test_umbreon_a0_d15_s14_l25(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(197, 0, 0, 15, 14, 25)

        self.assertEqual(100.0, g_rating, msg="great league rating")
        self.assertEqual(197, g_id, msg="great league pokemon")
        self.assertEqual(1497, g_cp, msg="great league combat power")
        self.assertEqual(27.5, g_level, msg="great league level")
        self.assertEqual((18, 0), g_candy, msg="great league candy / xl")
        self.assertEqual(20500, g_stardust, msg="great league stardust")

        self.assertEqual(88.9, u_rating, msg="ultra league rating")
        self.assertEqual(197, u_id, msg="ultra league pokemon")
        self.assertEqual(2154, u_cp, msg="ultra league combat power")
        self.assertEqual(50, u_level, msg="ultra league level")
        self.assertEqual((220, 296), u_candy, msg="ultra league candy / xl")
        self.assertEqual(444000, u_stardust, msg="ultra league stardust")

    def test_toxicroak_a0_d15_s12_l5(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(454, 0, 0, 15, 12, 5)

        self.assertEqual(98.03, g_rating, msg="great league rating")
        self.assertEqual(454, g_id, msg="great league pokemon")
        self.assertEqual(1482, g_cp, msg="great league combat power")
        self.assertEqual(22.5, g_level, msg="great league level")
        self.assertEqual((61, 0), g_candy, msg="great league candy / xl")
        self.assertEqual(56600, g_stardust, msg="great league stardust")

        self.assertEqual(100.0, u_rating, msg="ultra league rating")
        self.assertEqual(454, u_id, msg="ultra league pokemon")
        self.assertEqual(2500, u_cp, msg="ultra league combat power")
        self.assertEqual(46.5, u_level, msg="ultra league level")
        self.assertEqual((296, 165), u_candy, msg="ultra league candy / xl")
        self.assertEqual(418600, u_stardust, msg="ultra league stardust")

    def test_marill_a0_d15_s15_l9(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(183, 0, 0, 15, 15, 9)

        self.assertEqual(100.0, g_rating, msg="great league rating")
        self.assertEqual(184, g_id, msg="great league pokemon")
        self.assertEqual(1499, g_cp, msg="great league combat power")
        self.assertEqual(45.5, g_level, msg="great league level")
        self.assertEqual((313, 133), g_candy, msg="great league candy / xl")
        self.assertEqual(387000, g_stardust, msg="great league stardust")

        self.assertEqual(88.19, u_rating, msg="ultra league rating")
        self.assertEqual(184, u_id, msg="ultra league pokemon")
        self.assertEqual(1583, u_cp, msg="ultra league combat power")
        self.assertEqual(50, u_level, msg="ultra league level")
        self.assertEqual((313, 296), u_candy, msg="ultra league candy / xl")
        self.assertEqual(512000, u_stardust, msg="ultra league stardust")

    def test_burmy_plant_a0_d15_s15_l23(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(412, 118, 0, 15, 15, 23)

        self.assertEqual(100.0, g_rating, msg="great league rating")
        self.assertEqual(413, g_id, msg="great league pokemon")
        self.assertEqual(1500, g_cp, msg="great league combat power")
        self.assertEqual(35.5, g_level, msg="great league level")
        self.assertEqual((174, 0), g_candy, msg="great league candy / xl")
        self.assertEqual(128000, g_stardust, msg="great league stardust")

        self.assertEqual(92.5, u_rating, msg="ultra league rating")
        self.assertEqual(414, u_id, msg="ultra league pokemon")
        self.assertEqual(1898, u_cp, msg="ultra league combat power")
        self.assertEqual(50, u_level, msg="ultra league level")
        self.assertEqual((332, 296), u_candy, msg="ultra league candy / xl")
        self.assertEqual(458000, u_stardust, msg="ultra league stardust")

    def test_burmy_unknown_form(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(412, 999999, 0, 15, 15, 23)

        self.assertEqual(0.0, g_rating, msg="great league rating")
        self.assertEqual(412, g_id, msg="great league pokemon")
        self.assertEqual(0, g_cp, msg="great league combat power")
        self.assertEqual(0, g_level, msg="great league level")
        self.assertEqual((0, 0), g_candy, msg="great league candy / xl")
        self.assertEqual(0, g_stardust, msg="great league stardust")

        self.assertEqual(0.0, u_rating, msg="ultra league rating")
        self.assertEqual(412, u_id, msg="ultra league pokemon")
        self.assertEqual(0, u_cp, msg="ultra league combat power")
        self.assertEqual(0, u_level, msg="ultra league level")
        self.assertEqual((0, 0), u_candy, msg="ultra league candy / xl")
        self.assertEqual(0, u_stardust, msg="ultra league stardust")

    def test_giratina_altered_a0_d14_s15_l20(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(487, 90, 0, 14, 15, 20)

        self.assertEqual(0.0, g_rating, msg="great league rating")
        self.assertEqual(487, g_id, msg="great league pokemon")
        self.assertEqual(1471, g_cp, msg="great league combat power")
        self.assertEqual(16.5, g_level, msg="great league level")
        self.assertEqual((0, 0), g_candy, msg="great league candy / xl")
        self.assertEqual(0, g_stardust, msg="great league stardust")

        self.assertEqual(100.0, u_rating, msg="ultra league rating")
        self.assertEqual(487, u_id, msg="ultra league pokemon")
        self.assertEqual(2497, u_cp, msg="ultra league combat power")
        self.assertEqual(28, u_level, msg="ultra league level")
        self.assertEqual((50, 0), u_candy, msg="ultra league candy / xl")
        self.assertEqual(56000, u_stardust, msg="ultra league stardust")

    def test_giratina_origin_a0_d14_s15_l20(self):
        (
            g_rating,
            g_id,
            g_cp,
            g_level,
            g_candy,
            g_stardust,
            u_rating,
            u_id,
            u_cp,
            u_level,
            u_candy,
            u_stardust,
        ) = get_pvp_info(487, 91, 0, 14, 15, 20)

        self.assertEqual(0.0, g_rating, msg="great league rating")
        self.assertEqual(487, g_id, msg="great league pokemon")
        self.assertEqual(1476, g_cp, msg="great league combat power")
        self.assertEqual(15, g_level, msg="great league level")
        self.assertEqual((0, 0), g_candy, msg="great league candy / xl")
        self.assertEqual(0, g_stardust, msg="great league stardust")

        self.assertEqual(97.55, u_rating, msg="ultra league rating")
        self.assertEqual(487, u_id, msg="ultra league pokemon")
        self.assertEqual(2460, u_cp, msg="ultra league combat power")
        self.assertEqual(25, u_level, msg="ultra league level")
        self.assertEqual((28, 0), u_candy, msg="ultra league candy / xl")
        self.assertEqual(31000, u_stardust, msg="ultra league stardust")


if __name__ == "__main__":
    unittest.main()
