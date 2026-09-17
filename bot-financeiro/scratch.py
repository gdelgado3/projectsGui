import sqlite3
conexao=sqlite3.connect("crioeu")
cursor=conexao.cursor()
autores=cursor.execute("CREATE TABLE IF NOT EXISTS autores(id INTEGER PRIMARY KEY,nome TEXT)")
livros=cursor.execute("CREATE TABLE IF NOT EXISTS livros(id INTEGER PRIMARY KEY,titulo TEXT, autor_id INTEGER REFERENCES autores(id))")
cursor.execute("INSERT INTO autores(nome) VALUES ('Dan Brown')")
iddanbrown=cursor.lastrowid
cursor.execute("INSERT INTO autores(nome) VALUES ('Robert Green')")
idrobert=cursor.lastrowid
cursor.execute(f"INSERT INTO livros(titulo,autor_id) VALUES ('Codigo da vinci',{iddanbrown})")
cursor.execute(f"INSERT INTO livros(titulo,autor_id) VALUES ('Mestria',{idrobert})")
cursor.execute(f"INSERT INTO livros(titulo,autor_id) VALUES ('48 leis poder',{idrobert})")
cursor.execute("SELECT autores.nome,livros.titulo FROM livros JOIN autores ON livros.autor_id=autores.id")
resultadojoin=cursor.fetchall()
print(resultadojoin)



