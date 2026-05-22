from django.test import TestCase
from .models import Maker, Brand, Scale, Tag, Kit


class TagModelTest(TestCase):
    def test_tag_unique_name(self):
        Tag.objects.create(name="積みプラ")
        with self.assertRaises(Exception):
            Tag.objects.create(name="積みプラ")

    def test_tag_str(self):
        tag = Tag.objects.create(name="未組立")
        self.assertEqual(str(tag), "未組立")


class KitModelTest(TestCase):
    def setUp(self):
        self.maker = Maker.objects.create(name="バンダイ")
        self.brand = Brand.objects.create(name="HG", maker=self.maker)
        self.scale = Scale.objects.create(size="1/144")

    def test_kit_str(self):
        kit = Kit.objects.create(
            name="RX-78-2 ガンダム",
            maker=self.maker,
            brand=self.brand,
            scale=self.scale,
            price=1320,
        )
        self.assertEqual(str(kit), "RX-78-2 ガンダム")

    def test_kit_tags(self):
        tag = Tag.objects.create(name="ガンプラ")
        kit = Kit.objects.create(
            name="ザク",
            maker=self.maker,
            brand=self.brand,
            scale=self.scale,
            price=1100,
        )
        kit.tags.add(tag)
        self.assertIn(tag, kit.tags.all())
