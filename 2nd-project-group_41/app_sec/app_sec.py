from flask import Flask, render_template, request, redirect, url_for, session, abort, flash
from dbwrappers import DatabaseWrappers
from werkzeug.security import check_password_hash
import os
import re
import json
from config import config
from auth.views import auth_bp
from auth.decorators import requires_auth
import requests
import secrets

UPLOAD_FOLDER = os.path.join('static', 'images', 'products')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

auth0_config = config['AUTH0']
domain = auth0_config["DOMAIN"]

app = Flask(__name__,
            static_url_path='',
            static_folder='static')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


app.config['MAX_CONTENT_LENGTH'] = 500 * 1000 * 1000

# Atributo "Secure" dos Tokens
app.config['SESSION_COOKIE_SECURE'] = True

# Atributo "SameSite" dos Tokens (Strict)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'


# app.secret_key = os.urandom(24)
app.secret_key = config["WEBAPP"]["SECRET_KEY"]
app.register_blueprint(auth_bp, url_prefix='/')

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
@requires_auth
def cart():
    
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
    t = []
    for val in cart.keys():
        arr_str += f"{val}, "

    #print(f"\n\n{arr_str[:-2]}")
    cart_items = db.get_product_by_id(arr_str[:-2])

    print(f"\n\n\n\a{cart_items}\n\n\n\n\n")
    
    for d in cart_items:
        k = d["id"]
        val = cart[str(k)]
        d["quantity"] = val

    # Calcula o subtotal do carrinho
    cart_subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    cart_total = cart_subtotal  # Se não houver impostos ou taxas adicionais

    # Renderize o modelo cart.html e passe a variável cart_items para ele
    return render_template("cart.html", cart_items=cart_items, cart_subtotal=cart_subtotal, cart_total=cart_total)
    

@app.route("/checkout", methods=["GET", "POST"])
@requires_auth
def checkout():
    cart_items = []

    try:
        cart = session["cart"]
    except KeyError:
        return render_template("checkout.html", cart_items=[], cart_total=0)
    db = DatabaseWrappers()

    if request.method == "POST":
        #username = request.form["username"]
        billing_country = request.form["c_country"]
        billing_fname = request.form["c_fname"]
        billing_lname = request.form["c_lname"]
        billing_companyname = request.form["c_companyname"]
        billing_address = request.form["c_address"]
        billing_state_country = request.form["c_state_country"]
        billing_postal_zip = request.form["c_postal_zip"]
        billing_email_address = request.form["c_email_address"]
        billing_phone = request.form["c_phone"]

        user_id = session.get("user").get("userinfo").get("sub")

        
        db.insert_update_user(user_id, billing_country, billing_fname, billing_lname, billing_companyname, billing_address,
                           billing_state_country, billing_postal_zip, billing_email_address, billing_phone)
        
    
    arr_str = ""
    for val in cart.keys():
        arr_str += f"{val}, "
    
    
    cart_items = db.get_product_by_id(arr_str[:-2])

    for d in cart_items:
        k = d["id"]
        val = cart[str(k)]
        d["quantity"] = val

    cart_subtotal = sum(item['price'] * item['quantity'] for item in cart_items)
    cart_total = cart_subtotal  # Se não houver impostos ou taxas adicionais

    return render_template("checkout.html", cart_items=cart_items, cart_total=cart_total)


@app.route("/forum", methods=["GET", "POST"])
def forum():
    db = DatabaseWrappers()

    if request.method == "POST":
        title = request.form["title"]
        message = request.form["message"]
        db.insert_forum_post(title, message)

    forum_posts = db.get_forum_posts()

    return render_template("forum.html", forum_posts=forum_posts)


@app.route("/product/<product_id>", methods=['GET', 'POST'])
def product(product_id):
    db = DatabaseWrappers()
    product = db.get_product_by_id(product_id)

    if request.method == 'POST':
        quantidade = int(request.form['quantidade'])
        if session.get("user"):            
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

                    print(f"\n\n\n\n{session['cart'] = }\n\n\n\n")

                    session.modified = True
                    
                    #print(f"{session['cart']= }")
                    return render_template("product.html", product=product[0], alert="success")
                else:
                    return render_template("product.html", product=product[0], alert="fail")
            else:
                abort(404)
        else:
            return redirect(url_for('auth.login'))  # Redireciona o usuário para a página de login

    if product:
        product = product[0]  # Acesse o primeiro item da lista (ou ajuste a estrutura dos dados conforme necessário)
        return render_template("product.html", product=product)
    else:
        abort(404)


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
        # return json.dumps( {'data': items} )
        return render_template("shop_items.html", items=items)
    else:
        # This is not an AJAX request
        return render_template("shop.html", items=items, categories=db.get_categories(), active_cat=category, name=name if name!="" else None)

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/user_profiles", methods=["GET", "POST"])
@requires_auth
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
        if file and allowed_file(file.filename): # TODO for org: not safe per the docs!!  allowed_file(file.filename) should be used. check: https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
            filename = name + '.' + file.filename.split(".")[1]
            db = DatabaseWrappers()
            new_filename = db.insert_product(name, description, price, stock, category, filename)                   
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            return redirect(url_for('user_profiles'))

        return redirect(url_for('user_profiles', fail=True))
    elif request.method == "GET":
        #if "user_id" not in session:
        #    return redirect(url_for("login"))


        print(domain)
        print(session.get("user").get("userinfo").get("sub"))
        url= f"https://{domain}/api/v2/users/{session.get('user').get('userinfo').get('sub')}/roles"

        api_config = config['API']
        payload = {}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_config["KEY"]}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        print(f"{response.text = }")
        admin_role_id= "rol_iEFUl2nsUNa4J76a"
        
        # only one role so no need to complicate!!!
        resp = response.json()
        if resp and resp[0]["id"] == admin_role_id:
            db = DatabaseWrappers()
            items = db.get_products()
            print(items)
            return render_template("user_profiles.html", items=items)
        else:
            return render_template("user_profiles.html")

@app.route("/changepass", methods=["GET", "POST"])
@requires_auth
def changepass():

    # url = "https://login.auth0.com/api/v2/tickets/password-change"

    # payload = json.dumps({
    #     "result_url": "string",
    #     "user_id": "string",
    #     "client_id": "string",
    #     "organization_id": "string",
    #     "connection_id": "string",
    #     "email": "user@example.com",
    #     "ttl_sec": 0,
    #     "mark_email_as_verified": False,
    #     "includeEmailInRedirect": True
    # })

    # headers = {
    #     'Content-Type': 'application/json',
    #     'Accept': 'application/json'
    # }

    # response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)


    if request.method == "POST":
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        confirm_new_password = request.form["confirm_new_password"]

        if new_password != confirm_new_password:
            return render_template("change_pass.html", error="As novas senhas não coincidem.")

        db = DatabaseWrappers()
        user_id = session.get("user").get("userinfo").get("sub")

        if user and check_password_hash(user["password"], old_password):
            print("Changing password")
            print(f"{user['username'] = } {new_password = }")
            db.update_user_password(user["username"], new_password)
            return redirect(url_for("logout"))
        elif check_password_hash(old_password, new_password):
            return render_template("change_pass.html", error="A nova palavra-passe deve ser diferente da antiga.")
        else:
            return render_template("change_pass.html", error="Palavra-passe antiga incorreta.")

    return render_template("change_pass.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404
