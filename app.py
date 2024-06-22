from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy
from models import Sucursal,Paquete,Transporte,db
import random
from datetime import datetime

app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/despachante')
def despachante():
    sucursales = db.session.query(Sucursal).all()
    return render_template('despachante.html', sucursales=sucursales)

@app.route('/funcionalidades')
def funcionalidades():
    return render_template('funcionalidades.html')

@app.route('/Registrar_P', methods=['GET', 'POST'])
def Registrar_P():
    if request.method == 'POST':
        peso = request.form.get('peso')
        nombre = request.form.get('nombre')
        direccion = request.form.get('direccion')
        sucursal = request.form.get('sucursal')

        if not peso or not nombre or not direccion or not sucursal:
            return 'Error: Debes ingresar todos los campos', 400

        try:
            peso = float(peso)
            if peso <= 0:
                return 'Error: El peso debe ser un número positivo', 400
        except ValueError:
            return 'Error: El peso debe ser un número válido', 400

        
        num_envio = random.randint(100000, 999999)
        

        paquete = Paquete(
            numeroenvio=num_envio,
            peso=peso,
            nomdestinatario=nombre,
            dirdestinatario=direccion,
            entregado=False,
            observaciones=None,
            idsucursal=int(sucursal),
            idtransporte=None,
            idrepartidor = None
        )
        
        try:
            db.session.add(paquete)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return f'Error al registrar el paquete: {e}', 500

        return render_template('Exito.html', mensaje=f'Registro exitoso. Número de envío: {num_envio}')
    else:
        return render_template('Registrar_P.html')
    


@app.route('/Registar_S', methods=['GET', 'POST'])
def Registrar_S():
    if request.method == 'POST':
        sucursal_destino = request.form.get('sucursal_destino')
        paquetes_ids = request.form.getlist('paquetes')

        if not sucursal_destino or not paquetes_ids:
            return 'Error: Debes seleccionar una sucursal destino y al menos un paquete', 400

        # Obtener fecha y hora actuales para la salida del transporte
        fecha_hora_salida = datetime.now()
        numerotransporte = random.randint(100,300)

        # Crear el transporte
        transporte = Transporte(
            numerotransporte = numerotransporte,
            fechahorasalida=fecha_hora_salida,
            fechahorallegada=None,  # La llegada aún no se registra
            idsucursal=int(sucursal_destino)
        )

        try:
            db.session.add(transporte)
            db.session.flush()  # Para obtener el ID del transporte antes de hacer commit

            # Asignar paquetes al transporte
            for paquete_id in paquetes_ids:
                paquete = db.session.query(Paquete).filter_by(id=paquete_id).first()
                if paquete:
                    paquete.idtransporte = transporte.id

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f'Error al registrar la salida del transporte: {e}', 500

        return render_template('Exito.html', mensaje='Salida de transporte registrada exitosamente')
    else:
        sucursales = db.session.query(Sucursal).all()
        paquetes = db.session.query(Paquete).filter_by(entregado=False, idtransporte=None).all()
        return render_template('Registrar_S.html', sucursales=sucursales, paquetes=paquetes)

@app.route('/Registrar_Ll', methods=['GET', 'POST'])
def Registrar_Ll():
    if request.method == 'POST':
        transporte_id = request.form.get('transporte_id')

        if not transporte_id:
            return 'Error: Debes seleccionar un transporte', 400

        # Obtener fecha y hora actuales para la llegada del transporte
        fecha_hora_llegada = datetime.now()

        try:
            # Buscar el transporte en la base de datos
            transporte = db.session.query(Transporte).filter_by(id=transporte_id).first()
            if not transporte:
                return 'Error: Transporte no encontrado', 404

            # Actualizar la fecha y hora de llegada
            transporte.fechahorallegada = fecha_hora_llegada
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f'Error al registrar la llegada del transporte: {e}', 500

        return render_template('Exito.html', mensaje='Llegada de transporte registrada exitosamente')
    else:
        # Obtener todos los transportes que aún no han registrado una fecha de llegada
        transportes = db.session.query(Transporte).filter_by(fechahorallegada=None).all()
        return render_template('Registrar_Ll.html', transportes=transportes)


def create_app():
    db.init_app(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
