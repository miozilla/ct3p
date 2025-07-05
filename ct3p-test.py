import boto3
import time
import uuid

# Initialize AWS clients
polly = boto3.client('polly')
transcribe = boto3.client('transcribe')
translate = boto3.client('translate')
textract = boto3.client('textract')
comprehend = boto3.client('comprehend')
s3 = boto3.client('s3')

# Configuration
bucket_name = 's3-bucket-name'  # Replace with actual bucket name
audio_file_uri = f's3://{bucket_name}/sample.mp3'  # Ensure this file exists in your bucket
document_file_path = 'document.pdf'  # Replace with local document/image
text_to_test = "Hello, this is a test of AWS services."

# 1. Polly – Text-to-Speech
def test_polly(text):
    print("Running Polly...")
    response = polly.synthesize_speech(Text=text, OutputFormat='mp3', VoiceId='Joanna')
    with open('polly_output.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    print(" Polly: Audio saved as polly_output.mp3")

# 2. Transcribe – Speech-to-Text
def test_transcribe(job_name, media_uri):
    print("Running Transcribe...")
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat='mp3',
        LanguageCode='en-US'
    )
    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']
        if job_status in ['COMPLETED', 'FAILED']:
            break
        print(" Waiting for Transcribe job to complete...")
        time.sleep(5)
    if job_status == 'COMPLETED':
        transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        print(" Transcribe: Transcript available at", transcript_url)
    else:
        print(" Transcribe job failed.")

# 3. Translate – English to Malay
def test_translate(text, source_lang='en', target_lang='ms'):
    print("Running Translate...")
    result = translate.translate_text(Text=text, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang)
    print(f" Translate: '{text}' → '{result['TranslatedText']}'")

# 4. Textract – Extract Text from Document
def test_textract(file_path):
    print("Running Textract...")
    with open(file_path, 'rb') as doc:
        response = textract.detect_document_text(Document={'Bytes': doc.read()})
    print(" Textract: Extracted lines:")
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            print("  •", block['Text'])

# 5. Comprehend – Sentiment and Entity Detection
def test_comprehend(text):
    print("Running Comprehend...")
    sentiment = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    entities = comprehend.detect_entities(Text=text, LanguageCode='en')
    print("Comprehend:")
    print(" Sentiment:", sentiment['Sentiment'])
    print(" Entities:", [e['Text'] for e in entities['Entities']])

# Run all tests
if __name__ == "__main__":
    print("Starting AWS Services Test Suite...\n")
    test_polly(text_to_test)
    job_id = f"transcribe-job-{uuid.uuid4()}"
    test_transcribe(job_id, audio_file_uri)
    test_translate(text_to_test)
    test_textract(document_file_path)
    test_comprehend(text_to_test)
    print("\n All tests completed.")