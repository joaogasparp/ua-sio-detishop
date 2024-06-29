import sqlite3
from cryptography.fernet import Fernet
from werkzeug.security import check_password_hash, generate_password_hash

## NOTE: fazer aqui as funções de acesso a database (selects, inserts e assim)

class DatabaseWrappers:
    """Wrappers for accessing database."""

    def __init__(self, database_path="database.db"):
        self.conn = sqlite3.connect(database_path)
        self.cursor = self.conn.cursor()
        key = Fernet.generate_key()
        self.cipher_suite = Fernet(key)


    def print_tables(self, print_rows=False):
        """Prints all tables and respective column names in database."""

        # fetch all table names
        tables = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

        for table in tables:
            # gets columns for each table
            self.cursor.execute(f'select * from {table[0]}')
            names = list(map(lambda x: x[0], self.cursor.description))

            print(f"{table[0]} -> {names}")
            if print_rows:
                rows = self.cursor.fetchall()
                for row in rows:
                    print(row)

    # con - pass the sqlite connect object
    # table_name - just the table name
    # columns - column names and type in sql style
    def create_table(self, table_name, columns):
        """Creates table in database."""
        try:
            self.conn.execute(f"CREATE TABLE {table_name} ({columns})")
        except sqlite3.OperationalError:
            print(f"Table \"{table_name}\" already exists.")

        self.conn.commit()

    def fetch_json(self):
        """Converts query response to json type structure."""
        colname = [ d[0] for d in self.cursor.description ]
        result_list = [ dict(zip(colname, r)) for r in self.cursor.fetchall() ]

        return result_list

    # Insertions
    def insert_update_user(self, user_id, billing_country, billing_fname, billing_lname, billing_companyname, billing_address,
                           billing_state_country, billing_postal_zip, billing_email_address, billing_phone):
        billing_country = self.cipher_suite.encrypt(billing_country.encode())
        billing_fname = self.cipher_suite.encrypt(billing_fname.encode())
        billing_lname = self.cipher_suite.encrypt(billing_lname.encode())
        billing_companyname = self.cipher_suite.encrypt(billing_companyname.encode())
        billing_address = self.cipher_suite.encrypt(billing_address.encode())
        billing_state_country = self.cipher_suite.encrypt(billing_state_country.encode())
        billing_postal_zip = self.cipher_suite.encrypt(billing_postal_zip.encode())
        billing_email_address = self.cipher_suite.encrypt(billing_email_address.encode())
        billing_phone = self.cipher_suite.encrypt(billing_phone.encode())
        self.cursor.execute(
            """INSERT INTO
            users (id, c_country, c_fname, c_lname, c_companyname, c_address, c_state_country, c_postal_zip, c_email_address, c_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT do UPDATE SET
            c_country=?, c_fname=?, c_lname=?, c_companyname=?, c_address=?, c_state_country=?, c_postal_zip=?, c_email_address=?, c_phone=?
            """, (user_id, billing_country, billing_fname, billing_lname, billing_companyname, billing_address,
                           billing_state_country, billing_postal_zip, billing_email_address, billing_phone,
                           billing_country, billing_fname, billing_lname, billing_companyname, billing_address,
                           billing_state_country, billing_postal_zip, billing_email_address, billing_phone)) #MANEIRA HORRIVEL DE FAZER
        
        self.conn.commit()

    def insert_product(self, name, description, price, stock, category, product_image, from_manager=False):
        self.cursor.execute(f"""INSERT INTO products(name, description, price, stock, category, product_image) 
                            VALUES(\"{name}\", \"{description}\", {price}, {stock}, \"{category.lower()}\", \"{product_image}\")""")
        

        # append id to product image
        last_row_id = self.cursor.lastrowid
        product_image_with_id = f"{last_row_id}_{product_image}"
        if not from_manager:
            self.cursor.execute("UPDATE products SET product_image = ? WHERE id = ?", (product_image_with_id, last_row_id))
            self.conn.commit()

        return product_image_with_id

    # Selects
    def get_products(self, name="", min_price=None, max_price=None, show_available=True, show_out_of_stock=True, category="%"):
        # query = (
        #     f'SELECT id, name, description, price, stock, category, product_image FROM products\n' 
        #     f'WHERE name LIKE \"%{name}%\"\n'
        #     f'AND   category LIKE \"{category.lower()}\"\n'
        # )
        
        # op = ">" if show_available and not show_out_of_stock else "==" if not show_available and show_out_of_stock else ">="
        # query += f"AND stock {op} 0\n"

        # if min_price != None and max_price != None:
        #     if min_price <= max_price:
        #         query += f"AND price BETWEEN {min_price} and {max_price}\n"
        # elif min_price != None:
        #     query += f"AND price >= {min_price}\n"
        # elif max_price != None:
        #     query += f"AND price <= {max_price}\n"

        query = (
            'SELECT id, name, description, price, stock, category, product_image FROM products\n' 
            'WHERE name LIKE ?\n'
            'AND category LIKE ?\n'
        )

        op = ">" if show_available and not show_out_of_stock else "==" if not show_available and show_out_of_stock else ">="
        query += 'AND stock ' + op + ' 0\n'

        parameters = [f'%{name}%', category.lower()]

        if min_price is not None and max_price is not None:
            if min_price <= max_price:
                query += 'AND price BETWEEN ? and ?\n'
                parameters.extend([min_price, max_price])
        elif min_price is not None:
            query += 'AND price >= ?\n'
            parameters.append(min_price)
        elif max_price is not None:
            query += 'AND price <= ?\n'
            parameters.append(max_price)

        # print(query)
        self.cursor.execute(query, parameters)
        return self.fetch_json()
    
    def get_product_by_id(self, id):
        print(f"\n\n{id = }\n\n") 
        q = f'SELECT id, name, description, price, stock, category, product_image FROM products WHERE id IN ({id})'
        self.cursor.execute(q)
      
        return self.fetch_json()
    
    def get_column(self, column_name, table_name):
        """Gets column from given table."""
        self.cursor.execute(f"SELECT DISTINCT ? FROM ?;", (column_name, table_name, ))
        return self.cursor.fetchall()

    def get_categories(self):
        
        self.cursor.execute(
            "SELECT category, SUM(stock)\n" 
            "FROM products\n"
            "GROUP BY category\n"
            "ORDER BY SUM(stock) DESC"
        )

        return [(i[0].capitalize(), i[1]) for i in self.cursor.fetchall()]
        
    def get_all_users(self):
        query = "SELECT * FROM users"
        self.cursor.execute(query)
        users = self.cursor.fetchall()

        user_list = []
        for user in users:
            user_data = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'password': user[3]
            }
            user_list.append(user_data)

        return user_list
    
    def update_user_password(self, username, new_password):
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        print("hashed pass = ", hashed_password)
        query = (
            f'UPDATE users\n'
            f'SET password = ?\n'
            f'WHERE username = ?'
        )
        self.cursor.execute(query, (hashed_password, username))
        self.conn.commit()
        
    def get_user_by_id(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_data = self.cursor.fetchone()

        if user_data:
            user_dict = {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'password': user_data[3]
            }
            return user_dict
        else:
            return None
    
    def get_user_email_by_id(self, user_id):
        self.cursor.execute("SELECT username, email FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result if result else (None, None)
    
    def get_all_profiles(self):
        query = "SELECT * FROM users"
        self.cursor.execute(query)
        all_profiles = self.fetch_json()

        return all_profiles
    
    def insert_forum_post(self, title, message):
        self.cursor.execute("INSERT INTO forum_posts(title, message) VALUES(?, ?)", (title, message, ))
        self.conn.commit()

    def get_forum_posts(self):
        self.cursor.execute("SELECT * FROM forum_posts ORDER BY id DESC")
        return self.fetch_json()
    
    def get_user_by_username(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

        user_data = self.cursor.fetchone()

        if user_data:
            user_dict = {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'password': user_data[3]
            }
            return user_dict
        else:
            return None
    

    # Cart
    def insert_product_cart(self):
        self.cursor.execute("""CREATE TABLE if not exists CART(id INTERGER PRIMARY KEY AUTOINCREMENT, username TEXT, product TEXT, quatidade INTEGERM price INTEGER)""")
        self.conn.commit()


    def add_to_cart(self, username, product, quantidade, product_image):
        # Consulta para verificar se o produto já existe no carrinho de compras do usuário
        check_query = "SELECT COUNT(*) FROM cart WHERE username = ? AND product = ?"
        self.cursor.execute(check_query, (username, product))
        existing_count = self.cursor.fetchone()[0]

        if existing_count > 0:
            # Se o produto já estiver no carrinho, atualize a quantidade
            update_query = "UPDATE cart SET quantidade = quantidade + ? WHERE username = ? AND product = ?"
            self.cursor.execute(update_query, (quantidade, username, product))
        else:
            # Consulta para buscar o preço do produto e a imagem na tabela de produtos
            price_image_query = "SELECT price, product_image FROM products WHERE name = ?"
            self.cursor.execute(price_image_query, (product,))
            result = self.cursor.fetchone()

            if result:
                price, image = result
                # Inserir um novo registro no carrinho com o preço e a imagem do produto
                insert_query = "INSERT INTO cart (username, product, quantidade, price, product_image) VALUES (?, ?, ?, ?, ?)"
                self.cursor.execute(insert_query, (username, product, quantidade, price, image))

        # Certifique-se de confirmar as mudanças no banco de dados
        self.conn.commit()

    def get_products_in_cart(self, username):
        query = "SELECT id, username, product, quantidade, price, product_image FROM cart WHERE username = ?"
        self.cursor.execute(query, (username,))
        cart_items = self.cursor.fetchall()

        cart_products = []

        for item in cart_items:
            product_details = {
                'id': item[0],
                'username': item[1],
                'product': item[2],
                'quantidade': item[3],
                'price': item[4],
                'product_image': item[5]
            }
            cart_products.append(product_details)

        return cart_products


    def remove_from_cart(self, username, product_id):
        try:
            # Execute uma consulta para remover o produto do carrinho
            delete_query = "DELETE FROM cart WHERE username = ? AND id = ?"
            self.cursor.execute(delete_query, (username, product_id))
            self.conn.commit()
            print("REMOVED PRODUCT_ID\n")
            return True  # Indica que a remoção foi bem-sucedida
        except Exception as e:
            print("Erro ao remover produto do carrinho:", str(e))
            self.conn.rollback()
            return False  # Indica que houve um erro durante a remoção

    def remove_product(self, id):
        self.cursor.execute(f"DELETE FROM products WHERE id = {id}")
        self.conn.commit()

    def insert_billing(self, username, country, fname, lname, companyname, address, state_country, postal_zip, email_address, phone):
        cipher_country = self.cipher_suite.encrypt(country.encode())
        cipher_fname = self.cipher_suite.encrypt(fname.encode())
        cipher_lname = self.cipher_suite.encrypt(lname.encode())
        cipher_companyname = self.cipher_suite.encrypt(companyname.encode())
        cipher_address = self.cipher_suite.encrypt(address.encode())
        cipher_state_country = self.cipher_suite.encrypt(state_country.encode())
        cipher_postal_zip = self.cipher_suite.encrypt(postal_zip.encode())
        cipher_email_address = self.cipher_suite.encrypt(email_address.encode())
        cipher_phone = self.cipher_suite.encrypt(phone.encode())
        self.cursor.execute(f"""INSERT INTO billing(username, country, fname, lname, companyname, address, state_country, postal_zip, email_address, phone)
                            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (username, cipher_country, cipher_fname, cipher_lname, cipher_companyname, cipher_address, cipher_state_country, cipher_postal_zip, cipher_email_address, cipher_phone))
        self.conn.commit()

    '''
    def get_billing_by_username(self, username):
        query = ('SELECT * FROM users WHERE username = ?')
        self.cursor.execute(query, (username))
        billing_details = self.cursor.fetchall()
        for detail in billing_details:
            billing = {
                'id': detail[0],
                'username': detail[1],
                'country': self.cipher_suite.decrypt(detail[2]).decode(),
                'fname': self.cipher_suite.decrypt(detail[3]).decode(),
                'lname': self.cipher_suite.decrypt(detail[4]).decode(),
                'companyname': self.cipher_suite.decrypt(detail[5]).decode(),
                'address': self.cipher_suite.decrypt(detail[6]).decode(),
                'state_country': self.cipher_suite.decrypt(detail[7]).decode(),
                'postal_zip': self.cipher_suite.decrypt(detail[8]).decode(),
                'email_address': self.cipher_suite.decrypt(detail[9]).decode(),
                'phone': self.cipher_suite.decrypt(detail[10]).decode(),
            }

        return billing
    '''

if __name__ == "__main__":
    db = DatabaseWrappers("database.db")
    #db.insert_product("lol", "xd", 5, 0, 3, 4)
    #db.remove_product(5)
    db.print_tables(print_rows=True)
    #print(db.get_products(min_price='49', max_price='320'))
