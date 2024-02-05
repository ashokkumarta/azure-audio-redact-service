import batch_redact as _br
import sys, os

supported_redact_categories = ('Name', 'Phone', 'Address', 'Email', 'NumericIdentifier', 'CreditCard')

def usage():
    print('Usage: python run.py <input_audios_folder> <azure_container> [RedactCategory1 RedactCategory2 ...]')
    print('  (Mandatory) input_audios_folder: Folder that contains the audios to be redacted')
    print('  (Mandatory) azure_container: Azure container to use for the batch run')
    print('  (Optional)  Redact Category: Set of redact categories to apply. Applies \'CreditCard\' if this parameter(s) are NOT provided')
    print('      Supported Redact Categories: Name, Phone, Address, Email, NumericIdentifier, CreditCard')
    os._exit(-1)

def initialize():
    if (len(sys.argv) < 3):
        print('\nThe syntax of the command is incorrect\n')
        usage()

    _br.redact_categories = set()

    if (len(sys.argv) == 3):
        _br.redact_categories.add('CreditCard')
    else: 
        print('\nValidating redact categories provided\n')
        for redact_category in sys.argv[3:]:
            if(redact_category in supported_redact_categories):
                _br.redact_categories.add(redact_category)
            else:
                print('Unsupported Redact Category: %s. Skipping' % redact_category)

    if (len(_br.redact_categories) < 1):
        print('\nNone of the redact categories provided are valid\n')
        usage()

    input_audios_folder = azure_container = sys.argv[1]
    batch_id = azure_container = sys.argv[2]

    print('Redact categories to be applied: %s' % _br.redact_categories)
    print('Starting the batch run with RUN_ID: %s using AZURE_STORAGE_CONTAINER: %s' % (batch_id, azure_container))
    os.environ['INPUT_AUDIO_FOLDER'] = input_audios_folder
    os.environ['RUN_ID'] = batch_id
    os.environ['AZURE_STORAGE_CONTAINER'] = azure_container
    os.environ['TRANSCRIBED_FOLDER'] = 'transcribed'
    os.environ['REDACTION_INFO_FOLDER'] = 'redaction-info'
    os.environ['REDACTED_AUDIO_FOLDER'] = 'redacted-audio'
    os.environ['REDACTION_STATUS_FOLDER'] = 'status'

initialize()

print('\nTRANSCRIBING AUDIOS\n')
transcribed_report = _br.batch_transcribe()
##transcribed_report = get_transcribed_report('https://eastus.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions/c4554cf2-1bc6-4fc0-a177-f8b4c31cd1c2/files')

print('\nFETCHING TRANSCRIBED CONTENT\n')
_br.fetch_transcribed_files(transcribed_report)

print('\nGENERATING REDACTION INFO\n')
_br.generate_redaction_info()

print('\nGENERATING REDACTED AUDIOS\n')
_br.generate_redacted_audios()
print('\nPROCRESSING COMPLETE\n')
