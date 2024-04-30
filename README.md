# KIWI Merino

### Lincoln University COMP693 Group B

## Project preparations:

1. Setup a virtual environment with python3.10 in VSCode
2. Install pip packages

```bash
$ pip install -r requirements.txt
```

3. Add `connect.py` under `app` folder with the following content:

```python
dbhost = 'localhost'    # Your database host
dbuser = 'root'         # Your database username
dbpass = ''             # Your database password, leave it empty if you don't have one
dbname = 'kiwimerino'   # Your database name
```

4. Import the initial database schema from `sql/kiwimerino_pre_migration.sql` to your database

5. Running db migration command to keep the schema up to date

```bash
$ flask db upgrade
```

6. Start the project (in debug mode)

```bash
$ flask run --debug
```

## Testing Accounts

- **Manger Account**
  - email: john.smith@email.com
  - Password: `pp_merino_123!`
- **Tutor Account**
  - email: jane.doe@email.com
  - Password: `pp_merino_123!`
- **Member Account**
  - email: harry.potter@email.com
  - Password: `pp_merino_123!`

=======

### Image Credits

- [app/static/uploads/tutor.jpg] - https://pixabay.com/vectors/man-shepherd-cartoon-character-8331569/
- [app/static/uploads/member.jpg] - https://pixabay.com/vectors/girl-character-people-person-152497/
- [app/static/uploads/manager.jpg] - https://pixabay.com/vectors/businessman-workplace-office-boss-6593090/
- [app/static/img/default-profile.jpg] - https://pixabay.com/illustrations/sheep-sleeping-fantasy-animal-7178748/
- [app/static/img/logo.png] - Created by Lin via Photoshop
- [app/static/img/banner.jpg] - Created by Lin via Photoshop
- [app/static/img/bigsheep.jpg] - https://stockcake.com/i/sunset-sheep-serenity_301197_446675
- [app/static/img/sheepsun.jpg] - https://stockcake.com/i/sunset-sheep-grazing_455090_326776
- [app/static/img/sheep.jpg] - https://stockcake.com/i/grazing-sheep-solitude_419700_290682
- [app/static/img/tutor.jpg] - https://stockcake.com/i/farmer-checking-tablet_545248_931420
- [app/static/img/lesson.jpg] - https://stockcake.com/i/shearing-sheep-farm_839645_938768
- [app/static/img/homepage.jpg] - https://stockcake.com/i/pastoral-sheep-grazing_667163_182592
