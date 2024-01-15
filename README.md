# Resumidor de Comunicados B3


## Como usar

### 1. Escolha as empresas que você quer acompanhar
Escolha tickers de empresas listadas na B3.
Coloque-os num arquivo ticker_monitorados.txt no formato
```txt
petr4
vale3
b3sa3
cxse3
```

### 2. Suas credenciais
Configure seu .env no seguinte formato (não use aspas depois dos =):
```
OPENAI_KEY=
GAMIL=

EMAIL=
WEBSITE=

TXT_MONITORADO=tickers_monitorados.txt
```

onde
- GAMIL é a sua senha de app do gmail.
- EMAIL o seu email para onde o resumo será enviado.
- WEBSITE é o site em que as buscas serão feitas.