import pymysql
import pymysql.cursors
from flask import Flask, request, jsonify
from flask_cors import CORS
import os # Mantenha o import os para a linha da porta do app.run

app = Flask(__name__)
CORS(app)

# Função para conectar ao banco de dados - AGORA COM VALORES FIXOS PARA TESTE FINAL
def conectar():
    # ATENÇÃO: ESTES VALORES ESTÃO HARDCODED. ISTO NÃO É A MELHOR PRÁTICA PARA SEGURANÇA.
    # APENAS USE ISSO PARA TESTE DO TCC SE NÃO CONSEGUIR FAZER AS VARIAVEIS DE AMBIENTE FUNCIONAREM.
    db_host = 'nozomi.proxy.rlwy.net'
    db_user = 'root'
    db_password = 'sbxPjavPiJTbXcTgifxlgJmDUHVCFGDJ'
    db_name = 'railway'
    db_port = 39014 # Railway fornece a porta como número, então já é um inteiro

    print(f"Tentando conectar COM VALORES FIXOS: Host={db_host}, User={db_user}, DB={db_name}, Port={db_port}")

    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Conexão com o banco de dados MySQL do Railway ESTABELECIDA COM SUCESSO usando valores fixos!")
        return conn
    except Exception as e:
        print(f"Erro CRÍTICO ao conectar ao banco de dados (mesmo com valores fixos): {e}")
        raise # Re-lança a exceção para que o Flask a capture e retorne o 500

# ... (Restante do seu código API: rotas /novo_tcc, /listar_tccs, /excluir_tcc, etc.) ...

if __name__ == '__main__':
    # O Render usa a variável de ambiente 'PORT' para definir a porta da sua aplicação
    # É importante manter isso lendo de os.environ.get('PORT')
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
