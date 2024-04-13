import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests # agarrar los nodos correctos 
from uuid import uuid4
from urllib.parse import urlparse


class Blockchain:
    #componentes del blockchain
    def __init__(self):
        self.chain = [] # esta lista es la cadena de bloques y empieza estando vacia
        self.transactions = []
        #bloque genesis --> primer bloque de nuestro blockchain
        #funcion que crea bloques, dos argumentos proof, previous_hash, '0' porque se utiliza una libreria que solo acepta string bajo comillas
        self.create_block(proof = 1,previous_hash = '0')
        self.nodes = set()
    
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                #length = response.json(['length']) no funciona porque no se le puede pasar la clave del diccionario directamente, response es un objeto aun. Hay que utilizar el metodo get()
                length = response.json().get('length')
                chain = response.json().get('chain')
                
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
            
            if longest_chain:
                self.chain = longest_chain
                return True
            return False
            
    
    def create_block(self, proof, previous_hash):
        #esta funcion debe crear el nuevo bloque que ha sido minado
        # blockchain con sus 4 claves esenciales : indice, timestamp, proof, hash_previo
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions':self.transactions}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,
                                 'receiver': receiver,
                                 'amount': amount})
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
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

#Creando una Direccion para el Nodo en el puerto 5000
node_address = str(uuid4()).replace('-','')

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
    blockchain.add_transaction(sender=node_address, receiver = 'Eric', amount=1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message':'Felicidades, has minado un bloque',
               'index':block['index'],
               'timestamp': block['timestamp'],
               'proof':block['proof'],
               'previous_hash': block['previous_hash'],
               'transactions': block['transactions']}
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

#Agregando nueva transaction al blockchain
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Algun elemento de la transaccion esta faltando', 400
    
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'la transaccion sera añadida al bloque {index}'}
    return jsonify(response), 201 #es un POST request y no un GET por eso el codigo de respuesta es el 201

# Pase 3: Descentralizando el Blockchain

#Conectando Nuevos Nodos
@app.route('/connect_node', methods = ['POST'])
def conncet_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node', 401 # metodo POST no GET por eso 401
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : 'Todos los nodos estan ahora conectados. El Oscarcoin blockchain contiene los siguiente nodos:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

#reemplazar las cadenas mas cortas de los nodos por la mas larga
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced= blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'Los nodos tenian diferentes cadenas asique la cadena fue reemplazada por la mas larga',
                    'new_chain': blockchain.chain}
    else:
        response = {'message':'todo bien la cadena es la mas larga',
                    'current_chain': blockchain.chain}
    return jsonify(response), 200
    
    

# Corriendo la app
app.run(host='0.0.0.0', port='5001')