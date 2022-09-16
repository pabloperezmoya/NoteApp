
from db import _db_auth
from boto3.dynamodb.conditions import Key, Attr



class Db_Connection:
    def __init__(self):
        self.db = _db_auth.get_db()
        return self.db

    def get_db(self):
        return self.db

    def __call__(self):
        return self.get_db()

    def __getitem__(self, item):
        return self.get_db().Table(item)

class Tables(Db_Connection):
    def __init__(self, table_name):
        self.db = super().__init__()

        if self.exists_table(table_name):
            self.table = self.db.Table(table_name)
        else:
            raise Exception(f"Table '{table_name}' does not exist")

    def exists_table(self, table_name):
        # for table in self.db.tables.all():
        #     if table.name == table_name:
        #         return True
        # return False
        return table_name in [ table.name for table in self.db.tables.all()]

    def required_attributes(self):
        return self.table.key_schema

    def _check_required_attributes(self, data):
        try:
            for requirement in self.required_attributes():
                if requirement['AttributeName'] not in data:
                    return False, f"Missing required attribute '{requirement['AttributeName']}'"
            return True, 0
        except Exception as e:

            return False, e

    def query_item(self, key_condition_expression, expression_attribute_values):
        # Notes().query_item('email = :v1', {":v1": "ppmoya08@gmail.com"})
        """query_item(key_condition_expression, expression_attribute_values) -> Boolean
        
        Query an item in the table. Returns True if successful, False otherwise."""
        try:
            response = self.table.query(
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return True, response['Items']
        except Exception as e:
            print(e)
            return False, e

    def get_item(self, key):
        """get_item(key) -> Boolean
        
        Get an item from the table. Returns True if successful, False otherwise."""
        check = self._check_required_attributes(key)
        if check[0] is True:
            try:
                return True, self.table.get_item(Key=key)['Item']
            except Exception as e:
                return False, f'No item found'
        else:
            print(check[1])
            return check
            
    def put_item(self, data):
        """put_item(data) -> Boolean
        
        Put an item into the table. Returns True if successful, False otherwise."""
        check = self._check_required_attributes(data)
        if check[0] == True:
            try:
                self.table.put_item(Item=data)
                return True, 0
            except Exception as e:
                print(e)
                return False, e
        else:
            print(check[1])
            return check

    def update_item(self, key, update_expression, expression_attribute_values, optimistic_locking=False):
        """update_item(data) -> Boolean
        
        update_expression: str -> 'set #n = :n'
        expression_attribute_values: dict -> {':n': 'new value'}
        
        Update an item in the table. Returns True if successful, False otherwise."""
        if optimistic_locking:
            check = self._check_required_attributes(key)
            if check[0] is True:
                try:
                    item = self.table.get_item(Key=key)['Item']
                    current_version = item['version']
                    item['version'] += 1

                    self.table.update_item(
                        Key=key, 
                        UpdateExpression=update_expression, 
                        ExpressionAttributeValues=expression_attribute_values,
                        ConditionExpression=Attr("version").eq(current_version)
                        )
                except Exception as e:
                    print(e)
                    return False, e
            else:
                print(check[1])
                return check

        else:
            check = self._check_required_attributes(key)
            if check[0] is True:
                try:
                    self.table.update_item(Key=key, UpdateExpression=update_expression, ExpressionAttributeValues=expression_attribute_values)
                    return True, 0
                except Exception as e:
                    return False, e
            else:
                print(check[1])
                return check

    def delete_item(self, key):
        """delete_item(key) -> Boolean
        
        Delete an item from the table. Returns True if successful, False otherwise."""
        check = self._check_required_attributes(key)
        if check[0] is True:
            try:
                self.table.delete_item(Key=key)
                return True, 0
            except Exception as e:
                print(e)
                return False, e
        else:
            print(check[1])
            return check
