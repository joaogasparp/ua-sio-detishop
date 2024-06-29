## Description
Our project portrays an online store selling souvenir items from DETI at the University of Aveiro, including products such as t-shirts, hoodies, and sneakers. Within the project, users can be created, their password can be reset if forgotten, and they can log in with the option to keep the session active. This means that as long as the server is running, logging in once allows the website to recognize the user accessing it. Subsequently, if needed, there is also the option to log out. Users can make purchases by adding various products to the cart, and if they change their mind, they can remove them later and proceed to checkout. The website includes a page for creating posts with a title and content, described by the user. There is another page where users have the option to change their current password, with the introduction of the old password being mandatory for the process to be completed correctly. The site also features a pre-defined admin account with the username: "admin" and password: "admin". This admin account can add new products and access user information, including usernames, emails, and passwords. It's important to note that users who are not logged in cannot access critical pages or make purchases. <br>
The project has two main folders: "app", which relates to the insecure application (contains various types of vulnerabilities), and "app_sec", which represents the secure application (without weaknesses).

## Vulnerabilites used
[CWE-79](https://cwe.mitre.org/data/definitions/79.html)

[CWE-89](https://cwe.mitre.org/data/definitions/89.html)

[CWE-521](https://cwe.mitre.org/data/definitions/521.html)

[CWE-256](https://cwe.mitre.org/data/definitions/256.html)

[CWE-620](https://cwe.mitre.org/data/definitions/620.html)

[CWE-434](https://cwe.mitre.org/data/definitions/434.html)


## How to run
1. Go to the respective folder:
```bash
cd app
```
or
```bash
cd app_sec
```

2. Create a virtual enviorment:
```bash
python3 -m venv venv
```

2. Activate the virtual enviorment (you will need to repeast this step every time you open a new terminal):
```bash
source venv/bin/activate
```

3. Install the requeriments:
```bash
pip install -r requirements.txt
```

4. Run the server:<br>
4.1 In the app folder:
```bash
flask --app app run --debug
```
4.2 In the app_sec folder:
```bash
flask --app app_sec run --debug
```

5. Access the website:

http://127.0.0.1:5000/


## Authors
[Guilherme Santos](https://github.com/sonic28g), 107961<br>
[João Gaspar](https://github.com/joaogasparp), 107708<br>
[Pedro Coutinho](https://github.com/pmacoutinho), 93278<br>
[Miguel Ferreira](https://github.com/mgLTF), 93419
