# Import QueryMixin to enable SQL execution methods
from employee_events.sql_execution import QueryMixin


# Define QueryBase using inheritance from QueryMixin
class QueryBase(QueryMixin):
    """Base class with shared SQL queries for Employee and Team."""

    # Class attribute to identify the table name
    name = ""

    def names(self) -> list:
        """Return a list of tuples with all available names and ids."""
        # Return empty list if no table name is set
        return []

    def event_counts(self, id: int):
        """
        Return a DataFrame with daily positive and negative
        event counts for a given entity id.
        """
        sql = f"""
            SELECT event_date,
                   SUM(positive_events) AS positive_events,
                   SUM(negative_events) AS negative_events
            FROM employee_events
            WHERE {self.name}_id = {id}
            GROUP BY event_date
            ORDER BY event_date
        """
        return self.pandas_query(sql)

    def notes(self, id: int):
        """
        Return a DataFrame with note_date and note
        for a given entity id.
        """
        # QUERY 2
        # Return note_date and note from notes table
        # Join using f-string formatted table and id column names
        sql = f"""
            SELECT note_date, note
            FROM notes
            JOIN {self.name}
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
        """
        return self.pandas_query(sql)