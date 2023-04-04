from flask import Flask, render_template, request, redirect, url_for, jsonify
from controller.controllerHerramienta import *


#Para subir archivo tipo foto al servidor
import os
from werkzeug.utils import secure_filename 


#Declarando nombre de la aplicación e inicializando, crear la aplicación Flask
app = Flask(__name__)
application = app

msg  =''
tipo =''


#Creando mi decorador para el home, el cual retornara la Lista de Carros
@app.route('/', methods=['GET','POST'])
def inicio():
    return render_template('public/layout.html', miData = listaHerramientas())


#RUTAS
@app.route('/registrar-herramienta', methods=['GET','POST'])
def addCarro():
    return render_template('public/acciones/add.html')


 
#Registrando nuevo herramienta
@app.route('/herramienta', methods=['POST'])
def formAddHerramienta():
    if request.method == 'POST':
        articulo               = request.form['articulo']
        description              = request.form['description']
        direccion                = request.form['direccion']
        telefono               = request.form['telefono']
        precio             = request.form['precio']
        fecha            = request.form['fecha']
        
        
        if(request.files['foto'] !=''):
            file     = request.files['foto'] #recibiendo el archivo
            nuevoNombreFile = recibeFoto(file) #Llamado la funcion que procesa la imagen
            resultData = registrarHerramienta(articulo, description, direccion, telefono, precio, fecha, nuevoNombreFile)
            if(resultData ==1):
                return render_template('public/layout.html', miData = listaHerramientas(), msg='El Registro fue un éxito', tipo=1)
            else:
                return render_template('public/layout.html', msg = 'Metodo HTTP incorrecto', tipo=1)   
        else:
            return render_template('public/layout.html', msg = 'Debe cargar una foto', tipo=1)
            


@app.route('/form-update-herramienta/<string:id>', methods=['GET','POST'])
def formViewUpdate(id):
    if request.method == 'GET':
        resultData = updateHerramienta(id)
        if resultData:
            return render_template('public/acciones/update.html',  dataInfo = resultData)
        else:
            return render_template('public/layout.html', miData = listaHerramientas(), msg='No existe herramienta', tipo= 1)
    else:
        return render_template('public/layout.html', miData = listaHerramientas(), msg = 'Metodo HTTP incorrecto', tipo=1)          
 
   
  
@app.route('/ver-detalles-del-herramienta/<int:idHerramienta>', methods=['GET', 'POST'])
def viewDetalleHerramienta(idHerramienta):
    msg =''
    if request.method == 'GET':
        resultData = detallesdelCarro(idHerramienta) #Funcion que almacena los detalles del herramienta
        
        if resultData:
            return render_template('public/acciones/view.html', infoCarro = resultData, msg='Detalles del herramienta', tipo=1)
        else:
            return render_template('public/acciones/layout.html', msg='No existe el herramienta', tipo=1)
    return redirect(url_for('inicio'))
    

@app.route('/actualizar-herramienta/<string:idHerramienta>', methods=['POST'])
def  formActualizarHerramienta(idHerramienta):
    if request.method == 'POST':
        articulo           = request.form['articulo']
        description          = request.form['description']
        direccion            = request.form['direccion']
        telefono           = request.form['telefono']
        precio         = request.form['precio']
        fecha        = request.form['fecha']
        
        #Script para recibir el archivo (foto)
        if(request.files['foto']):
            file     = request.files['foto']
            fotoForm = recibeFoto(file)
            resultData = recibeActualizarCarro(articulo, description, direccion, telefono, precio, fecha, fotoForm, idHerramienta)
        else:
            fotoCarro  ='sin_foto.jpg'
            resultData = recibeActualizarCarro(articulo, description, direccion, telefono, precio, fecha, fotoCarro, idHerramienta)

        if(resultData ==1):
            return render_template('public/layout.html', miData = listaHerramientas(), msg='Datos del carro actualizados', tipo=1)
        else:
            msg ='No se actualizo el registro'
            return render_template('public/layout.html', miData = listaHerramientas(), msg='No se pudo actualizar', tipo=1)


#Eliminar herramienta
@app.route('/borrar-herramienta', methods=['GET', 'POST'])
def formViewBorrarHerramienta():
    if request.method == 'POST':
        idHerramienta         = request.form['id']
        nombreFoto      = request.form['nombreFoto']
        resultData      = eliminarHerramienta(idHerramienta, nombreFoto)

        if resultData ==1:
            #Nota: retorno solo un json y no una vista para evitar refescar la vista
            return jsonify([1])
            #return jsonify(["respuesta", 1])
        else: 
            return jsonify([0])




def eliminarHerramienta(idHerramienta='', nombreFoto=''):
        
    conexion_MySQLdb = connectionBD() #Hago instancia a mi conexion desde la funcion
    cur              = conexion_MySQLdb.cursor(dictionary=True)
    
    cur.execute('DELETE FROM herramientas WHERE id=%s', (idHerramienta,))
    conexion_MySQLdb.commit()
    resultado_eliminar = cur.rowcount #retorna 1 o 0
    #print(resultado_eliminar)
    
    basepath = os.path.dirname (__file__) #C:\xampp\htdocs\localhost\Crud-con-FLASK-PYTHON-y-MySQL\app
    url_File = os.path.join (basepath, 'static/assets/fotos_herramientas', nombreFoto)
    os.remove(url_File) #Borrar foto desde la carpeta
    #os.unlink(url_File) #Otra forma de borrar archivos en una carpeta
    

    return resultado_eliminar



def recibeFoto(file):
    print(file)
    basepath = os.path.dirname (__file__) #La ruta donde se encuentra el archivo actual
    filename = secure_filename(file.filename) #Nombre original del archivo

    #capturando extensión del archivo ejemplo: (.png, .jpg, .pdf ...etc)
    extension           = os.path.splitext(filename)[1]
    nuevoNombreFile     = stringAleatorio() + extension
    #print(nuevoNombreFile)
        
    upload_path = os.path.join (basepath, 'static/assets/fotos_herramientas', nuevoNombreFile) 
    file.save(upload_path)

    return nuevoNombreFile

       
  
  
#Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    return redirect(url_for('inicio'))
    
    
    
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)