# Importa as bibliotecas necessárias do Flask
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Cria a aplicação Flask
app = Flask(__name__)

# Configura o banco de dados SQLite que será criado com o nome 'agenda.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agenda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o SQLAlchemy com a app Flask (ORM que lida com o banco)
banco = SQLAlchemy(app)

# Define o modelo da tabela Videoconferencia no banco de dados
class Videoconferencia(banco.Model):
    id = banco.Column(banco.Integer, primary_key=True)      # ID único de cada registro
    titulo = banco.Column(banco.String(200))                # Título da videoconferência
    data = banco.Column(banco.String(10))                   # Data (ex: 2025-07-02)
    horario = banco.Column(banco.String(5))                 # Horário (ex: 14:30)
    local = banco.Column(banco.String(100))                 # Local ou plataforma
    link = banco.Column(banco.String(200))                  # Link da reunião (pode ser vazio)
    participantes = banco.Column(banco.Text)                # Lista de participantes
    responsavel = banco.Column(banco.String(100))           # Nome do responsável
    realizada = banco.Column(banco.Boolean, default=False)  # Se foi realizada (✅ ou não)

# Rota principal: mostra as videoconferências pendentes e realizadas
@app.route('/')
def pagina_inicial():
    ordenar_por = request.args.get('ordenar')  # Recebe parâmetro da URL para ordenar
    query = Videoconferencia.query.filter_by(realizada=False)

    # Ordenação condicional
    if ordenar_por in ['titulo', 'data', 'horario', 'participantes', 'responsavel']:
        query = query.order_by(getattr(Videoconferencia, ordenar_por))
    
    eventos = query.all()
    realizados = Videoconferencia.query.filter_by(realizada=True).all()
    return render_template('index.html', eventos=eventos, realizados=realizados)

# Rota para adicionar nova videoconferência
@app.route('/adicionar', methods=['POST'])
def adicionar_evento():
    novo_evento = Videoconferencia(
        titulo=request.form['titulo'],
        data=request.form['data'],
        horario=request.form['horario'],
        local=request.form['local'],
        link=request.form['link'],
        participantes=request.form['participantes'],
        responsavel=request.form['responsavel']
    )
    banco.session.add(novo_evento)     # Adiciona no banco
    banco.session.commit()             # Salva as alterações
    return redirect(url_for('pagina_inicial'))  # Redireciona para a homepage

# Rota para marcar como "realizada"
@app.route('/realizar/<int:id>', methods=['POST'])
def marcar_como_realizada(id):
    evento = banco.session.get(Videoconferencia, id)
    if evento:
        evento.realizada = True
        banco.session.commit()
    return redirect(url_for('pagina_inicial'))

# Rota para excluir videoconferência
@app.route('/excluir/<int:id>')
def excluir_evento(id):
    evento = banco.session.get(Videoconferencia, id)
    if evento:
        banco.session.delete(evento)
        banco.session.commit()
    return redirect(url_for('pagina_inicial'))

# Inicializa o banco de dados e roda o servidor Flask
if __name__ == '__main__':
    with app.app_context():
        banco.create_all()  # Cria as tabelas se ainda não existirem
    app.run(debug=True, host='0.0.0.0', port=5000)  # Roda o app acessível por toda a rede