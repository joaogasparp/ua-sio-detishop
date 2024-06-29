from flask import Flask, make_response, render_template, request, redirect, url_for, session, jsonify, abort, flash
from dbwrappers import DatabaseWrappers
import os
import re
import json

UPLOAD_FOLDER = os.path.join('static', 'images', 'products')

app = Flask(__name__,
            static_url_path='',
            static_folder='static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = os.urandom(24)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    query  = request.args.get("query")
    return redirect(url_for('shop', name=query))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/cart", methods=["GET", "POST"])
def cart():
    

    if "user_id" in session:
        db = DatabaseWrappers()
        cart_items = []  # Inicialize uma lista vazia para os produtos no carrinho

        try:
            cart = session["cart"]
        except KeyError:
            return render_template("cart.html", cart_items=[], cart_subtotal=0, cart_total=0)

        if request.method == "POST":
            print(f"\n\n\n\n\n{request.form['id'] = }\n\n\n\n\n")
            product_id = request.form['id']
            print(f"{product_id = } {cart = }")
            cart.pop(str(product_id))
            session.modified = True
            print(f"\n\n\n\n{product_id = } {cart = }")
            return redirect(url_for('cart'))
    

        # Suponha que você tenha uma função `get_cart_items` que busca os produtos no carrinho do usuário
        #cart_items = db.get_products_in_cart(user_id)
        arr_str = ""
        for val in cart.keys():
            arr_str += f"{val}, "
        cart_items = db.get_product_by_id(arr_str[:-2])

        for d in cart_items:
            k = d["id"]
            val = cart[str(k)]
            d["quantity"] = val

        # Calcula o subtotal do carrinho
        cart_subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
        cart_total = cart_subtotal  # Se não houver impostos ou taxas adicionais

        # Renderize o modelo cart.html e passe a variável cart_items para ele
        return render_template("cart.html", cart_items=cart_items, cart_subtotal=cart_subtotal, cart_total=cart_total)
    else:
        return redirect(url_for('login'))  # Redirecione o usuário para a página de login se não estiver logado

@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    db = DatabaseWrappers()
    if 'username' in request.form and 'product_id' in request.form:
        username = request.form['username']
        product_id = request.form['product_id']
        # Chame a função para remover o produto do carrinho no banco de dados usando o 'username' e 'product_id'
        db.remove_from_cart(username, product_id)
        return 'Produto removido com sucesso'  # Você pode retornar uma mensagem de sucesso
    return 'Erro na remoção do produto'  # Você pode retornar uma mensagem de erro se os parâmetros estiverem ausentes
    

@app.route("/checkout")
def checkout():
    if "user_id" in session:
        user_id = session["user_id"]
        db = DatabaseWrappers()
        cart_items = db.get_products_in_cart(user_id)

        cart_subtotal = sum(item['price'] * item['quantidade'] for item in cart_items)
        cart_total = cart_subtotal  # Se não houver impostos ou taxas adicionais

        return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total)
    else:
        return redirect(url_for('login'))  # Redirecione o usuário para a página de login se não estiver logado



@app.route("/forum", methods=["GET", "POST"])
def forum():
    db = DatabaseWrappers()

    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        db.insert_forum_post(title, message)

    forum_posts = db.get_forum_posts()

    #return forum_posts
    return render_template("forum.html", forum_posts=forum_posts)

@app.route("/get_posts", methods=["GET", "POST"])
def get_posts():
    db = DatabaseWrappers()
    forum_posts = db.get_forum_posts()

    return forum_posts

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = DatabaseWrappers()
        user = db.get_user_by_username_and_password(username, password)

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("home"))
        else:
            print("Login falhou")
            return redirect(url_for('login_page', error='login_failed'))

        # if user and user['password'] == password:
        #     session["user_id"] = user["id"]
        #     return redirect(url_for("home"))
        # else:
        #     # print("Login falhou")
        #     return redirect(url_for('login_page', error='login_failed'))

    return render_template("login.html")

@app.route('/login_page')
def login_page():
    success = request.args.get('success')
    error = request.args.get('error')
    return render_template('login.html', success=success, error=error)

@app.route("/product/<product_id>", methods=['GET', 'POST'])
def product(product_id):
    db = DatabaseWrappers()
    product = db.get_product_by_id(product_id)

    if request.method == 'POST':
        quantidade = int(request.form['quantidade'])
        if "user_id" in session:            
            if product:
                try:
                    already_in_cart = session["cart"][product_id]
                except KeyError:
                    print("key error")
                    already_in_cart = 0

                if quantidade + already_in_cart <= product[0]["stock"]:
                    try:
                        session["cart"][product_id] += quantidade
                        print(f"incrementing pid! = {session['cart'][product_id]}")
                    except KeyError as e:
                        if e.args[0] == "cart":
                            session["cart"] = {}

                        session["cart"][product_id] = quantidade

                    session.modified = True
                    
                    #print(f"{session['cart']= }")
                    return render_template("product.html", product=product[0], alert="success")
                else:
                    return render_template("product.html", product=product[0], alert="fail")
            else:
                abort(404)
        else:
            return redirect(url_for('login'))  # Redireciona o usuário para a página de login

    if product:
        product = product[0]  # Acesse o primeiro item da lista (ou ajuste a estrutura dos dados conforme necessário)
        return render_template("product.html", product=product)
    else:
        abort(404)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("register.html", error="As senhas não coincidem.")

        db = DatabaseWrappers()
        
        email_already_taken = db.is_email_taken(email)
        username_already_taken = db.is_username_taken(username)

        if email_already_taken:
            print("Email already taken")
            return redirect(url_for('register_page', error='email_taken'))

        if username_already_taken:
            print("Username already taken")
            return redirect(url_for('register_page', error='username_taken'))
        
        db.insert_user(username, email, password)
        return redirect(url_for('login_page', success='registration_successful'))

    return render_template("register.html")

@app.route('/register_page')
def register_page():
    error_type = request.args.get('error_type')
    
    if error_type == 'email_taken':
        error_message = 'E-mail já com registo na página. Faça login!'
    elif error_type == 'username_taken':
        error_message = 'Username já utilizado.'
    else:
        error_message = 'Erro desconhecido.'
    
    print("Error Message:", error_message)  # Adiciona esta linha para depuração
    return render_template('register.html', error=error_message)

def is_it_true(value):
  return value.lower() == 'true'

@app.route("/shop")
def shop():

    name = request.args.get("name", default="")
    #$75 - $229
    range = request.args.get("range", default="0 - 500")
    range = re.findall('\d+', range)
    
    show_available = request.args.get("show_available", default=True, type=is_it_true)
    show_out_of_stock = request.args.get("show_out_of_stock", default=True, type=is_it_true)

    category = request.args.get("category", default="%")
        
    db = DatabaseWrappers()
    items = db.get_products(name,
                            int(range[0]),
                            int(range[1]),
                            show_available,
                            show_out_of_stock,
                            category )
    
    print(items)
    #items.append({'id': 1, 'name': 'Manga cava', 'description': '<script> alert("yo");</script>', 'price': 10, 'stock': 40, 'category': 'roupa', 'product_image': 'cloth_1.jpg'})
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # This is an AJAX request 
        return json.dumps( {'data': items} )
    else:
        # This is not an AJAX request
        return render_template("shop.html", items=items, categories=db.get_categories(), active_cat=category, name=name if name!="" else None)

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))

def user_email_exist(username, email):
    db = DatabaseWrappers()
    user_data = db.get_user_by_username_email(username, email)
    return user_data is not None

@app.route("/reset_pass", methods=["GET"])
def show_reset_pass():
    return render_template("reset_pass.html")

@app.route("/reset_pass", methods=["POST"])
def reset_pass():
    username = request.form.get("username")
    email = request.form.get("email")

    if user_email_exist(username, email):
        new_password = request.form.get("new_password")
        db = DatabaseWrappers()
        db.update_user_password(username, new_password)
        return redirect(url_for("login"))
    
def is_admin(user_id):
    db = DatabaseWrappers()
    user = db.get_user_by_id(user_id)
    return user and user.get("is_admin") == 1

@app.route("/user_profiles", methods=["GET", "POST"])
def user_profiles():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        stock = request.form["stock"]
        category = request.form["category"]
        
        file = request.files['image']
        print(name, description, price, stock, category)

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file: # TODO for app_sec: not safe per the docs!!  allowed_file(file.filename) should be used. check: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
            filename = name + '.' + file.filename.split(".")[1]
            db = DatabaseWrappers()
            new_filename = db.insert_product(name, description, price, stock, category, filename)                   
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            return redirect(url_for('user_profiles'))

        return "success"
    elif request.method == "GET":
        if "user_id" not in session:
            return redirect(url_for("login"))

        db = DatabaseWrappers()
        user_id = session["user_id"]
        user = db.get_user_by_id(user_id)
        
        if user_id == 1:
            all_profiles = db.get_all_profiles()
            print(f"{all_profiles = }")
            items = db.get_products()
            return render_template("user_profiles.html", user_id=user_id, all_profiles=all_profiles, items=items)
        else:
            print(user)
            return render_template("user_profiles.html", user=user)

@app.route("/changepass", methods=["GET", "POST"])
def changepass():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        #old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_new_password = request.form["confirm_new_password"]

        if new_password != confirm_new_password:
            return render_template("change_pass.html", error="As novas senhas não coincidem.")

        db = DatabaseWrappers()
        user_id = session["user_id"]
        user = db.get_user_by_id(user_id)

        
        db.update_user_password(user["username"], new_password)
        return redirect(url_for("logout"))
        

    return render_template("change_pass.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404
