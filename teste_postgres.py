import psycopg

with psycopg.connect(
    dbname="priorado146"
) as conexao, conexao.cursor() as cursor:

    cursor.execute(
        "SELECT id, nome FROM membros ORDER BY id"
    )

    membros = cursor.fetchall()


print("Conexão realizada com sucesso!")
print("Membros encontrados:")

for membro in membros:
    print(membro)