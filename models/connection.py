

def conn():
  username = 'postgres'
  password = 'dalab'
  db_name = 'dalab_dashboard'
  url  = "postgresql://"+username +":"+password+"@localhost:5432/"+db_name
  return url
