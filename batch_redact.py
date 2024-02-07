# import libraries
import os, subprocess, shutil
import requests, json
import time, uuid
from datetime import datetime
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations import ConversationAnalysisClient

global redact_categories

FFMPEG_CMD_TPL = "ffmpeg -hide_banner -loglevel error -i \"{input_audio_file}\" -filter_complex \"[0]volume=0:enable=' {pii_section} '[main];sine=f=800,pan=stereo|FL=c0|FR=c0,volume=0:enable='{nonpii_section}'[beep];[main][beep]amix=inputs=2:duration=first\" {output_audio_file} -y"
FFPROBE_CMD_TPL = 'ffprobe -i {file_name} -show_entries format=duration -v quiet -of csv="p=0"'

def secs(ticks):
    return ticks / 10000000

def get_env(name, folder=True):
    if(folder):
        return os.path.join(os.environ.get(name),os.environ.get('RUN_ID'))
    return os.environ.get(name)

def get_batch_transcribe_status(batch_transcribe_url):
    batch_transcribe_status_headers = {
            'Ocp-Apim-Subscription-Key': get_env('AZURE_SPEECH_KEY', False),
        }
    batch_status_response = requests.get(batch_transcribe_url, headers = batch_transcribe_status_headers)
    return batch_status_response.json().get('status')

def get_transcribed_report(transcribed_report_url):
    batch_transcribe_status_headers = {
            'Ocp-Apim-Subscription-Key': get_env('AZURE_SPEECH_KEY', False),
        }
    batch_status_response = requests.get(transcribed_report_url, headers = batch_transcribe_status_headers)
    return batch_status_response.json()

def get_file(file_url):
    response = requests.get(file_url)
    return response.json()

def get_audio_duration(file_name):
    ffprobe_cmd = FFPROBE_CMD_TPL.replace('{file_name}',file_name)
    return str(round(float(subprocess.getoutput(ffprobe_cmd)),2))

def init_status_file():
    status_file = get_env('REDACTION_STATUS_FOLDER') + '-redaction-details.csv'
    os.makedirs(os.path.dirname(status_file), exist_ok=True)
    with open(status_file, "w") as f:
        f.write('Source File,Duration(secs),Status,PII Action,Target File\n')

def write_summary():
    summary_file = get_env('REDACTION_STATUS_FOLDER') + '-run-summary.rpt'
    with open(summary_file, "a") as f:
        f.write('\n')
        f.write('Run at: '+datetime.today().isoformat()+'\n')
        f.write('INPUT_AUDIOS_FOLDER: '+os.environ['INPUT_AUDIOS_FOLDER']+'\n')
        f.write('RUN_ID: '+os.environ['RUN_ID']+'\n')
        f.write('AZURE_STORAGE_CONTAINER: '+os.environ['AZURE_STORAGE_CONTAINER']+'\n')
        f.write('TRANSCRIBED_FOLDER: '+os.environ['TRANSCRIBED_FOLDER']+'\n')
        f.write('REDACTION_INFO_FOLDER: '+os.environ['REDACTION_INFO_FOLDER']+'\n')
        f.write('REDACTED_AUDIO_FOLDER: '+os.environ['REDACTED_AUDIO_FOLDER']+'\n')
        f.write('REDACTION_STATUS_FOLDER: '+os.environ['REDACTION_STATUS_FOLDER']+'\n')
        f.write('Redaction Categories Applied: '+str(redact_categories)+'\n')
        f.write('Run status: Success\n')

def write_status(source_file_name, status):
    target_file_name = source_file_name.replace(get_env('INPUT_AUDIOS_FOLDER'), get_env('REDACTED_AUDIO_FOLDER'))
    duration = get_audio_duration(source_file_name)
    status_file = get_env('REDACTION_STATUS_FOLDER') + '-redaction-details.csv'
    with open(status_file, "a") as f:
        f.write(source_file_name + ',' + duration + ',' + 'Processed' + ',' + status + ',' + target_file_name  +'\n')


def write_transcribed_files(file_name, transcribed_content):
    output_file = file_name.replace(get_env('AZURE_STORAGE_CONTAINER', False), get_env('TRANSCRIBED_FOLDER'))
    print('Writing transcribed content to %s' % (output_file))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(json.dumps(transcribed_content))

def write_redaction_info_files(file_name, redaction_info_content):
    output_file = file_name.replace(get_env('TRANSCRIBED_FOLDER'), get_env('REDACTION_INFO_FOLDER'))
    print('Writing redaction info to: %s' % (output_file))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w") as f:
        f.write(json.dumps(redaction_info_content))

def batch_transcribe():
    print('Initializing SPEECH TO TEXT Batch Transcription')
    speech_svc_url = 'https://'+get_env('AZURE_SPEECH_REGION', False)+'.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions'
    print('Service URL initialized to: '+speech_svc_url)
    speech_svc_payload = str({
        'contentContainerUrl': 'https://'+get_env('AZURE_STORAGE_ACCOUNT', False)+'.blob.core.windows.net/'+get_env('AZURE_STORAGE_CONTAINER', False),
        'locale': 'en-US',
        'displayName': 'Redact Run '+str(round(time.time()*1000)),
        'properties': {
            'wordLevelTimestampsEnabled': 'true',
        },
    })
    print('Payload initialized to: '+speech_svc_payload)
    speech_svc_headers = {
            'Ocp-Apim-Subscription-Key': get_env('AZURE_SPEECH_KEY', False),
            'Content-Type': 'application/json',
        }
    print('Headers initialized to: '+str(speech_svc_headers))

    print('Triggering SPEECH TO TEXT Batch Transcription')
    batch_response = requests.post(speech_svc_url, data = speech_svc_payload, headers = speech_svc_headers)
    print('Response: \n')
    print(batch_response.text)
    batch_status = batch_response.json().get('status')
    print('\nTranscription status: '+batch_status)
    while(batch_status in ('NotStarted','Running')):
        batch_status = get_batch_transcribe_status(batch_response.json().get('self'))
        print('Transcription status: '+batch_status)
        time.sleep(2)
    if(batch_status in ('Failed')):
        print('Audio transcription failed. Exiting')
        os._exit(-1)
    transcribed_report_url = batch_response.json().get('links').get('files')
    transcribed_report = get_transcribed_report(transcribed_report_url)
    print('Transcribed output files: \n'+str(transcribed_report))
    return transcribed_report

def fetch_transcribed_files(transcribed_report): 
    output_values = transcribed_report['values']
    for val in output_values:
        kind = val['kind']
        if(kind == 'Transcription'):
            file_name = val['name']
            content_url = val['links']['contentUrl']
            print('Fetching Transcribed output for: '+file_name)
            transcribed_content = get_file(content_url)
            write_transcribed_files(file_name, transcribed_content)
            print('Done\n')

def create_conversation_items(recognized_phrases):
    conversation_items = []
    for phrase in recognized_phrases:
        participantId = 'agent_' + str(phrase['channel'])
        id = str(uuid.uuid1())
        phrase_item = phrase['nBest'][0]
        conversation_item = {}
        conversation_item['participantId'] = participantId
        conversation_item['id'] = id
        conversation_item['text'] = phrase_item['display']
        conversation_item['lexical'] = phrase_item['lexical']
        conversation_item['itn'] = phrase_item['itn']
        conversation_item['maskedItn'] = phrase_item['maskedITN']
        audioTimings = []
        for word in phrase_item['words']:
            audio_word = {}
            audio_word['word'] = word['word']
            audio_word['offset'] = word['offsetInTicks']
            audio_word['duration'] = word['durationInTicks']
            audioTimings.append(audio_word)
        conversation_item['audioTimings'] = audioTimings
        conversation_items.append(conversation_item)
    return conversation_items

def create_language_service_payload(transcribed_content_json):
    print('Applying Redact categories: %s' % redact_categories)
    lang_payload = {
            'displayName': 'Redact PII run'+str(round(time.time()*1000)),
            'analysisInput': {
                'conversations': [
                    {
                        'id': '23611680-c4eb-4705-adef-4aa1c17507b5',
                        'language': 'en',
                        'modality': 'transcript',
                    }
                ]
            },
            'tasks': [
                {
                    'taskName': 'Redact PII run '+str(round(time.time()*1000)),
                    'kind': 'ConversationalPIITask',
                    'parameters': {
                        'modelVersion': '2022-05-15-preview',
                        'redactionSource': 'text',
                        'includeAudioRedaction': True,
                        'piiCategories': list(redact_categories)
                    }
                }
            ]
        }
    conversation_items = create_conversation_items(transcribed_content_json['recognizedPhrases'])
    lang_payload['analysisInput']['conversations'][0]['conversationItems'] = conversation_items
    return lang_payload

def generate_redact_info_using_language_service(language_service_payload):
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_KEY"]
    # analyze query
    client = ConversationAnalysisClient(endpoint, AzureKeyCredential(key))
    with client:
        poller = client.begin_conversation_analysis(
            task=language_service_payload
        )
        # view result
        result = poller.result()
        task_result = result["tasks"]["items"][0]
        print("Status: {}".format(task_result["status"]))
        conv_pii_result = task_result["results"]
        if conv_pii_result["errors"]:
            print("... errors occured ...")
            for error in conv_pii_result["errors"]:
                print(error)
        else:
            conversation_result = conv_pii_result["conversations"][0]
            if conversation_result["warnings"]:
                print("... view warnings ...")
                for warning in conversation_result["warnings"]:
                    print(warning)
            else:
                return conversation_result

def generate_redaction_info():
    for path, subdirs, files in os.walk(get_env('TRANSCRIBED_FOLDER')):
        for name in files:
            transcribed_file_name = os.path.join(path, name)
            print('Generating redaction info for: %s' % transcribed_file_name)
            f = open(transcribed_file_name, "r")
            transcribed_content = f.read()
            transcribed_content_json = json.loads(transcribed_content)
            language_service_payload = create_language_service_payload(transcribed_content_json)
            redaction_info_response = generate_redact_info_using_language_service(language_service_payload)
            if(redaction_info_response):
                write_redaction_info_files(transcribed_file_name, redaction_info_response)
            print('Done\n')
    print('Redaction info processing for all files complete')

def get_input_audio_file(redact_info_file):
    return redact_info_file.rstrip(".json").replace(get_env('REDACTION_INFO_FOLDER'), get_env('INPUT_AUDIOS_FOLDER'))

def copy_file(redact_info_file):
    input_audio_file = get_input_audio_file(redact_info_file)
    output_audio_file = input_audio_file.replace(get_env('INPUT_AUDIOS_FOLDER'), get_env('REDACTED_AUDIO_FOLDER'))
    os.makedirs(os.path.dirname(output_audio_file), exist_ok=True)
    shutil.copy(input_audio_file, output_audio_file)

def redact_audio(redact_info_file, pii_section, nonpii_section):

    input_audio_file = get_input_audio_file(redact_info_file)
    output_audio_file = input_audio_file.replace(get_env('INPUT_AUDIOS_FOLDER'), get_env('REDACTED_AUDIO_FOLDER'))

    ffmpeg_cmd = FFMPEG_CMD_TPL.replace('{input_audio_file}',input_audio_file)
    ffmpeg_cmd = ffmpeg_cmd.replace('{pii_section}',pii_section)
    ffmpeg_cmd = ffmpeg_cmd.replace('{nonpii_section}',nonpii_section)
    ffmpeg_cmd = ffmpeg_cmd.replace('{output_audio_file}',output_audio_file)
    
    output_audio_parent_path = Path(output_audio_file).parent
    print('Checking & creating output folder path: ',output_audio_parent_path)
    output_audio_parent_path.mkdir(parents=True, exist_ok=True)

    print('\nGenerating redacted audio for: ',input_audio_file)
    print('Using ffmpeg command: \n',ffmpeg_cmd)
    print('Executing FFMPEG process')
    os.system(ffmpeg_cmd)
    print('FFMPEG process complete')
    print('Redacted audio stored at: ',output_audio_file)

def append_ffmpeg_time_segment(section, start, end):
    if(section):
        section = section + "+between(t,"+str(start)+","+str(end)+")"
    else:
        section ="between(t,"+str(start)+","+str(end)+")"
    return section

def create_ffmpeg_pii_sections(redact_info_content_json):

    pii_section = ''
    nonpii_section = ''

    nonpii_start = 0
    for conversationItem in redact_info_content_json['conversationItems']:
        for redactedAudioTiming in conversationItem['redactedContent']['redactedAudioTimings']:
            pii_start = secs(redactedAudioTiming['offset'])
            pii_end = pii_start + secs(redactedAudioTiming['duration'])
            nonpii_end = pii_start
            pii_section = append_ffmpeg_time_segment(pii_section, pii_start, pii_end)
            nonpii_section = append_ffmpeg_time_segment(nonpii_section, nonpii_start, nonpii_end)
            nonpii_start = pii_end
    if(pii_section):    
        nonpii_end = 360000
        nonpii_section = append_ffmpeg_time_segment(nonpii_section, nonpii_start, nonpii_end)
        return pii_section, nonpii_section
    return None, None

def generate_redacted_audios():
    init_status_file()
    for path, subdirs, files in os.walk(get_env('REDACTION_INFO_FOLDER')):
        for name in files:
            redact_info_file_name = os.path.join(path, name)
            print('\nProcessing: %s' % redact_info_file_name)
            f = open(redact_info_file_name, "r")
            redact_info_content = f.read()
            redact_info_content_json = json.loads(redact_info_content)
            pii_section, nonpii_section = create_ffmpeg_pii_sections(redact_info_content_json)
            if(pii_section):
                redact_audio(redact_info_file_name, pii_section, nonpii_section)
                print('Completed redaction for: ', get_input_audio_file(redact_info_file_name))
                write_status(get_input_audio_file(redact_info_file_name), 'Redaction done')
            else:
                print('No PII found', redact_info_file_name)
                print('Skipping redaction for: ', get_input_audio_file(redact_info_file_name))
                copy_file(redact_info_file_name)
                write_status(get_input_audio_file(redact_info_file_name), 'No PII')
    write_summary()