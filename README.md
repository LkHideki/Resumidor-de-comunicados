# Resumidor de comunicados B3

Já pensou em como é trabalhoso ficar lendo todos os comunicados das empresas listadas na B3 que você segue e gosta?

E se você pudesse receber no seu email um resumo desses comunicados de um jeito curtinho e com a referência para download?

A solução chegou!

**Limitação: No momento, funciona em apenas um site (e isso não será um problema).**


## Como usar

Primeiro, certifique-se de ter:
1. Uma chave para usar a api da OpenAI (que usaremos para resumir os textos);
2. Uma "senha de app" na sua conta Google (que usaremos para mandar o resumo por email).

A *senha de app* é um recurso da conta google que serve para você logar em serviços que não suportam verificação em duas etapas. É como uma chave de api, mas que substitui a sua senha.

Você pode gerar uma assim:
1. Acesse sua conta Google em um navegador.
2. Vá para a seção de segurança da sua conta.
3. Procure a opção "Senhas de app" ou algo semelhante.
4. Se você tiver a verificação em duas etapas ativada, você poderá selecionar a opção para gerar uma senha de app.
5. Escolha o tipo de aplicativo e dispositivo para o qual você precisa da senha.
6. Depois de selecionar, o Google irá gerar uma senha de 16 dígitos. Esta é a senha de app.

### 0. A estrutura da pasta
A raiz deve estar assim:
```
/
  .gitignore
  README.md
  helpers.py
  main.py
  meu_driver.py
  req.txt
  testes.py
```

Crie um ambiente virtual, ative-o e instale as dependências listadas no **req.txt** com
```bash
pip install -r requirements.txt
```


### 1. Escolha as empresas que você quer acompanhar
Escolha tickers de empresas listadas na B3.
Coloque-os num arquivo tickers_monitorados.txt no formato
```txt
petr4
vale3
b3sa3
cxse3
```
(Isto não é uma recomendação de investimento.)

### 2. Suas credenciais
Configure seu .env no seguinte formato (não use aspas depois dos =):
```
OPENAI_KEY=
GMAIL=

EMAIL=
WEBSITE=

TXT_MONITORADO=tickers_monitorados.txt
```

onde
- GMAIL é a sua *senha de app*.
- EMAIL o seu email para onde o resumo será enviado.
- WEBSITE é o site em que as buscas serão feitas.

### 3. Antes de rodar
Sua estrutura deve incluir estes dois novos arquivos já editados:
```
/
  .env
  tickers_monitorados.txt

  ...e os outros itens já mencionados antes
```

### 4. Para rodar
**Com o ambiente virtual ativo**, basta rodar o arquivo main.py
```bash
python3 main.py
```
Você pode acompanhar o andamento da execução pela ocupação da pasta .aux e pelo terminal que está rodando o programa.

#### Observação (caso tenha problemas na execução)
O programa roda um driver do selenium pra fazer o scrap (por default é o Firefox). Se você tiver algum problema para carregar o driver de modo que precise selecionar outro browser, faça-o no arquivo *meu_driver.py* de modo a alterar a variável `driver` de dentro da função. Não se esqueça de atualizar os imports e de atualizar a `options` também.


### 5. Depois de rodar

Uma pasta *.aux* será criada na raiz para guardar os pdfs baixados.

A nomenclatura dos pdfs segue:
- Arquivos iniciados com a data ainda não foram lidos.
- Arquivos iniciados com "-" já foram lidos e resumidos.

**O email com o resumo só será enviado depois que todo o fluxo for bem sucedido.**

Se a pasta .aux ficar muito pesada, exclua sem dó. Tem uma função no helpers.py que eu preparei para isso, mas decidi não colocar no fluxo do main.