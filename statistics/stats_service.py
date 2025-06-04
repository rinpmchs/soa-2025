import grpc
from clickhouse_driver import Client
import proto.stats_pb2 as pb
import proto.stats_pb2_grpc as grpc_pb
from database import db

class StatisticsServicer(grpc_pb.StatisticsServicer):
    def GetPostStats(self, request, context):
        post_id = request.post_id
        row = db.execute(
            "SELECT \n"
            "  countIf(event_type='view') AS views,\n"
            "  countIf(event_type='like') AS likes,\n"
            "  countIf(event_type='comment') AS comments\n"
            "FROM events WHERE post_id = %(id)s",
            {'id': post_id}
        )[0]
        return pb.PostStatsResponse(views=row[0], likes=row[1], comments=row[2])

    def _get_daily(self, post_id, event_type):
        rows = db.execute(
            "SELECT event_date, count() FROM events "
            "WHERE post_id = %(id)s AND event_type = %(evt)s "
            "GROUP BY event_date ORDER BY event_date",
            {'id': post_id, 'evt': event_type}
        )
        return [pb.DailyStat(date=str(r[0]), count=r[1]) for r in rows]

    def GetPostViewsDaily(self, request, context):
        stats = self._get_daily(request.post_id, 'view')
        return pb.DailyStatsResponse(stats=stats)

    def GetPostLikesDaily(self, request, context):
        stats = self._get_daily(request.post_id, 'like')
        return pb.DailyStatsResponse(stats=stats)

    def GetPostCommentsDaily(self, request, context):
        stats = self._get_daily(request.post_id, 'comment')
        return pb.DailyStatsResponse(stats=stats)

    def _get_top(self, metric, limit, by_user=False):
        evt = {'likes': 'like', 'views': 'view', 'comments': 'comment'}[metric]
        id_field = 'user_id' if by_user else 'post_id'
        rows = db.execute(
            f"SELECT {id_field}, count() AS cnt FROM events "
            f"WHERE event_type = %(evt)s GROUP BY {id_field} "
            f"ORDER BY cnt DESC LIMIT %(lim)s",
            {'evt': evt, 'lim': limit}
        )
        return [pb.TopItem(id=r[0], count=r[1]) for r in rows]

    def GetTopPosts(self, request, context):
        items = self._get_top(request.metric.name.lower(), request.limit)
        return pb.TopPostsResponse(posts=items)

    def GetTopUsers(self, request, context):
        items = self._get_top(request.metric.name.lower(), request.limit, by_user=True)
        return pb.TopUsersResponse(users=items)
