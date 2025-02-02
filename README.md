- slightly reworked nozza87's script from [this](https://vaultwarden.discourse.group/t/please-help-generating-master-password-hash-in-server-db-to-retrieve-wifes-lost-password/2724/10) thread
- this guide is written for run under unix-like os, guide for windows run can be found in original thread 

## Dependencies
```BASH
python -m venv <venv_name>
. ./<venv_name>/bin/activate
pip install -r requirements.txt
```

## Usage

### Test run
- Press Enter to continue when prompted (This can take a while with large numbers of guesses)
- Check you see `Match: d17780c96b5452d220164a321f240ee49b236d57b7a38744c7ddc47980265542`
- Check you have a file named `Match_d17780c96b5452d220164a321f240ee49b236d57b7a38744c7ddc47980265542.txt`

### Restore yopur password
- Obtain Vaultwarden database or database backup file. Actual database usually named `db.sqlite3` and stored in `/data/` directory in the docker container 

- Next you need to get your email, password hash and salt from "users" table in database. You can use any sqlite database viewer for it (I can recommend `sqlitebrowser`) and run next sql query:
	- Copy email to `EMAIL` variable in `main.py`
	- Copy 64 byte salt as hex value to `SALT` variable in `main.py` 
	* Copy 32 byte password hash as hex value to `HASH` variable in `main.py`
	- Copy number of rounds ("password_iterations") to `ROUNDS` variable in `main.py`
```SQL
select "users"."email", hex("users"."salt"), hex("users"."password_hash"), "users"."password_iterations" from "users"
```

- Change the variable `PASS_VARIANTS` in `main.py` to suit your password
	- You need to enter each known letter as an array of possibilities
	- Eg: "Te5t" = \[["T","t"], ["e","E","3"], ["S","s","5"], ["T","t"]\]
	- Use the "blDryRun" flag explained below to check guesses before running full hashes to prevent wasted time

- Run script with `python main.py`

- This script can take anywhere from seconds to days to fully run depending on the number of guesses required
- If you set the variable `blDryRun` in `main.py` to True it will print the calculated guesses instead of calculating hashes
- If you set the variable `blThreaded` in `main.py` to False it will run single threaded (much slower, only use this if your computer cannot multi thread)
