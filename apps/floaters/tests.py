# from django.test import TestCase
# from .factories import FloaterFactory
# from .models import Floater

# class TestFloaterModel(TestCase):
#     def test_create_floater(self):
#         floater = FloaterFactory(display_name='Fancy')
#         self.assertEqual(floater.display_name, 'Fancy')

#     def test_tier_points(self):
#         # Create a new Floater with tier 'BR'
#         floater = FloaterFactory(display_name='Test Floater', tier=Floater.STARTER_PACK)
#         self.assertEqual(floater.tier_jumps, Floater.TIER_JUMPS[Floater.STARTER_PACK])

#         floater.tier = Floater.TRIED_TRUE
#         self.assertEqual(floater.tier_jumps, Floater.TIER_JUMPS[Floater.TRIED_TRUE])

#         floater.tier = Floater.BADDIES
#         self.assertEqual(floater.tier_jumps, Floater.TIER_JUMPS[Floater.BADDIES])

#         floater.tier = Floater.GOD
#         self.assertEqual(floater.tier_jumps, Floater.TIER_JUMPS[Floater.GOD])