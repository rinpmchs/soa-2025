import unittest
from unittest.mock import MagicMock
from proto import stats_pb2 as pb
from stats_service import StatisticsServicer
from database import db


class TestStatisticsService(unittest.TestCase):
    def setUp(self):
        self.servicer = StatisticsServicer()
        self.orig_execute = db.execute

    def tearDown(self):
        db.execute = self.orig_execute

    def test_get_post_stats_normal(self):
        db.execute = MagicMock(return_value=[(10, 2, 5)])
        req = pb.PostStatsRequest(post_id="p1")
        res = self.servicer.GetPostStats(req, None)
        self.assertEqual(res.views, 10)
        self.assertEqual(res.likes, 2)
        self.assertEqual(res.comments, 5)

    def test_get_post_stats_empty(self):
        db.execute = MagicMock(return_value=[(0, 0, 0)])
        req = pb.PostStatsRequest(post_id="unknown")
        res = self.servicer.GetPostStats(req, None)
        self.assertEqual(res.views, 0)
        self.assertEqual(res.likes, 0)
        self.assertEqual(res.comments, 0)

    def test_get_daily_methods(self):
        sample_rows = [("2025-05-20", 3), ("2025-05-21", 5)]
        db.execute = MagicMock(return_value=sample_rows)
        for method in [
            self.servicer.GetPostViewsDaily,
            self.servicer.GetPostLikesDaily,
            self.servicer.GetPostCommentsDaily,
        ]:
            res = method(pb.PostStatsRequest(post_id="p1"), None)
            self.assertEqual(len(res.stats), 2)
            self.assertEqual(res.stats[0].date, "2025-05-20")
            self.assertEqual(res.stats[0].count, 3)

    def test_top_posts_and_users(self):
        # Simulate top posts
        db.execute = MagicMock(return_value=[("p1", 100), ("p2", 50)])
        req = pb.TopRequest(metric=pb.TopRequest.Metric.LIKES, limit=2)
        posts_res = self.servicer.GetTopPosts(req, None)
        self.assertEqual(len(posts_res.posts), 2)
        self.assertEqual(posts_res.posts[0].id, "p1")
        self.assertEqual(posts_res.posts[0].count, 100)

        # Simulate top users
        db.execute = MagicMock(return_value=[("u1", 80), ("u2", 20)])
        users_res = self.servicer.GetTopUsers(req, None)
        self.assertEqual(len(users_res.users), 2)
        self.assertEqual(users_res.users[0].id, "u1")
        self.assertEqual(users_res.users[0].count, 80)

    def test_top_limit_zero(self):
        db.execute = MagicMock(return_value=[])
        req = pb.TopRequest(metric=pb.TopRequest.Metric.VIEWS, limit=0)
        posts_res = self.servicer.GetTopPosts(req, None)
        self.assertEqual(posts_res.posts, [])

if __name__ == '__main__':
    unittest.main()