from .query_base import QueryBase


class Employee(QueryBase):

    name = "employee"

    def names(self):
        sql = """
            SELECT first_name || ' ' || last_name AS full_name, employee_id
            FROM employee
            ORDER BY employee_id
        """
        return self.query(sql)

    def username(self, employee_id):
        sql = """
            SELECT first_name || ' ' || last_name
            FROM employee
            WHERE employee_id = ?
        """
        return self.query(sql, (employee_id,))

    def model_data(self, employee_id):
        sql = """
            SELECT SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM employee_events
            WHERE employee_id = ?
        """
        return self.pandas_query(sql, (employee_id,))
