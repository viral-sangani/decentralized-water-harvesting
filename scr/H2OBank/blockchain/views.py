from django.shortcuts import render
import datetime
import hashlib
import json
from uuid import uuid4
import socket, requests
from urllib.parse import urlparse
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import AnonymousUser


class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = [] 
        self.create_block(nonce = 1, previous_hash = '0')
        self.nodes = set() 

    def create_block(self, nonce, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': nonce,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions 
                }
        self.transactions = [] 
        self.chain.append(block)
        return block

    def get_last_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_nonce):
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce

    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

    def add_transaction(self, sender, receiver, amount, time): 
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount,
                                  'time': str(datetime.datetime.now())})
        previous_block = self.get_last_block()
        return previous_block['index'] + 1

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
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Creating our Blockchain
blockchain = Blockchain()
# Creating an address for the node running our server
node_address = str(uuid4()).replace('-', '') 
root_node = 'e36f0158f0aed45b3bc755dc52ed4560d' 

# Mining a new block
def mine_block(request):
    if request.method == 'GET':
        previous_block = blockchain.get_last_block()
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        previous_hash = blockchain.hash(previous_block)
        
        print(blockchain.transactions)
        if len(blockchain.transactions) == 0:
            blockchain.add_transaction(sender = root_node, receiver = node_address, amount = 1.15, time=str(datetime.datetime.now()))
        block = blockchain.create_block(nonce, previous_hash)
        response = {'message': 'Congratulations, you just mined a block!',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'nonce': block['nonce'],
                    'previous_hash': block['previous_hash'],
                    'transactions': block['transactions']}
    return JsonResponse(response)

# Getting the full Blockchain
def get_chain(request):
    if request.method == 'GET':
        response = {'chain': blockchain.chain,
                    'length': len(blockchain.chain)}
    return JsonResponse(response)

# Checking if the Blockchain is valid
def is_valid(request):
    if request.method == 'GET':
        is_valid = blockchain.is_chain_valid(blockchain.chain)
        if is_valid:
            response = {'message': 'All good. The Blockchain is valid.'}
        else:
            response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return JsonResponse(response)

# Adding a new transaction to the Blockchain
@csrf_exempt
def add_transaction(request): #New

    if request.method == 'POST':
        
        received_json = json.loads(request.body)
        print(received_json)
        transaction_keys = ['sender', 'receiver', 'amount','time']
        if not all(key in received_json for key in transaction_keys):
            return 'Some elements of the transaction are missing', HttpResponse(status=400)
        index = blockchain.add_transaction(received_json['sender'], received_json['receiver'], received_json['amount'],received_json['time'])
        
        response = {'message': f'This transaction will be added to Block {index}'}
    return JsonResponse(response)

# Connecting new nodes
@csrf_exempt
def connect_node(request): #New
    if request.method == 'POST':
        received_json = json.loads(request.body)
        nodes = received_json.get('nodes')
        if nodes is None:
            return "No node", HttpResponse(status=400)
        for node in nodes:
            blockchain.add_node(node)
        response = {'message': 'All the nodes are now connected. The Sudocoin Blockchain now contains the following nodes:',
                    'total_nodes': list(blockchain.nodes)}
    return JsonResponse(response)

# Replacing the chain by the longest chain if needed
def replace_chain(request): #New
    if request.method == 'GET':
        is_chain_replaced = blockchain.replace_chain()
        if is_chain_replaced:
            response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                        'new_chain': blockchain.chain}
        else:
            response = {'message': 'All good. The chain is the largest one.',
                        'actual_chain': blockchain.chain}
    return JsonResponse(response)

class test(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        print(json.loads(request.body))
        return Response({'success': 'true'})

class container_1(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        received_json = json.loads(request.body)
        amount = received_json['amount']
        if amount > 40 and amount < 60:
            amount *= 27

        if amount >= 60 and amount < 80:
            amount *= 24

        if amount < 100 and amount > 80:
            amount *= 21

        if amount < 140 and amount > 101:
            amount *= 12

        if amount <= 40 and amount >= 15:
            amount *= 37
        
        if amount <= 14 and amount > 1:
            amount *= 83

        if "sender" in received_json and "receiver" in received_json and "amount" in received_json:
            blockchain.add_transaction(received_json['sender'], received_json['receiver'], amount,datetime.datetime.now())

        previous_block = blockchain.get_last_block()
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        previous_hash = blockchain.hash(previous_block)
        
        if len(blockchain.transactions) == 0:
            response = {"Error": "No Transection Found"}
        else:
            block = blockchain.create_block(nonce, previous_hash)
            response = {'message': 'Congratulations, you just mined a block!',
                        'index': block['index'],
                        'timestamp': block['timestamp'],
                        'nonce': block['nonce'],
                        'previous_hash': block['previous_hash'],
                        'transactions': block['transactions'],
                        'success': True}
        
        return Response(response)

class container_3(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        received_json = json.loads(request.body)
        print(received_json)
        if "status" in received_json:
            if received_json['status'] == "on":
                url = "http://192.168.43.230/motor=ON"
            elif received_json['status'] == "off":
                url = "http://192.168.43.230/motor=OFF"
            requests.get(url)
        return Response({})

class container_3_data(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        received_json = json.loads(request.body)

        print(received_json)

        amount = received_json['amount']

        if amount > 40 and amount < 60:
            amount *= 27

        if amount >= 60 and amount < 80:
            amount *= 24

        if amount < 100 and amount > 80:
            amount *= 21

        if amount < 140 and amount > 101:
            amount *= 12

        if amount <= 40 and amount >= 15:
            amount *= 37
        
        if amount <= 14 and amount > 1:
            amount *= 83

        if "sender" in received_json and "receiver" in received_json and "amount" in received_json:
            blockchain.add_transaction(received_json['sender'], received_json['receiver'], amount,datetime.datetime.now())

        previous_block = blockchain.get_last_block()
        previous_nonce = previous_block['nonce']
        nonce = blockchain.proof_of_work(previous_nonce)
        previous_hash = blockchain.hash(previous_block)
        
        if len(blockchain.transactions) == 0:
            response = {"Error": "No Transection Found"}
        else:
            block = blockchain.create_block(nonce, previous_hash)
            response = {'message': 'Congratulations, you just mined a block!',
                        'index': block['index'],
                        'timestamp': block['timestamp'],
                        'nonce': block['nonce'],
                        'previous_hash': block['previous_hash'],
                        'transactions': block['transactions'],
                        'success': True}
        
        return Response(response)

#################################################### Website Code #####################################################

# user = e36f0158f0aed45b3bc755dc52ed4560d
# server =  2ad8e222853549e59c9d528731b0cf48


def home_view(request):
    user_transection = []
    total_usage = 0
    total_balance = 0
    for item in blockchain.chain:
        if len(item['transactions']) == 0:
            pass
        else:
            user_transection.append(item['transactions'][0])
            if item['transactions'][0]['receiver'] == "e36f0158f0aed45b3bc755dc52ed4560d":
                #print(item['transactions'][0]['amount'])
                total_usage += item['transactions'][0]['amount']

            if item['transactions'][0]['sender'] == "e36f0158f0aed45b3bc755dc52ed4560d":
                #print(item['transactions'][0]['amount'])
                total_balance += item['transactions'][0]['amount']


    context = {
        'total_usage':total_usage,
        'total_balance': total_balance,
        'usage_last_month': total_usage,
        'water_in_bank': total_balance,
        'user_id': 'e36f0158f0aed45b3bc755dc52ed4560d',
        'user_transection': user_transection
    }
    return render(request, 'website/dashboard.html', context)


def view_transactions(request):
    #template_name: 'website/view_transactions.html'
    user_transactions = []

    for item in blockchain.chain:
        if(len(item['transactions']) == 0):
            pass
        else:
            user_transactions.append(item['transactions'][0])
    
    print(user_transactions)

    context = {
        'transactions': user_transactions,
    }
    return render(request, 'website/view_transactions.html', context)


############################################ Consumer.py #########################################################
class LiveScoreConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'block_chain'
        await self.channel_layer.group_add(
           self.group_name,
           self.channel_name
        )
        await self.accept()

    async def receive(self, text_data):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'get_blockchain',
                'chain': blockchain.chain
            }
        )
    async def get_blockchain(self, event):
        await self.send(text_data=json.dumps({
                'chain': blockchain.chain
            }))


    async def websocket_disconnect(self, message):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )