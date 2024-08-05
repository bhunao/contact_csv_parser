# Persons CSV Parser

## Arquitetura
### Tecnologías
- Docker
- Python 3.11
- [FastAPI](https://fastapi.tiangolo.com/) 0.109
- [Pydantic](https://docs.pydantic.dev/) 2.8
- [Jinja2Fragments](https://github.com/sponsfreixes/jinja2-fragments) 1.2
- [Motor](https://motor.readthedocs.io/en/stable/) 3.1
- [HTMX](https://htmx.org/) 2.0
- [Bootstrap](https://getbootstrap.com/) 5.3
- [MongoDB](https://www.mongodb.com/docs/upcoming/release-notes/7.0/) mongodb 7.0
- [Mongo-Express](https://hub.docker.com/_/mongo-express/) 

O projeto foi criado utilizando como base FastAPI para o back-end e Jinja2Fragments com HTMX no front-end, utili

#### Design
O projeto foi criado utilizando tecnologías simples e que entregam e assim facilitando a velocidade de desenvolvimento e adição de novas funcionalidades.

##### Front-End
No front-end foi utilizado [Bootstrap](https://getbootstrap.com/) para estilização e responvidade da aplicação. [Jinja2Fragments](https://github.com/sponsfreixes/jinja2-fragments) é utilizado para o backend para retornar a pagina HTML ao usuário, diferente do [Jinja](https://jinja.palletsprojects.com/en/3.1.x/) ele pode retornar sómente blocos de HTML gerados no Jinja fazendo com que seja possivel criar junto com [HTMX](https://htmx.org/) paginas que consigam conectar com o backend diretamente sem a necessidade de ter uma aplicação separada para o front-end já que HTMX te da acesso a AJAX, transições CSS, WebSockets e Server Sent Events direto no HTML.

##### Back-End
No back-end foi utilizado [FastAPI](https://fastapi.tiangolo.com/) um frame moderno de alta performance para construção de APIs, junto com ele também é utilizado o framework [Pydantic](https://docs.pydantic.dev/) para validação de dados e por ultimo [Motor](https://motor.readthedocs.io/en/stable/) para conexão asyncrona com banco de dados para poder aproveitar a asyncronissidade do FastAPI.

##### Mongo-Express
Imagem docker utilizada no desenvolvimento para facilitar o desenvolvimento com mongodb.


### Rodando o Projeto
#### Variáveis de Ambiente
O projeto utiliza de algumas variáveis de ambiente que ficam no arquivo `.env`. No repositório existe um arquivo de exemplo com nome de `.env_example` que contem as variáveis de ambiente necessárias para rodar o projeto que são `MONGO_INITDB_ROOT_USERNAME` e `MONGO_INITDB_ROOT_PASSWORD` para uso do banco de dados.

Para rodar o projeto é necessário ter o docker instalado e rodar os seguintes comandos:
`docker compose build`  
`docker compose up`

## O Projeto

### Adicionar arquivo
![index](imgs/screnshot_index.png) 
### Menu expandivel
![index](imgs/screnshot_index2.png) 
### Tabela de Contatos
![contact](imgs/screenshot_contacts.png) 
### Informações do Contato
![contat data](imgs/screenshot_contact_data.png) 
### Changelog Mudanças no Contato
![changelog](imgs/screenshot_changelog.png) 
