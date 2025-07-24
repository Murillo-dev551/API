from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os # Importe o módulo os para acessar variáveis de ambiente

app = Flask(__name__)
CORS(app)  # Libera acesso externo (Wix, etc.)

# Conexão com banco de dados
def conectar():
    db_host = os.environ.get('DB_HOST') # <--- ISSO DEVE PERMANECER ASSIM
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')
    db_port = int(os.environ.get('DB_PORT'))

    # ... validações ...

    conn = pymysql.connect(
        host=db_host, # <--- AQUI DEVE SER A VARIÁVEL, NÃO A STRING FIXA
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port,
        cursorclass=pymysql.cursors.DictCursor
    )

# Rota para cadastrar novo TCC
@app.route('/novo_tcc', methods=['POST'])
def novo_tcc():
    dados = request.json
    campos = ['titulo', 'autor', 'curso', 'ano', 'link_arquivo']
    if not all(campo in dados and dados[campo] for campo in campos):
        return jsonify({'erro': 'Preencha todos os campos obrigatórios'}), 400

    conn = None # Inicializa conn para garantir que esteja definido
    try:
        conn = conectar() # Tenta conectar
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO tccs (titulo, autor, curso, ano, link_arquivo, id_membro_wix)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                dados['titulo'],
                dados['autor'],
                dados['curso'],
                dados['ano'],
                dados['link_arquivo'],
                dados.get('id_membro_wix')
            ))
            conn.commit()
        return jsonify({'mensagem': 'TCC cadastrado com sucesso!'})
    except Exception as e:
        # Registre o erro completo para depuração, se necessário
        # app.logger.error(f"Erro ao cadastrar TCC: {e}")
        return jsonify({'erro': str(e)}), 500
    finally:
        if conn: # Garante que conn existe antes de tentar fechar
            conn.close()

# Rota para listar TCCs com filtros
@app.route('/listar_tccs', methods=['GET'])
def listar_tccs():
    autor = request.args.get('autor')
    curso = request.args.get('curso')
    ano = request.args.get('ano')

    query = "SELECT * FROM tccs WHERE 1=1"
    params = []

    if autor:
        query += " AND autor LIKE %s"
        params.append(f"%{autor}%")
    if curso:
        query += " AND curso = %s"
        params.append(curso)
    if ano:
        query += " AND ano = %s"
        params.append(ano)

    conn = None # Inicializa conn para garantir que esteja definido
    try:
        conn = conectar() # Tenta conectar
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            resultados = cursor.fetchall()
        return jsonify(resultados)
    except Exception as e:
        # Registre o erro completo para depuração, se necessário
        # app.logger.error(f"Erro ao listar TCCs: {e}")
        return jsonify({'erro': str(e)}), 500
    finally:
        if conn: # Garante que conn existe antes de tentar fechar
            conn.close()

# Inicia o servidor
if __name__ == '__main__':
    # O Render injeta a porta via variável de ambiente PORT
    # Use a porta fornecida pelo Render, ou 3000 como fallback para desenvolvimento local
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
