# azure-audio-redact-service
Service to redact PII information from audio files

Tools to install
----------------
```
python3
azcopy
ffmpeg
```

Python modules
--------------
```
pip install azure-cognitiveservices-speech
pip install azure-ai-language-conversations==1.1.0b2
```

Azure Permissions required
--------------------------
```
Cognitive Services Contributor
Cognitive Services Speech Contributor
Storage Account Contributor 
Storage Blob Data Contributor
TODO: Role to assign Storage Blob Data Reader to speed service on storage account
```

Azure services used
-------------------
```
Storage account
Speech service
Language
```

Assign RABC for Azure services 
-------------------
```
Storage account
- TODO: Permissions to assign

Speech service
- TODO: Permissions to assign

Language
- TODO: Permissions to assign

```

Scripts to copy/delete folder to/from Azure storage
---------------------------------------------------
```
azcopy login -> to login for device authentication
copy_to_az.bat
del_from_az.bat
```

Configuration properties to set (Environment variables)
-------------------------------------------------------
```
AZURE_CONVERSATIONS_ENDPOINT=<language service url>
AZURE_CONVERSATIONS_KEY=<language service key>
AZURE_SPEECH_KEY=<speech service key>
AZURE_SPEECH_REGION=<speech service region>
AZURE_STORAGE_ACCOUNT=<storage account>
AZURE_STORAGE_CONTAINER=<container to use>
#TODO: Remove these and move required attributes to command line
INPUT_AUDIO_FOLDER=<origional audios folder>
TRANSCRIBED_FOLDER=<transcribed content folder>
REDACTION_INFO_FOLDER=<redaction info content folder>
REDACTED_AUDIO_FOLDER=<redacted output audios folder>
REDACTION_STATUS_FOLDER=<status reports folder>
```

Onetime setup
-------------
```
Install the tools
Install python modules
Setup Azure account with required permissions  
With this Azure account, create required Azure services and grant RABC permissions
Setup configuration properties as environment variables
```

Steps to execute each batch
---------------------------
```
Run azcopy from INPUT_AUDIO_FOLDER to upload origional audios to Azure storage container
Execute redaction script
    
    python run.py <azure_container> [Redact Category] [Redact Category] ... 

Supported Redact Categories: Name, Phone, Address, Email, NumericIdentifier, CreditCard
By default applies Redact Category: CreditCard, which can be overridden by passing the redact categories to be applied as optional parameters 
    
```

References
---------------------------
```
https://learn.microsoft.com/en-us/azure/ai-services/speech-service/batch-transcription-create?pivots=speech-cli
https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/overview
https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/how-to-call-for-conversations?tabs=client-libraries
https://learn.microsoft.com/en-us/python/api/overview/azure/ai-textanalytics-readme?view=azure-python&viewFallbackFrom=azure-python-preview&preserve-view=true
https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/textanalytics/azure-ai-textanalytics/samples
https://learn.microsoft.com/en-us/azure/ai-services/language-service/personally-identifiable-information/concepts/conversations-entity-categories
https://www.reddit.com/r/ffmpeg/comments/r0at91/beeping_out_portions_of_an_audio_file_using_ffmpeg/

```
