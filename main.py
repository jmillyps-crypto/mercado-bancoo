from flask import Flask, render_template, redirect, url_for, flash, request
import fdb

app = Flask(__name__)


app.config['SECRET_KEY'] = 'Aqui_e_a_chave_do_grupo'

host = 'localhost'
database = r'C:\Users\marco\Downloads\BANCO .FDB'
user = 'SYSDBA'
password = 'SYSDBA'

con = fdb.connect(host=host, database=database, user=user, password=password)

@app.route('/')
def criarconta():
    return render_template('criarconta.html')


@app.route('/endereco')
def endereco():
    return render_template('endereco.html')

@app.route('/adicionar_endereco', methods=['POST'])
def adicionar_endereco():
    cep = request.form['cep']
    rua = request.form['rua']
    numero = request.form['numero']
    complemento = request.form['complemento']  or None
    nome = request.form['nome']
    telefone = request.form['telefone']

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT 1 FROM endereco e WHERE nome = ? AND rua = ? AND numero = ?""", (nome,rua,numero))
        if cursor.fetchone():
            flash('Erro: Endereço já cadastrado')
            return redirect(url_for('endereco'))

        cursor.execute( """ INSERT INTO endereco (cep,rua,numero,complemento,nome,telefone)
                            VALUES (?, ? ,?, ?, ? ,?)""", (cep,rua,numero,complemento,nome,telefone))

        con.commit()
        return redirect(url_for('pagamento'))

    except Exception as e:
        flash(f"Ocorreu um error -> {e}")
        con.rollback()
        return redirect(url_for('endereco'))

    finally:
        cursor.close()

@app.route('/pagamento')
def pagamento():
    cursor = con.cursor() #abrindo o cursor

    cursor.execute("""SELECT e.id_endereco,e.rua, e.numero, e.cep 
                            FROM endereco e""")

    enderecos = cursor.fetchall()

    cursor.close()
    return render_template('pagamento.html', enderecos=enderecos)

@app.route('/editar_endereco/<int:id>', methods=['GET','POST'])
def editar_endereco(id):
    cursor = con.cursor()
    try:
        cursor.execute("""SELECT id_endereco, cep, rua, numero, complemento, nome, telefone
                          FROM endereco e WHERE id_endereco = ?""", (id,))

        endereco = cursor.fetchone()


        if not endereco:
            flash('Endereço não encontrado')
            return redirect(url_for('pagamento'))

        if request.method == 'POST':
            cep = request.form['cep']
            rua = request.form['rua']
            numero = request.form['numero']
            complemento = request.form['complemento'] or None
            nome = request.form['nome']
            telefone = request.form['telefone']

            cursor.execute("""UPDATE endereco SET cep = ?,rua = ?,numero = ?,complemento = ?,nome = ?,telefone = ?
                              WHERE id_endereco = ?""", (cep, rua, numero, complemento, nome, telefone, id))

            con.commit()
            flash("Endereço editado com sucesso")
            return redirect(url_for('pagamento'))

    except Exception as e:
            con.rollback()
            flash(f"Ocorreu um error -> {e}")
            return redirect(url_for('pagamento'))


    finally:
        cursor.close()
    return render_template('editar_endereco.html', endereco=endereco)


@app.route('/finalizar')
def finalizar():
    return render_template('pagamento-banco.html')


@app.route('/cadastrar_cartao', methods=['POST'])
def cadastrar_cartao():
    numero_cartao = request.form['numero']
    nome = request.form['nome']
    vencimento = request.form['vencimento']
    codigo = request.form['codigo']
    cpf = request.form['cpf']

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT 1 FROM pagamento p WHERE numero_cartao = ? and nome = ? and vencimento = ? and codigo = ? and cpf = ?""", (numero_cartao,nome,vencimento,codigo,cpf))
        if cursor.fetchone():
            flash('Erro: Cartão já cadastrado')
            return redirect(url_for('finalizar'))

        cursor.execute( """ INSERT INTO pagamento (numero_cartao, nome, vencimento, codigo, cpf)
                            VALUES (?, ? ,?,?, ?)""", (numero_cartao, nome, vencimento, codigo, cpf))

        con.commit()
        return redirect(url_for('mensagem'))

    except Exception as e:
        flash(f"Ocorreu um error -> {e}")
        con.rollback()
        return redirect(url_for('finalizar'))

    finally:
        cursor.close()

@app.route('/mensagem')
def mensagem():
    return render_template('mensagem.html')

if __name__ == '__main__':
    app.run(debug=True)
