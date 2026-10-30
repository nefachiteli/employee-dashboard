from .query_base import QueryBase


class Team(QueryBase):

    name = "team"

    def names(self):
        sql = "SELECT team_name, team_id FROM team ORDER BY team_id"
        return self.query(sql)

    def username(self, team_id):
        sql = "SELECT team_name FROM team WHERE team_id = ?"
        return self.query(sql, (team_id,))

    def model_data(self, team_id):
        # one row per employee; the dashboard averages the predictions
        sql = """
            SELECT SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM employee_events
            WHERE team_id = ?
            GROUP BY employee_id
        """
        return self.pandas_query(sql, (team_id,))
