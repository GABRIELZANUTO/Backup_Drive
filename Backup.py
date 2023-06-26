import subprocess,datetime,configparser,os,glob,time
import xml.etree.ElementTree as ET
import win32security
import win32api
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload

#Função de Backup usando o metodo MYSQLDUMP orientado com as informações do .ini
def backup(diretorio,pasta_bin,pasta_destino,nome,data_atual,usuario,senha,porta,tabela):
    nome = f"{nome}_{data_atual}.sql" #Monta o nome do arquivos de Backup
    comandos = [
        f'cd {diretorio}',
        f'cd {pasta_bin}',
        f'mysqldump -u{usuario} -p{senha} -P{porta} {tabela} > {pasta_destino}\{nome}',
        'exit'
    ]
    return comandos,nome

#Função que envia o arquivo para determinada pasta dentro do google drive
def envia_arquivo(file_path,pasta_nuvem):
    credentials = Credentials.from_service_account_info(
        CRE,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    drive_service = build('drive', 'v3', credentials=credentials)
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [pasta_nuvem]
    }
    media = MediaFileUpload(file_path, resumable=True)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

#Função que pesquisa pelo nome se existe algum backup com o mesmo nome naquela pasta
def pesquisa_arquivo(file_initials,pasta_nuvem):
    credentials = Credentials.from_service_account_info(
        CRE,
        scopes=['https://www.googleapis.com/auth/drive'])
    drive_service = build('drive', 'v3', credentials=credentials)
    query = f"name contains '{file_initials}' and '{pasta_nuvem}' in parents"
    fields = 'files(id, name)'
    results = drive_service.files().list(q=query, fields=fields).execute()
    files = results.get('files', [])
    '''
    Se achar algum arquivo pelo nome, ele retorna uma lista com todos
    Coloquei uma limitação pra só ser valido se retornar 1 arquivo
    Para caso de erro na pesquisa do google drive e não apague arquivos sem querer
    '''
    if len(files) == 1:
      return files
    #Caso não tenho nenhum retorna false
    else:
      return False

#Função responsável por excluir o arquivo que foi encontrado na pesquisa dentro da pasta do Drive    
def exclui_drive(arquivo_id,pasta_nuvem):
  credenciais_path = Credentials.from_service_account_info(
  CRE,
  scopes=['https://www.googleapis.com/auth/drive']
    )
  service = build('drive', 'v3', credentials=credenciais_path)
  service.files().update(fileId=arquivo_id, removeParents=pasta_nuvem).execute()
'''
Função para criar o XML que vai ser usado na crição da tarefa do AGENDADOR DE TAREFAS DO WINDOWS
Essa tarefa é programada para ser exeutada 1 vez por mês, sempre no dia que foi feito o primeiro Backcup
Sendo programada para abrir o executavel dentro do contexto da pasta em que está o .ini
'''
def criar_xml(hostname,diretorio_atual,sid):
    data = datetime.datetime.now().strftime("%Y-%m-%d")
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    dia = datetime.datetime.now().strftime("%d")
    # Criação do elemento raiz
    root = ET.Element("Task")
    root.attrib["version"] = "1.4"
    root.attrib["xmlns"] = "http://schemas.microsoft.com/windows/2004/02/mit/task"

    # Criação dos elementos filhos e suas respectivas tags e valores
    registration_info = ET.SubElement(root, "RegistrationInfo")
    date = ET.SubElement(registration_info, "Date")
    date.text = f"{data}T{hora}.2708586"
    author = ET.SubElement(registration_info, "Author")
    author.text = f"{hostname}"
    description = ET.SubElement(registration_info, "Description")
    description.text = ""
    uri = ET.SubElement(registration_info, "URI")
    uri.text = ""
    triggers = ET.SubElement(root, "Triggers")
    calendar_trigger = ET.SubElement(triggers, "CalendarTrigger")
    start_boundary = ET.SubElement(calendar_trigger, "StartBoundary")
    start_boundary.text = f"{data}T{hora}"
    enabled = ET.SubElement(calendar_trigger, "Enabled")
    enabled.text = "true"
    schedule_by_month = ET.SubElement(calendar_trigger, "ScheduleByMonth")
    days_of_month = ET.SubElement(schedule_by_month, "DaysOfMonth")
    day = ET.SubElement(days_of_month, "Day")
    day.text = f"{dia}"
    months = ET.SubElement(schedule_by_month, "Months")
    for month in ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]:
        month_element = ET.SubElement(months, month)
    principals = ET.SubElement(root, "Principals")
    principal = ET.SubElement(principals, "Principal")
    principal.attrib["id"] = "Author"
    user_id = ET.SubElement(principal, "UserId")
    user_id.text = f"{sid}"
    logon_type = ET.SubElement(principal, "LogonType")
    logon_type.text = "S4U"
    run_level = ET.SubElement(principal, "RunLevel")
    run_level.text = "HighestAvailable"
    settings = ET.SubElement(root, "Settings")
    multiple_instances_policy = ET.SubElement(settings, "MultipleInstancesPolicy")
    multiple_instances_policy.text = "IgnoreNew"
    disallow_start_if_on_batteries = ET.SubElement(settings, "DisallowStartIfOnBatteries")
    disallow_start_if_on_batteries.text = "true"
    stop_if_going_on_batteries = ET.SubElement(settings, "StopIfGoingOnBatteries")
    stop_if_going_on_batteries.text = "true"
    allow_hard_terminate = ET.SubElement(settings, "AllowHardTerminate")
    allow_hard_terminate.text = "true"
    start_when_available = ET.SubElement(settings, "StartWhenAvailable")
    start_when_available.text = "false"
    run_only_if_network_available = ET.SubElement(settings, "RunOnlyIfNetworkAvailable")
    run_only_if_network_available.text = "false"
    idle_settings = ET.SubElement(settings, "IdleSettings")
    stop_on_idle_end = ET.SubElement(idle_settings, "StopOnIdleEnd")
    stop_on_idle_end.text = "true"
    restart_on_idle = ET.SubElement(idle_settings, "RestartOnIdle")
    restart_on_idle.text = "false"
    allow_start_on_demand = ET.SubElement(settings, "AllowStartOnDemand")
    allow_start_on_demand.text = "true"
    enabled = ET.SubElement(settings, "Enabled")
    enabled.text = "true"
    hidden = ET.SubElement(settings, "Hidden")
    hidden.text = "false"
    run_only_if_idle = ET.SubElement(settings, "RunOnlyIfIdle")
    run_only_if_idle.text = "false"
    disallow_start_on_remote_app_session = ET.SubElement(settings, "DisallowStartOnRemoteAppSession")
    disallow_start_on_remote_app_session.text = "false"
    use_unified_scheduling_engine = ET.SubElement(settings, "UseUnifiedSchedulingEngine")
    use_unified_scheduling_engine.text = "true"
    wake_to_run = ET.SubElement(settings, "WakeToRun")
    wake_to_run.text = "false"
    execution_time_limit = ET.SubElement(settings, "ExecutionTimeLimit")
    execution_time_limit.text = "PT1H"
    priority = ET.SubElement(settings, "Priority")
    priority.text = "7"
    actions = ET.SubElement(root, "Actions")
    actions.attrib["Context"] = "Author"
    exec_element = ET.SubElement(actions, "Exec")
    command = ET.SubElement(exec_element, "Command")
    command.text = fr"{diretorio_atual}\Backup.exe"
    arguments = ET.SubElement(exec_element, "Arguments")
    arguments.text = ""
    working_directory = ET.SubElement(exec_element, "WorkingDirectory")
    working_directory.text = fr'{diretorio_atual}'

    tree = ET.ElementTree(root)
    tree.write("backupagenda.xml", encoding="UTF-16", xml_declaration=True)

'''
Função responsável por executar o comando no cmd para cirar a tarefa do agendador de tarefas do windows
Só irá funcionar se for executado como Adminstrador do Windows
'''
def criar_tarefa(diretorio_atual):
  time.sleep(10) #Sleep de 10 segundos para criar o xml corretamernte
  comando_agenda = f'schtasks /CREATE /TN "Backup"  /XML {diretorio_atual}\\backupagenda.xml' #Monta o comando
  subprocess.run(comando_agenda, shell=True) #Executa no cmd
  

#----------------INICIO DA EXECUÇÃO  --------------------

data_atual = datetime.datetime.now().strftime("%Y%m%d") #Data do dia
hostname = win32api.GetUserNameEx(win32api.NameSamCompatible) #Nome do computador que vai ser executada para o xml
sid = win32security.ConvertSidToStringSid(win32security.LookupAccountName(None, hostname)[0]) #SID do usuario logado no windows para o xml
diretorio_atual = os.getcwd()

#Retirando informações do .ini
config = configparser.ConfigParser()
config.read('Backup.ini')
diretorio = config.get("CONFIG","DIRETORIO")
pasta_bin = config.get("CONFIG","PASTA_BIN")
pasta_destino = config.get("CONFIG","PASTA_DESTINO")
pasta_nuvem = config.get("CONFIG","PASTA_NUVEM")
nome = config.get("CONFIG","NOME")
tabela = config.get("CONFIG","TABELA")
usuario = config.get("CONFIG","USUARIO")
senha = config.get("CONFIG","SENHA")
porta = config.get("CONFIG","PORTA")
agendador = config.get("VALIDACAO","AGENDADOR")

'''
Verificação se é a primeira vez que o programa está sendo executado
Se for ele vai criar a tarefa no Agendador 
'''
if agendador == "0":
  criar_xml(hostname,diretorio_atual,sid) #Cria o XML
  criar_tarefa(diretorio_atual) 
  time.sleep(10)
  caminho_arquivo = fr"{diretorio_atual}\backupagenda.xml" 
  os.remove(caminho_arquivo) #Remove xml usado para criar a tarefa no agendador
  config.set('VALIDACAO', 'AGENDADOR', '1') #Altera status do agendador do .ini para 1
  with open('Backup.ini', 'w') as configfile:
    config.write(configfile)

#Exclui o arquivo antigo de backup na pasta destino
arquivos_econtrados = glob.glob(f"{pasta_destino}/*.sql")
if arquivos_econtrados:
    for arquivo in arquivos_econtrados:
       os.remove(arquivo)

comandos,nome = backup(diretorio,pasta_bin,pasta_destino,nome,data_atual,usuario,senha,porta,tabela)#Passa as informações para montar os comandos do backup
comando_tudo = ' && '.join(comandos) #Junta todos os comandos
subprocess.run(comando_tudo, shell=True) #Abre o CMD e realiza os comandos para geração do arquivo de Backup
verifica = pesquisa_arquivo(nome,pasta_nuvem) #Chama a função de verificação do backup
local_backup = fr"{pasta_destino}\{nome}" #Monta o caminho do arquivo de backup
if verifica is False:
   envia_arquivo(local_backup,pasta_nuvem) #Sobe o arquivo para o drive
else:
  for i in verifica:
    exclui_drive(i['id'],pasta_nuvem) #Exclui arquivo com o mesmo nome do drive
  envia_arquivo(local_backup,pasta_nuvem) #Sobe o novo arquivo

  
 