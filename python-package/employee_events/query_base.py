from .sql_execution import SQLExecutionMixin


class QueryBase(SQLExecutionMixin):
    """Queries shared by Employee and Team.

    Subclasses set `name` to "employee" or "team", which selects the
    matching `<name>_id` column in the SQL below.
    """

    name = ""

    def names(self):
        """Return (display name, id) pairs. Overridden by subclasses."""
        return []

    def event_counts(self, entity_id):
        """Daily positive and negative event totals, oldest first."""
        sql = f"""
            SELECT event_date,
                   SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM employee_events
            WHERE {self.name}_id = ?
            GROUP BY event_date
            ORDER BY event_date
        """
        return self.pandas_query(sql, (entity_id,))

    def notes(self, entity_id):
        """Manager notes, newest first."""
        sql = f"""
            SELECT note_date, note
            FROM notes
            WHERE {self.name}_id = ?
            ORDER BY note_date DESC
        """
        return self.pandas_query(sql, (entity_id,))
