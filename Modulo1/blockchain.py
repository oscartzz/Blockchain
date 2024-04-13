import datetime
import hashlib
import json
from flask import Flask, jsonify

class Blockchain:
    #componentes del blockchain
    def __init__(self):
        self.chain = [] # esta lista es la cadena de bloques y empieza estando vacia
        #bloque genesis --> primer bloque de nuestro blockchain
        #funcion que crea bloques, dos argumentos proof, previous_hash, '0' porque se utiliza una libreria que solo acepta string bajo comillas
        self.create_block(proof = 1,previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        #esta funcion debe crear el nuevo bloque que ha sido minado
        # blockchain con sus 4 claves esenciales : indice, timestamp, proof, hash_previo
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
    
    #funcion que nos permite obtener el block anterior
    def get_previous_block(self):
        return self.chain[-1] #ultimo bloque de la cadena
    
    #proof of work --> numero o pedazo de datos que los mineros deben encontrar para minar el bloque
    
    def proof_of_work(self, previous_proof):
        new_proof = 1 #variable que va a ser el nuevo proof, ponemos 1 porque para resolver el problema incrementaremos el numero de 1 en 1 hasta obtener el proof correcto
        check_proof= False #
        while check_proof is False:
            # mas 0 agreguemos mas complicado sera el problema
            # el problema que queremos que los mineros resuelvan va a ser el siguiente new_proof**2 - previous_proof**2
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
        
    def hash(self, block):
        #se utiliza el block como input para retornarlo en su version sha256
        #codificamos el bloque para que pueda ser aceptado por el hash operation
        encoded_block = json.dumps(block, sort_keys = True).encode() #con encode tenemos el block en el formato indicado sha256
        return hashlib.sha256(encoded_block).hexdigest()
    
    #checkeamos si la cadena es valida
    def is_chain_valid(self, chain):
        previous_block = chain[0] # empezamos por el primer block de la cadena
        block_index = 1 #inicializamos el indice
        while block_index < len(chain): #iteramos en todos los blocks de la cadena y no para hasta llegar al ultimo indice de la cadena
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            #ahora chequeamos que los proof del blqoue anterior y del bloque actual coinciden
            previous_proof = previous_block['proof'] # proof del block anterior
            proof = block['proof'] # proof actual
            hash_operation =  hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    

# Paso 2 - Minando el blockchain

app= Flask (__name__) #inicializamos la web app --> buscar Flask quickstart
blockchain=Blockchain()

#minando un nuevo bloque
#decorador
@app.route('/mine_block', methods=['GET'])

def mine_block():
    #primero hay que resolver el problema del proofofwork, una vez obtenemos el proof basado en el previous proof es que hemos conseguido minar
    previous_block = blockchain.get_previous_block() #obtiene el bloque anterior, es un diccionario con proof inicializado a 1
    previous_proof = previous_block['proof'] #obtiene el valor proof del bloque, si es el primer bloque obtiene proof = 1
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message':'Felicidades, has minado un bloque',
               'index':block['index'],
               'timestamp': block['timestamp'],
               'proof':block['proof'],
               'previous_hash': block['previous_hash']}
    return jsonify(response), 200 #codigo http, mirar en internet

#Obtneiendo la cadena completa
@app.route('/get_chain', methods=['GET'])

def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

#Obteniendo la validez de la cadena de bloques
@app.route('/is_valid', methods=['GET'])

def is_valid():
    is_valid= blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response={'message': 'Todo Bien. El blockchain es valido'}
    else:
        response = {'message':'Houston tenemos un problema el blockchain no es valido'}
    return jsonify(response), 200


# Corriendo la app
app.run(host='0.0.0.0', port='5000')

"""

def proof_of_work(previous_proof):
    new_proof = 1 #variable que va a ser el nuevo proof, ponemos 1 porque para resolver el problema incrementaremos el numero de 1 en 1 hasta obtener el proof correcto
    check_proof= False #
    while check_proof is False:
        # mas 0 agreguemos mas complicado sera el problema
        # el problema que queremos que los mineros resuelvan va a ser el siguiente new_proof**2 - previous_proof**2
        hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
        if hash_operation[:4] == "0000":
            check_proof = True
        else:
            new_proof += 1
        return new_proof
    
print(proof_of_work(2))

"""

#hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
#hash_operation[:4]

