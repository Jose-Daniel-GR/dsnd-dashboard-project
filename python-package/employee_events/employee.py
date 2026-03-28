# Import the QueryBase class
from employee_events.query_base import QueryBase

# Import the query decorator for sql execution
from employee_events.sql_execution import query


# Define Employee as a subclass of QueryBase
class Employee(QueryBase):
    """Handles SQL queries specific to individual employees."""

    # Set table name to employee
    name = "employee"

    def names(self) -> list:
        """
        Return a list of tuples with full name
        and id for all employees.
        """
        # Query 3
        # Select full name and employee id
        # for all employees in the database
        sql = """
            SELECT first_name || ' ' || last_name AS full_name,
                   employee_id
            FROM employee
            ORDER BY full_name
        """
        return self.query(sql)

    def username(self, id: int) -> list:
        """
        Return a list of tuples with the full name
        of the employee matching the given id.
        """
        # Query 4
        # Select full name filtered by employee id
        sql = f"""
            SELECT first_name || ' ' || last_name AS full_name
            FROM employee
            WHERE employee_id = {id}
        """
        return self.query(sql)

    def model_data(self, id: int):
        """
        Return a DataFrame with aggregated positive
        and negative events for the ML model.
        """
        # Execute the SQL query and return a pandas DataFrame
        return self.pandas_query(f"""
            SELECT SUM(positive_events) positive_events
                 , SUM(negative_events) negative_events
            FROM {self.name}
            JOIN employee_events
                USING({self.name}_id)
            WHERE {self.name}.{self.name}_id = {id}
        """)