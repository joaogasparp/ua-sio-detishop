import sqlite3
#from pysqlcipher3 import dbapi2 as sqlite3
import argparse
import os
from dbwrappers import DatabaseWrappers

DATABASE_NAME = "database.db"

if __name__ == "__main__": 
    parser = argparse.ArgumentParser()
    parser.add_argument( "-r", "--reset", action="store_true", help="resets the whole database")
    args = parser.parse_args()

    if args.reset:
        os.remove(DATABASE_NAME)

    db = DatabaseWrappers(DATABASE_NAME)

    db.create_table("users", """id text UNIQUE, c_country text, c_fname text, c_lname text,
                    c_companyname text, c_address text, c_state_country text, c_postal_zip text, c_email_address text, c_phone text""")
    
    
    db.create_table("forum_posts", "id INTEGER PRIMARY KEY, title TEXT, message TEXT")

    # exemplo como chamar função!! se a tabela já existir não há stress
    db.create_table("products", "id integer primary key, name text, description text, price integer, stock integer, category text, product_image text")

    # inserting dummy products
    db.insert_product("Manga cava", "Camisola manga cava", 10, 40, "roupa", "cloth_1.jpg", True)
    db.insert_product("Polo", "Polo creme", 20, 50, "roupa", "cloth_2.jpg", True)
    db.insert_product("Camisa", "Camisa azul", 35, 0, "roupa", "cloth_3.jpg", True)
    db.insert_product("Sapatilhas", "Sapatilhas azuis", 50, 4, "calçado", "shoe_1.jpg", True)

    # insert billing details
    db.create_table("billing", "id INTEGER PRIMARY KEY, username TEXT, country TEXT, fname TEXT, lname TEXT, companyname TEXT, address TEXT, state_country TEXT, postal_zip TEXT, email_address TEXT, phone TEXT")

    # cart
    db.create_table("cart", "id INTEGER PRIMARY KEY, username TEXT, product TEXT, quantidade INTEGER, price INTEGER, product_image TEXT")
