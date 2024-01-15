import datetime
import os
import random
import bs4
import dotenv
import openai
import requests
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from pdfminer.high_level import extract_text
import meu_driver

dotenv.load_dotenv()


def read_tickers_from_txt(file: str = "tickers_monitorados.txt") -> list[str]:
    """
    Reads tickers from a text file and returns a list of tickers.
    Ignores:
        - all lines below the first line that starts with '#'
        - all lines that start with '-'
        - all lines with less than 4 characters

    Args:
        file (str): The path to the text file containing tickers.

    Returns:
        list[str]: A list of tickers extracted from the text file.
    """
    with open(file, 'r') as arq:
        tickers = arq.read().split('#')
        tickers = tickers[0].strip().upper().splitlines()
    return [x.strip() for x in tickers if (len(x.strip()) > 3 and not x.strip().startswith('-'))]


def certify_aux_folder_exists(root: str) -> None:
    """
    Verifies if the auxiliary folder exists in the specified root directory.
    If it doesn't exist, creates the folder.

    Args:
        root (str): The root directory path.

    Returns:
        None
    """
    if root not in os.listdir(os.getcwd()):
        print(f"O diretório {root} não existe. Criando...")
        os.mkdir(root)
        print()


def get_folder_size(folder_path) -> int:
    """
    Calculates the total size of a folder with its subfolders.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        int: The total size of the folder in bytes.
    """
    total = 0
    for path, _, files in os.walk(folder_path):
        for f in files:
            fp = os.path.join(path, f)
            total += os.path.getsize(fp)
    return total


def delete_negative_files_if_folder_is_huge(folder: str, huge_in_bytes: int) -> None:
    """
    Deletes "-*.pdf" files from a folder if the folder size exceeds a specified threshold.

    Args:
        folder (str): The path to the folder.
        huge_in_bytes (int): The threshold size in bytes.

    Returns:
        None
    """
    if get_folder_size(folder) > huge_in_bytes:
        print(f"O diretório {folder} está muito grande. Apagando...")
        for file in os.listdir(os.getcwd() + '/' + folder):
            if file.startswith('-'):
                os.remove(os.getcwd() + '/' + folder + '/' + file)
        print()


def get_soup(ticker: str, headless: bool = False) -> bs4.BeautifulSoup:
    """
    Retrieves the HTML content from the given URL and returns a BeautifulSoup object.

    Parameters:
    ticker (str): The ticker to fetch the HTML content from.
    headless (bool): Whether to run the browser in headless mode or not.

    Returns:
    BeautifulSoup: A BeautifulSoup object representing the parsed HTML content.
    """
    driver = meu_driver.load_driver()

    website = os.getenv("WEBSITE")
    if not website.endswith('/'):
        website += '/'
    if not website.endswith('acoes/'):
        website += 'acoes/'
    driver.get(website + ticker.lower())

    def click(seletor: str) -> None:
        """
        Clicks on an element with the given CSS selector.

        Args:
            seletor (str): The CSS selector of the element to be clicked.
        """
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, seletor)))
        driver.find_element(By.CSS_SELECTOR, seletor).click()

    # GERAL
    click("#main-2 > div.tab-nav-resume > div > div > ul > li:nth-child(2) > a")
    # Contábil
    click("#main-2 > div.tab-nav-resume > div > div > ul > li:nth-child(3) > a")
    # Comunicados
    click("#main-2 > div.tab-nav-resume > div > div > ul > li:nth-child(4) > a")

    # Espera até que a página esteja completamente carregada
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#document-section > div > div.documents.card > div.list > div:nth-child(1) > div:nth-child(3) > div > a')))
    except TimeoutException:
        raise TimeoutException("\tA lista de comunicados está vazia")

    soup = bs4.BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    return soup


def download_pdfs(soup: bs4.BeautifulSoup, ticker: str) -> list[dict[str, str]]:
    """
    Downloads PDF files from a BeautifulSoup object and returns a list of dictionaries containing information about each downloaded file.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        ticker (str): The ticker symbol of the stock.

    Returns:
        list[dict[str, str]]: A list of dictionaries, where each dictionary represents a downloaded file and contains the following keys:
            - 'title': The title of the file.
            - 'subtitle': The subtitle of the file.
            - 'date': The date of the file in the format 'yy-mm-dd'.
            - 'link': The URL link to the file.
            - 'filename': The filename of the downloaded file.
            - '_date': The date of the file as a datetime object.
    """
    sections = soup.select(
        '#document-section > div > div.documents.card > div.list > div > div > div > a')
    n = len(sections)

    print(f"\t\tForam encontrados {n} comunicados.") if n > 1 else print(
        f"\t\tFoi encontrado 1 comunicado.")

    arquivos = []
    for section in sections[::-1]:
        card = section.parent.parent.parent
        title = card.select_one('span:nth-child(1)').text.strip()
        subtitle = card.select_one('span:nth-child(2)').text.strip()
        date = card.select_one('div > div:nth-child(2)').text.strip()
        _date = datetime.datetime.strptime(date, "%d/%m/%Y")
        date = datetime.datetime.strptime(
            date, "%d/%m/%Y").strftime("%y-%m-%d")
        link = card.select_one('a')['href']

        try:
            conteudo = requests.get(link).content
            hasheando = title+date+subtitle
            core_nome = f'{date} {ticker.upper()} hash-{str(abs(hash(hasheando)))[-4:]}.pdf'
            nome_arquivo = '.aux/' + core_nome
            _nome_arquivo = '.aux/-' + core_nome
            folder = os.listdir(os.getcwd() + '/.aux')
            if (nome_arquivo not in folder) and (_nome_arquivo not in folder):
                with open(nome_arquivo, 'wb') as arq:
                    arq.write(conteudo)
            arquivos.append({
                'title': title,
                'subtitle': subtitle,
                'date': date,
                'link': link,
                'filename': nome_arquivo,
                "_date": _date
            })
        except:
            print(f"Erro ao baixar {title}")

    return arquivos


def clear_white_spaces(text: str) -> str:
    """
    Remove extra white spaces from the given text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with extra white spaces removed.
    """
    x = re.sub(r'\n\n', '\n', text)
    x = re.sub(r'\t', '\n', x)
    x = re.sub(r'\n\n', '\n', x)
    x = re.sub(r'\n', ' ', x)
    x = re.sub(r'  ', ' ', x)
    return re.sub(r'  ', ' ', x).strip()


def rename_pdf_file(current_file_path: str) -> None:
    """
    Renames a PDF file by adding a hyphen at the beginning of its name.

    Args:
        current_file_path (str): The path to the current PDF file.

    Returns:
        None
    """

    if not os.path.isfile(current_file_path):
        print("O arquivo não existe")
        return

    current_name = os.path.basename(current_file_path)
    if not current_name.endswith('.pdf'):
        new_name = '-' + current_name + '.pdf'
    else:
        new_name = '-' + current_name

    dir_name = os.path.dirname(current_file_path)
    new_path = os.path.join(dir_name, new_name)

    os.rename(current_file_path, new_path)


def resume(pdf_file_path: str, gpt4_permitted: bool = False) -> str:
    """
    Resumes the content of a PDF file by generating a summary paragraph using OpenAI's GPT-3.5 or GPT-4 model.

    Args:
        pdf_file_path (str): The path to the PDF file.
        gpt4_permitted (bool, optional): Indicates whether GPT-4 model is permitted to be used. Defaults to False.

    Returns:
        str: The generated summary paragraph.
    """
    if os.path.basename(pdf_file_path).startswith('-'):
        print('O arquivo já foi resumido antes.')
        return ''
    if not os.path.exists(pdf_file_path):
        print("Arquivo não existe!")
        return ""

    client = openai.OpenAI(api_key=os.getenv('OPENAI_KEY'))

    text = clear_white_spaces(extract_text(pdf_file_path))

    INSTRUCTION = re.sub(r'\t', '', '''

    Você está lendo o comunicado público de uma empresa para fins de estudo. Resuma o texto em um parágrafo, destacando apenas os pontos mais importantes e centrais. O resumo deve ter, no máximo, 85 palavras. O formato deve ser exatamente:
    <Título do resumo do Conteúdo>\n
    <Explicação suscinta dos tópicos importantes>.
    
    Apenas isto.
    Não coloque os símbolos < > acima no resumo. Foi apenas um placeholder.
    Insira uma dupla quebra de linha entre o título e o corpo.
    Sempre que possível, resuma os nomes das empresas.
    Resuma datas como '19 de abril de 2021' como '19/04/21'.
    Prefira usar siglas como 'RS' ao invés de 'Rio Grande do Sul'.
    
    ''').strip()

    config = {
        "max_tokens": 600,
        "frequency_penalty": 1.1
    }

    try:
        res = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': INSTRUCTION},
                {'role': 'user', 'content': text},
            ],
            model="gpt-3.5-turbo-1106",
            **config
        )
        rename_pdf_file(pdf_file_path)
        return res.choices[0].message.content
    except openai.AuthenticationError as e:
        print("Erro de autenticação. Verifique se a chave da API está correta.")
        return '-#-'
    except openai.BadRequestError as e:
        pattern = re.compile(
            r'maximum context length is ([0-9]+) tokens. However, your messages resulted in ([0-9]+) tokens.')
        lista = pattern.findall(e.message)[0]
        lista = [int(x) for x in lista]
        print(
            f'O texto tem {lista[1] - lista[0]} tokens a mais do que o permitido pro gpt3', end='')
        if not gpt4_permitted:
            print(' e o GPT4 não está permitido.')
            return ''

        print(". Usando o GPT-4...\n\n")
        res = client.chat.completions.create(
            messages=[
                {'role': 'system', 'content': INSTRUCTION},
                {'role': 'user', 'content': text},
            ],
            model="gpt-4-1106-preview",
            **config
        )
        rename_pdf_file(pdf_file_path)
        return res.choices[0].message.content


def email_me(address: str, subject="Automatic Email via Python", body="Hello"):
    """
    Sends an email using the Gmail SMTP server.

    Parameters:
    - address (str): The email address to send the email to.
    - subject (str): The subject of the email. Default is "Automatic Email via Python".
    - body (str): The body of the email. Default is "Hello".
    """
    sender = address
    recipient = sender

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = sender
    smtp_password = os.getenv("GMAIL")

    mime_multipart = MIMEMultipart()
    mime_multipart['from'] = sender
    mime_multipart['to'] = recipient
    mime_multipart["subject"] = subject

    email_body = MIMEText(body, 'plain', 'utf-8')
    mime_multipart.attach(email_body)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        # Code to send the email
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(mime_multipart)
        print("Email enviado com sucesso!")
