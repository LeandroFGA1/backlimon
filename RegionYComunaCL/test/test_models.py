from django.test import TestCase
from RegionYComunaCL.models import Region, Comuna


class RegionComunaModelTest(TestCase):

    def test_region_meta_options(self):
        self.assertEqual(Region._meta.db_table, 'nombre_tabla_region')
        self.assertFalse(Region._meta.managed)

    def test_comuna_meta_options(self):
        self.assertEqual(Comuna._meta.db_table, 'nombre_tabla_comuna')
        self.assertFalse(Comuna._meta.managed)
