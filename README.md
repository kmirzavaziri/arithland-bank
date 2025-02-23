# Arithland Bank

## Windows

### Install Dependencies

1. Download the latest version of Python from the
    [official Python website](https://www.python.org/downloads/).

2. Run the Installer.
    (**Important**: Check the box **"Add Python to PATH"** before clicking "Install Now.")

3. Open **Command Prompt** (search for `cmd` in the Start menu).

4. `cd` somewhere convinient.
    ```bash
    cd some\directory
    ```

5. Clone this repository. (If git is not installed, install it, and close and
    reopen the `cmd`.)
    ```bash
    git clone git@github.com:kmirzavaziri/arithland-bank.git
    cd arithland-bank
    ```

6. Create a virtual environment.
    ```bash
    python -m venv venv
    ```

7. Activate the Virtual Environment. (After activation, your Command Prompt will show `(venv)` at the beginning of the line, indicating that the virtual environment is active.)
    ```bash
    venv\Scripts\activate
    ```

8. Install requirements.
    ```bash
    pip install -r requirements.txt
    ```

### Start the Service

1. Open **Command Prompt** (search for `cmd` in the Start menu).

2. `cd` to the project directory.
    ```bash
    cd some\directory\arithland-bank
    ```

3. Activate the venv.
    ```bash
    venv\Scripts\activate
    ```
4. **(Optionally)** clear existing data, by deleting the file `db.sqlite3`.

5. Migrate the database. (If it's the first time, or you deleted the data)
    ```bash
    python manage.py migrate
    ```

6. Create an admin. (If it's the first time, or you deleted the data)
    ```bash
    python manage.py createsuperuser
    ```

7. Run the server.
    ```bash
    python manage.py runserver 0.0.0.0:8000
    ```

8. Open the application [0.0.0.0:8000](http://0.0.0.0:8000) and login with admin credentials.

9. Find your machine's local IP, and share with other machines in the same network,
    they can access it using the address `THE_IP:8000`. (You might need to disable the
    firewall on the server machine.)

## Steps to deploy

```
make init-ansible
make ansible-instance
```

And then trigger deploy pipeline.

## Known Issues

### To Do List

- team card background
- add revert transaction functionality
