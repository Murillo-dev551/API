from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pymysql.cursors
from pymysql.cursors import DictCursor
import os

app = Flask(__name__)
CORS(app)

# Função de conexão com o banco de dados
def conectar():
    # --- LENDO VARIAVEIS DE AMBIENTE DO RAILWAY ---
    
    # 1. Host e Porta (Para proxy TCP externo, que são as variáveis do Railway)
    db_host = os.environ.get("RAILWAY_TCP_PROXY_DOMAIN", "nozomi.proxy.rlwy.net")
    db_port_raw = os.environ.get("RAILWAY_TCP_PROXY_PORT", "39014")

    # 2. Credenciais Dinâmicas (Geralmente injetadas pelo serviço MySQL)
    db_user = os.environ.get("MYSQLUSER") 
    db_password = os.environ.get("MYSQL_ROOT_PASSWORD") 
    db_name = os.environ.get("MYSQL_DATABASE", "railway") 

    # --- Verificações e Fallbacks (Para garantir que não haja erros de None) ---
    
    if not db_host:
        raise ValueError("Erro de Conexão: Host (RAILWAY_TCP_PROXY_DOMAIN) não encontrado.")
    if not db_name:
        raise ValueError("Erro de Conexão: Nome do Banco de Dados (MYSQL_DATABASE) não encontrado.")
        
    # Fallback para usuário (Se não houver MYSQL_USER, assume 'root')
    if not db_user:
        db_user = 'root'
        
    # A senha e a porta DEVEM ser injetadas. Se não forem, falha.
    if not db_password:
        raise ValueError("Erro de Conexão: Senha (MYSQL_PASSWORD) não encontrada. Credenciais ausentes.")
    
    # 3. CONVERSÃO CRÍTICA: A porta lida é uma string, deve ser INT.
    if not db_port_raw:
        raise ValueError("Erro de Conexão: Porta (RAILWAY_TCP_PROXY_PORT) não encontrada.")
        
    try:
        db_port = int(db_port_raw)
    except Exception:
        raise ValueError(f"Porta inválida '{db_port_raw}'. Deve ser um número inteiro.")
    
    # --- Conexão ---
    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port, 
        cursorclass=pymysql.cursors.DictCursor
    )

# Rota para cadastrar novo TCC
@app.route('/novo_tcc', methods=['POST'])
def novo_tcc():
    try:
        dados = request.get_json()
        titulo = dados.get('titulo')
        autor = dados.get('autor')
        curso = dados.get('curso')
        ano = dados.get('ano')
        link_arquivo = dados.get('link_arquivo')
        id_membro_wix = dados.get('id_membro_wix')

        if not all([titulo, autor, curso, ano, link_arquivo, id_membro_wix]):
            return jsonify({"erro": "Campos obrigatórios faltando"}), 400

        conn = conectar()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO tccs (titulo, autor, curso, ano, link_arquivo, id_membro_wix)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (titulo, autor, curso, ano, link_arquivo, id_membro_wix))
            conn.commit()
        conn.close()

        return jsonify({"mensagem": "TCC cadastrado com sucesso"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rota para listar TCCs
@app.route('/listar_tccs', methods=['GET'])
def listar_tccs():
    try:
        titulo = request.args.get('titulo')
        autor = request.args.get('autor')
        curso = request.args.get('curso')
        ano = request.args.get('ano')

        query = "SELECT * FROM tccs WHERE 1=1"
        valores = []

        if titulo:
            query += " AND titulo LIKE %s"
            valores.append(f"%{titulo}%")
        if autor:
            query += " AND autor LIKE %s"
            valores.append(f"%{autor}%")
        if curso:
            query += " AND curso = %s"
            valores.append(curso)
        if ano:
            query += " AND ano = %s"
            valores.append(ano)

        conn = conectar()
        with conn.cursor() as cursor:
            cursor.execute(query, valores)
            resultado = cursor.fetchall()
        conn.close()

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/excluir_tcc', methods=['DELETE'])
def excluir_tcc():
    try:
        tcc_id = request.args.get('id')
        if not tcc_id:
            return jsonify({"erro": "ID não fornecido"}), 400

        conn = conectar()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tccs WHERE id = %s", (tcc_id,))
            conn.commit()
        conn.close()
        return jsonify({"mensagem": "TCC excluído com sucesso"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/buscar_tcc', methods=['GET'])
def buscar_tcc():
    try:
        titulo = request.args.get('titulo')
        if not titulo:
            return jsonify({"erro": "Título não informado"}), 400

        conn = conectar()
        with conn.cursor(DictCursor) as cursor:
            cursor.execute("SELECT * FROM tccs WHERE titulo LIKE %s LIMIT 1", (f"%{titulo}%",))
            resultado = cursor.fetchall()
        conn.close()

        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)






















