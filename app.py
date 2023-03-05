from itertools import count
from typing import Optional, List
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query

c = count()
app = Flask(__name__)
app.debug = True
spec = FlaskPydanticSpec('Flask', title='Live de Python')
spec.register(app)
database = TinyDB("database.json")


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    idade: int

print("c ", lambda: next(c))
class Pessoas(BaseModel):
    pessoas: List[Pessoa]
    count: int


@app.get('/pessoas')
@spec.validate(resp=Response(HTTP_200=Pessoas))
def pegar_pessoas():
    "Retorna pessoas"

    return jsonify(
        Pessoas(
            pessoas=database.all(),
            count=(len(database.all()))
        ).dict()
    )

@app.post('/pessoas')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_201=Pessoa))
def inserir_pessoas():
    "Insere uma pessoa no banco de dados"
    body = request.context.body.dict()
    database.insert(body)
    return body


@app.put('/pessoas/<int:id>')
@spec.validate(
    body=Request(Pessoa),
    resp=Response(HTTP_201=Pessoa)
)
def altera_pessoa(id):
    """Altera uma pessoa no banco de dados"""
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    return jsonify(
        body
    )


@app.delete('/pessoas/<int:id>')
@spec.validate(
    resp=Response(HTTP_204=Pessoa)
)
def deleta_pessoa(id):
    """Remove uma pessoa do banco de dados"""
    Pessoa = Query()
    database.remove(Pessoa.id == id)
    return jsonify(
        {}
    )


app.run(debug=True)
