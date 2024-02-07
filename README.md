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



Permissions for Azure user
--------------------------
```
Create or get an Azure user with following permissions for a resource group
- Cognitive Services Contributor
- Cognitive Services Speech Contributor
- Storage Account Contributor 
- Storage Blob Data Contributor

TODO: Role to assign Storage Blob Data Reader to speech service on storage account
```

Azure services required
-----------------------
```
Storage account
Speech services
Language service
```

RABC permissions for Azure services 
-----------------------------------
```
Storage account
- Grant Storage Blob Data Reader access to the Speech Service

```

Scripts to upload/delete audiods to/from Azure storage
------------------------------------------------------
```
azcopy login -> to login for device authentication
copy_to_az.bat -> run it from the folder you want to upload to Azure
del_from_az.bat -> run it from the folder you want to delete from Azure
```

Configuration properties to set (Environment variables)
-------------------------------------------------------
```
AZURE_CONVERSATIONS_ENDPOINT=<language service url>
AZURE_CONVERSATIONS_KEY=<language service key>
AZURE_SPEECH_KEY=<speech service key>
AZURE_SPEECH_REGION=<speech service region>
AZURE_STORAGE_ACCOUNT=<storage account>
```

Onetime setup
-------------
```
1. Install the tools
2. Install python modules
3. Create of get an Azure user account with required permissions  
4. With this Azure user account, create the required Azure services and grant RABC permissions
5. Setup configuration properties as environment variables
```

Steps to execute each batch
---------------------------
```
1. Run azcopy from input_audios_folder to upload origional audios to Azure storage container
2. Execute redaction script using the below command

     python run.py <input_audios_folder> <azure_container> [RedactCategory1 RedactCategory2 ...]
   
   Supported Redact Categories: Name, Phone, Address, Email, NumericIdentifier, CreditCard
   Applies Redact Category: CreditCard, if no redact categories are passed in the optional parameter 
    
```

Tested on
---------
```
Windows 11, 64-bit operating system, x64-based processor / Intel(R) Core(TM) i5-10210U CPU

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
