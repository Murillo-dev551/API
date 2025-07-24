from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)  # Libera acesso externo (Wix, etc.)

# Conexão com banco de dados
def conectar():
    return pymysql.connect(
        host='SEU_HOST',
        user='SEU_USUARIO',
        password='SUA_SENHA',
        database='SEU_BANCO',
        cursorclass=pymysql.cursors.DictCursor
    )

# Rota para cadastrar novo TCC
@app.route('/novo_tcc', methods=['POST'])
def novo_tcc():
    dados = request.json
    campos = ['titulo', 'autor', 'curso', 'ano', 'link_arquivo']
    if not all(campo in dados and dados[campo] for campo in campos):
        return jsonify({'erro': 'Preencha todos os campos obrigatórios'}), 400

    conn = conectar()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO tccs (titulo, autor, curso, ano, link_arquivo, id_membro_wix)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                dados['titulo'],
                dados['autor'],
                dados['curso'],
                int(dados['ano']),
                dados['link_arquivo'],
                dados.get('id_membro_wix')
            ))
            conn.commit()
        return jsonify({'mensagem': 'TCC cadastrado com sucesso!'})
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
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

    conn = conectar()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            resultados = cursor.fetchall()
        return jsonify(resultados)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
    finally:
        conn.close()

# Inicia o servidor
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)