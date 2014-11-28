"""Tests for the models of the aps_production app."""
from django.test import TestCase
from django.utils.timezone import now, timedelta

from . import factories


class ErrorTestCase(TestCase):
    """Tests for the ``Error`` model class."""
    longMessage = True

    def test_instantiation(self):
        error = factories.ErrorFactory()
        self.assertTrue(error.pk)


class ErrorBinTestCase(TestCase):
    """Tests for the ``ErrorBin`` model class."""
    longMessage = True

    def test_instantiation(self):
        error_bin = factories.ErrorBinFactory()
        self.assertTrue(error_bin.pk)


class OrderTestCase(TestCase):
    """Tests for the ``Order`` model class."""
    longMessage = True

    def test_instantiation(self):
        order = factories.OrderFactory()
        self.assertTrue(order.pk)


class OrderLineTestCase(TestCase):
    """Tests for the ``OrderLine`` model class."""
    longMessage = True

    def setUp(self):
        self.line = factories.OrderLineFactory()

    def test_instantiation(self):
        self.assertTrue(self.line.pk)

    def test_date_shipped(self):
        # this test does not cover any case with child OrderRuns
        # it assumes, that any parent OrderRun is only set to is_open==False
        # if all child runs are done already
        self.assertIsNone(self.line.date_shipped, msg=(
            'When there are no shipments, date_shipped should return None.'
        ))

        shipment1 = factories.ShipmentFactory(
            order_run__order_line=self.line,
        )
        shipment2 = factories.ShipmentFactory(
            order_run__order_line=self.line,
            date_shipped=now() - timedelta(days=1),
        )
        self.assertIsNone(self.line.date_shipped, msg=(
            'When there are only shipments, that have open runs, date_shipped'
            ' should return None.'
        ))

        shipment1.order_run.is_open = False
        shipment1.order_run.save()
        self.assertIsNone(self.line.date_shipped, msg=(
            'When there are some shipments left, that still have open runs,'
            ' date_shipped should return None.'
        ))

        shipment2.order_run.is_open = False
        shipment2.order_run.save()
        self.assertEqual(self.line.date_shipped, shipment1.date_shipped,
            msg=(
                'When there are no more shipments, that have open runs,'
                ' date_shipped should return the date of the latest shipment.'
        ))

    def test_date_delivered(self):
        # this test does not cover any case with child OrderRuns
        # it assumes, that any parent OrderRun is only set to is_open==False
        # if all child runs are done already
        self.assertIsNone(self.line.date_delivered, msg=(
            'When there are no shipments, date_delivered should return None.'
        ))

        shipment1 = factories.ShipmentFactory(
            order_run__order_line=self.line,
        )
        shipment2 = factories.ShipmentFactory(
            order_run__order_line=self.line,
            date_shipped=now() - timedelta(days=1),
        )
        self.assertIsNone(self.line.date_delivered, msg=(
            'When there are only shipments, that have open runs,'
            ' date_delivered should return None.'
        ))

        shipment1.order_run.is_open = False
        shipment1.order_run.save()
        self.assertIsNone(self.line.date_delivered, msg=(
            'When there are some shipments left, that still have open runs,'
            ' date_delivered should return None.'
        ))

        shipment2.order_run.is_open = False
        shipment2.order_run.save()
        self.assertEqual(
            self.line.date_delivered, shipment1.date_shipped + timedelta(
                days=3
            ),
             msg=(
                 'When there are no more shipments, that have open runs,'
                 ' date_delivered should return the date of the latest'
                 ' shipment.'
             ))


class OrderRunTestCase(TestCase):
    """Tests for the ``OrderRun`` model class."""
    longMessage = True

    def test_instantiation(self):
        order_run = factories.OrderRunFactory()
        self.assertTrue(order_run.pk)


class ShipmentTestCase(TestCase):
    """Tests for the ``Shipment`` model class."""
    longMessage = True

    def test_instantiation(self):
        shipment = factories.ShipmentFactory()
        self.assertTrue(shipment.pk)
