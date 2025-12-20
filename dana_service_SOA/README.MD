# How To Use Dana Service

## Clone Repository
``bash
    git clone https://github.com/whsasmita/UTS-SOA-SERVICE-DANA-APP.git
``

## Install Dependecies
``bash
    pip install -r requirements.txt
``

## Create Database
``bash
    python setup_database.py
``

## Start Service
### Account Service
1. Change directory to account_service
``bash
    cd services/account_service
``

2. Start the service
``bash
    python server.py
``

### TopUp Service
1. Change directory to topup_service
``bash
    cd services/topup_service
``

2. Start the service
``bash
    python server.py
``

### Transaction Service
1. Change directory to transaction_service
``bash
    cd services/transaction_service
``

2. Start the service
``bash
    python server.py
``

### Task Service (Not All Time)
1. Change directory to tasks
``bash
    cd tasks
``

2. Start the service
``bash
    python filename.py
``

## Start Client
1. Change directory to client
``bash
    cd client
``

2. Start the service
``bash
    python main_client.py
``