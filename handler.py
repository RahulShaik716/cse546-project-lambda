import os
import subprocess
from boto3 import client as boto3_client
import face_recognition
import pickle

dynamodb = boto3_client('dynamodb')
input_bucket = "mginputbucket4"
output_bucket = "mgoutputbucket4"
 # Initialize the S3 client
s3 = boto3_client('s3',region_name="us-west-1",aws_access_key_id="AKIAV5DKHYESU7RUN5AU",aws_secret_access_key="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")

# Function to read the 'encoding' file
def open_encoding(filename):
	file = open(filename, "rb")
	data = pickle.load(file)
	file.close()
	return data

def face_recognition_handler(event, context):	
	#  your code here*
	# Log a message to indicate the Lambda function has started
    print("Lambda function started processing.")
    try:
        # Process the S3 event records (in this case, we assume only one record)
        for record in event['Records']:
            # Extract the bucket and key from the event record
            s3_bucket = record['s3']['bucket']['name']
            s3_key = record['s3']['object']['key']

            # Define temporary paths for video and frames
            video_file_path = os.path.join(os.getcwd()+'\\tmp','input_video.mp4')
            frames_dir = os.path.join(os.getcwd()+'\\tmp','frames\\')

            # Download the video from S3
            s3.download_file(s3_bucket, s3_key, video_file_path)

            # Use ffmpeg to extract frames from the video
            subprocess.run(["ffmpeg", "-i", video_file_path, "-r", "1", f"{frames_dir}image-%3d.jpeg"])

            # Load known face encodings from an external source
            known_face_encodings = open_encoding('encoding')  # Replace with the correct path

            # Process each frame and recognize faces
            recognized_faces = []
            for frame_filename in os.listdir(frames_dir):
                frame_path = os.path.join(frames_dir, frame_filename)
                frame_image = face_recognition.load_image_file(frame_path)
                face_locations = face_recognition.face_locations(frame_image)

                if face_locations:
                    # Recognize the first detected face in the frame
                    face_encoding = face_recognition.face_encodings(frame_image, known_face_encodings)[0]
                    # Search for the recognized face in DynamoDB and get academic information
                    academic_info = search_dynamodb(face_encoding)  # Implement this function
                    recognized_faces.append(f"{academic_info['name']}, {academic_info['major']}, {academic_info['year']}")

            # Create a CSV content
            csv_content = "\n".join(recognized_faces)

            # Upload the CSV to the output S3 bucket with the video name as the file name
            output_key = s3_key.split('.')[0] + ".csv"
            s3.put_object(Bucket=output_bucket, Key=output_key, Body=csv_content)

            print("Processing completed.")

        return {
            "statusCode": 200,
            "body": "Processing complete"
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": str(e)
        }
def search_dynamodb(face_encoding):
    # Implement this function to search DynamoDB for academic information
    # Return academic information based on the recognized face
    try:
        # Convert the face_encoding to a string for use as a lookup key
        face_encoding_str = ' '.join(map(str, face_encoding))
        
        # Define the primary key for the DynamoDB table
        primary_key = {
            'face_encoding': {'S': face_encoding_str}
        }
        
        # Perform the DynamoDB lookup
        response = dynamodb.get_item(
            TableName='student_data',  # Replace with your DynamoDB table name
            Key=primary_key
        )

        # Extract academic information if the face is found
        if 'Item' in response:
            item = response['Item']
            academic_info = {
                'name': item['name']['S'],
                'major': item['major']['S'],
                'year': item['year']['S']
            }
            return academic_info
        else:
            # If face is not found, return 'Unknown' or handle as needed
            return {
                'name': 'Unknown',
                'major': 'Unknown',
                'year': 'Unknown'
            }

    except Exception as e:
        print(f"Error searching DynamoDB: {str(e)}")
        # Handle the error as needed
        # You can log the error, return a default value, or raise an exception
        return {
            'name': 'Error',
            'major': 'Error',
            'year': 'Error'
        }


