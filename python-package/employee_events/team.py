# Import the QueryBase class
from employee_events.query_base import QueryBase

# Import the query decorator for sql execution
from employee_events.sql_execution import query


# Create Team as a subclass of QueryBase
class Team(QueryBase):
    """Handles SQL queries specific to teams."""

    # Set table name to team
    name = "team"

    def names(self) -> list:
        """
        Return a list of tuples with team name
        and id for all teams in the database.
        """
        # Query 5
        # Select team_name and team_id
        # for all teams in the database
        sql = """
            SELECT team_name, team_id
            FROM team
            ORDER BY team_name
        """
        return self.query(sql)

    def username(self, id: int) -> list:
        """
        Return a list of tuples with the team name
        matching the given id.
        """
        # Query 6
        # Select team_name filtered by team_id
        sql = f"""
            SELECT team_name
            FROM team
            WHERE team_id = {id}
        """
        return self.query(sql)

    def model_data(self, id: int):
        """
        Return a DataFrame with positive and negative
        events per employee for the ML model.
        """
        # Execute the SQL query and return a pandas DataFrame
        return self.pandas_query(f"""
            SELECT positive_events, negative_events FROM (
                SELECT employee_id
                     , SUM(positive_events) positive_events
                     , SUM(negative_events) negative_events
                FROM {self.name}
                JOIN employee_events
                    USING({self.name}_id)
                WHERE {self.name}.{self.name}_id = {id}
                GROUP BY employee_id
            )
        """)