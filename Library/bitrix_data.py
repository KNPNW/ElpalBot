import requests
import sys
import ssl
import os
import shutil

workdir = os.getcwd()[:-7]
try:
    sys.path.insert(0, workdir + 'Data')
    from setings import log_bit, pas_bit
except:
    workdir = "..\\"
    sys.path.insert(0, workdir + "Data")
    from setings import log_bit, pas_bit


ssl._create_default_https_context = ssl._create_unverified_context
url_param = "https://elpal.bitrix24.ru/rest/1/qpl8f6ouvlzs2l0m/"
url = "https://elpal.bitrix24.ru"


def file_from_bitrix(contract, id):
    method_name = "crm.deal.list"
    params = {
        "filter[=ID]": "{}".format(contract),
        "select[3]": "UF_CRM_1597049284"
    }
    response = requests.post(url_param + method_name, params)
    result = response.json()
    result = result['result']
    print(result)
    result = result[0]['UF_CRM_1597049284']
    if len(result) == 0:
        return
    files = []
    for file in result:
        files.append(file['downloadUrl'])
    if os.path.isdir(workdir+'/Output/cache/{}'.format(id)):
        shutil.rmtree(workdir+'/Output/cache/{}'.format(id))
    os.mkdir(workdir+'/Output/cache/{}'.format(id))
    for i in range(len(files)):
        s = requests.Session()
        response = s.get('https://elpal.bitrix24.ru' + files[i], auth=(log_bit, pas_bit), stream=True)
        format_file = response.headers['content-type'].split('/')[-1]
        if format_file == 'vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            format_file = 'xlsx'
        if format_file == 'vnd.openxmlformats-officedocument.wordprocessingml.document':
            format_file = 'docx'
        with open(workdir + '/Output/cache/{}/{}.{}'.format(id, 'Файл_' + str(i + 1), format_file), 'wb') as f:
            f.write(response.content)
    return 1
