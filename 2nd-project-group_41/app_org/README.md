## How to run
1. Create a virtual enviorment:
```bash
python3 -m venv venv
```

2. Activate the virtual enviorment (you will need to repeast this step every time you open a new terminal):
```bash
.\venv\Scripts\activate
```

3. Install the requeriments:
```bash
pip install -r requirements.txt
```

4. Reset the data base:
```bash
python3 dbmanagement.py -r
```

5. Run the server:<br>
```bash
flask --app app_org run --debug
```

6. Access the website:
```bash
http://127.0.0.1:5000/
```

## Authors

- [Guilherme Santos](https://github.com/sonic28g), 107961
- [João Gaspar](https://github.com/joaogasparp), 107708
- [Miguel Ferreira](https://github.com/mgLTF), 93419
- [Pedro Coutinho](https://github.com/pmacoutinho), 93278