import os
import dotenv
from random import shuffle
import meu_email
import helpers
from selenium.common.exceptions import TimeoutException

ROOT = '.aux'


def main():
    """
    Função principal que executa o monitoramento de ações.

    Realiza o scrapping de informações de ações, faz o download de comunicados em PDF,
    lê e resume os PDFs usando a api da OPENAI e envia um e-mail com os resultados.

    :return: None
    """

    helpers.certify_aux_folder_exists(ROOT)
    helpers.delete_negative_files_if_folder_is_huge(ROOT, 40e6)

    tamanho_antes = round(helpers.get_folder_size(ROOT)/1e6, 2)

    print(
        f"\nTamanho da pasta antes dos arquivos: {tamanho_antes}Mb\n")

    tickers = helpers.read_tickers_from_txt(os.getenv('TXT_MONITORADO'))
    tickers_ordenados = tickers.copy()
    shuffle(tickers)

    infos = dict()
    i = 0
    for ticker in tickers:
        i += 1
        try:
            print(
                f'\n({100*i/(len(tickers)+0.01):.0f} %) Scrapping do ticker {ticker.upper()}...')
            stock = helpers.get_soup(ticker, True)

            print('\tDownload dos comunicados...')
            infos[ticker.upper()] = helpers.download_pdfs(stock, ticker)

        except TimeoutException as e:
            print(f"{e.msg}: {ticker.upper()}")

    ROOT_ = ROOT + '/'

    print("\n" + '-' * 40)
    corpo_final = ""
    tickers_lidos = set()
    for ticker in tickers_ordenados:
        if ticker not in infos:
            continue
        arquivos = infos[ticker]
        arquivos.sort(key=lambda d: d['_date'])
        _bloco_do_ticker = "\n" + '='*40 + f"\n\n\t{ticker}\n\n"
        n_arquivos_invalidos = 0
        for i, arq in enumerate(arquivos):
            link = arq['link']
            date = arq['_date'].strftime("%d/%m")
            resumo = helpers.resume(
                arq['filename'], gpt4_permitted=True).strip()
            if resumo == '-#-':
                return
            elif resumo != '':
                _bloco_do_ticker += f"({date}): "
                _bloco_do_ticker += resumo + f'\n\nPdf: {link}\n\n'
                print(ticker, date, '\n\n', resumo, end='\n\n\n')
            else:
                n_arquivos_invalidos += 1
            if i < len(arquivos)-1-n_arquivos_invalidos:
                _bloco_do_ticker += '\t\t' + '-'*20 + '\n\n'
        tickers_lidos.add(ticker)
        corpo_final += _bloco_do_ticker

    tamanho_depois = round(helpers.get_folder_size(ROOT_)/1e6, 1)
    print(
        f"\n\n\n\nTamanho da pasta depois dos arquivos: {tamanho_depois}Mb (+{round(tamanho_depois-tamanho_antes, 2)}Mb)\n")

    tickers_lidos_ordenados = []
    for t in tickers_ordenados:
        if t in tickers_lidos and t not in tickers_lidos_ordenados:
            tickers_lidos_ordenados.append(t.upper())

    if len(tickers_lidos) > 0:
        corpo_final = "Tickers lidos:\n\n" + \
            "\n".join([f"\t{i+1:2d}. {_x}" for i, _x in enumerate(tickers_lidos_ordenados)]) + \
            '\n\n' + corpo_final

        assunto = "Lidos: " + ", ".join([x[:4]
                                         for x in tickers_lidos_ordenados])
        try:
            meu_email.email_me(
                os.getenv('EMAIL'),
                assunto,
                corpo_final
            )

        except Exception as e:
            print(e)


if __name__ == '__main__':
    dotenv.load_dotenv()
    main()
