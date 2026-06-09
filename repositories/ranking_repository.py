# repositories/ranking_repository.py

from core.database import Database


class RankingRepository:
    @staticmethod
    def get_institutional_rankings():

        conn = Database.connection()

        return conn.execute("""
            SELECT *
            FROM institutional_rankings
            ORDER BY institutional_score DESC
        """).df()
