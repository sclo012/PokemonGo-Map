import unittest
import datetime
import logging

from pogom import models

logging.basicConfig(format='%(asctime)s [%(threadName)16s][%(module)14s]'
                           '[%(levelname)8s] %(message)s')
logging.getLogger().setLevel(logging.DEBUG)


def add_query_entry(query, encounter_id, hour, minute, second):
    query.append({
        'encounter_id': encounter_id,
        'scan_time': datetime.datetime(2017, 1, 11, hour, minute, second)
    })


def get_spawnpoint():
    sp = {
        'id': '1',
        'latitude': 0,
        'longitude': 0,
        'last_scanned': None,  # Null value used as new flag
        'kind': 'hhhs',
        'links': '????',
        'missed_count': 0,
        'latest_seen': 0,
        'earliest_unseen': None
    }

    models.SpawnpointDetectionData.set_default_earliest_unseen(sp)

    return sp


class ModelsTest(unittest.TestCase):
    def test_classify_hhhs(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 14:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 18, 0, 0)
        add_query_entry(query, '1', 18, 14, 59)

        add_query_entry(query, '2', 19, 0, 0)
        add_query_entry(query, '2', 19, 14, 59)

        add_query_entry(query, '3', 20, 0, 0)
        add_query_entry(query, '3', 20, 14, 59)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hhhs')
        self.assertEqual(sp['links'], 'hhh?')
        self.assertEqual(sp['latest_seen'], 14 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'], 14 * 60)

    def test_classify_hhss(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 29:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 18, 0, 0)
        add_query_entry(query, '1', 18, 14, 59)
        add_query_entry(query, '1', 18, 29, 59)

        add_query_entry(query, '2', 19, 0, 0)
        add_query_entry(query, '2', 19, 14, 59)
        add_query_entry(query, '2', 19, 29, 59)

        add_query_entry(query, '3', 20, 0, 0)
        add_query_entry(query, '3', 20, 14, 59)
        add_query_entry(query, '3', 20, 29, 59)

        sp['earliest_unseen'] = 0

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hhss')
        self.assertEqual(sp['links'], 'hh??')
        self.assertEqual(sp['latest_seen'], 29 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'],
                         (sp['latest_seen'] + 14 * 60) % 3600)

    def test_classify_hsss(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 44:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 18, 0, 0)
        add_query_entry(query, '1', 18, 14, 59)
        add_query_entry(query, '1', 18, 29, 59)
        add_query_entry(query, '1', 18, 44, 59)

        add_query_entry(query, '2', 19, 0, 0)
        add_query_entry(query, '2', 19, 14, 59)
        add_query_entry(query, '2', 19, 29, 59)
        add_query_entry(query, '2', 19, 44, 59)

        add_query_entry(query, '3', 20, 0, 0)
        add_query_entry(query, '3', 20, 14, 59)
        add_query_entry(query, '3', 20, 29, 59)
        add_query_entry(query, '3', 20, 44, 59)

        sp['earliest_unseen'] = 0

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hsss')
        self.assertEqual(sp['links'], 'h???')
        self.assertEqual(sp['latest_seen'], 44 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'],
                         (sp['latest_seen'] + 14 * 60) % 3600)

    def test_classify_hshs(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 14:59, then
        from 30:00 to 44:59
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 18, 0, 0)
        add_query_entry(query, '1', 18, 14, 59)
        add_query_entry(query, '1', 18, 30, 00)
        add_query_entry(query, '1', 18, 44, 59)

        add_query_entry(query, '2', 19, 0, 0)
        add_query_entry(query, '2', 19, 14, 59)
        add_query_entry(query, '2', 19, 30, 00)
        add_query_entry(query, '2', 19, 44, 59)

        add_query_entry(query, '3', 20, 0, 0)
        add_query_entry(query, '3', 20, 14, 59)
        add_query_entry(query, '3', 20, 30, 00)
        add_query_entry(query, '3', 20, 44, 59)

        sp['latest_seen'] = 44 * 60 + 59
        sp['earliest_unseen'] = 15 * 60

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'hshs')
        self.assertEqual(sp['links'], 'h?h?')
        self.assertEqual(sp['latest_seen'], 44 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'],
                         (sp['latest_seen'] + 14 * 60) % 3600)

    def test_classify_1x60_1(self):
        """
        Simulate a spawn point that ranges from minute 00:00 to 58:59
        """
        sp = get_spawnpoint()

        query = []

        for minute in range(0, 59, 14):
            add_query_entry(query, '1', 18, minute, 0)
        add_query_entry(query, '1', 18, 58, 59)

        for minute in range(0, 59, 14):
            add_query_entry(query, '2', 19, minute, 0)
        add_query_entry(query, '2', 19, 58, 59)

        add_query_entry(query, '3', 20, 0, 0)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['latest_seen'], 3600 - 61)
        self.assertEqual(sp['earliest_unseen'], 0)
        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')

    def test_classify_1x60_2(self):
        """
        Test a more difficult one where different spawnpoints overlap different
        times
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 18, 0, 0)
        add_query_entry(query, '1', 18, 14, 59)

        add_query_entry(query, '2', 19, 15, 0)
        add_query_entry(query, '2', 19, 29, 59)

        add_query_entry(query, '3', 20, 30, 0)
        add_query_entry(query, '3', 20, 44, 59)

        add_query_entry(query, '4', 21, 45, 0)
        add_query_entry(query, '4', 21, 58, 59)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')
        self.assertEqual(sp['latest_seen'], 3600 - 61)
        self.assertEqual(sp['earliest_unseen'], 0)

    def test_classify_1x60_3(self):
        """
        Test a difficult one where different spawnpoints overlap different
        times
        """
        sp = get_spawnpoint()

        query = []

        add_query_entry(query, '1', 18, 0, 0)
        add_query_entry(query, '1', 18, 12, 59)
        add_query_entry(query, '1', 18, 18, 59)
        add_query_entry(query, '1', 18, 55, 59)

        add_query_entry(query, '2', 20, 30, 0)
        add_query_entry(query, '2', 20, 46, 59)

        models.SpawnpointDetectionData.classify_sp(query, sp, None)

        self.assertEqual(sp['kind'], 'ssss')
        self.assertEqual(sp['links'], '+++-')
        self.assertEqual(sp['latest_seen'], 55 * 60 + 59)
        self.assertEqual(sp['earliest_unseen'], 0)
