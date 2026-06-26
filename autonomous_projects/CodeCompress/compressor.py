from typing import List
import arithmetic_coder
import byte_predictor

def compress_file(input_path: str, output_path: str) -> None:
    """
    Compress the file at input_path and write the compressed data to output_path.
    
    :param input_path: The path to the file to be compressed.
    :param output_path: The path where the compressed data will be written.
    """
    try:
        with open(input_path, 'rb') as infile:
            data = infile.read()
        
        # Initialize probabilities for each symbol (byte)
        probabilities = [1 / 256] * 256
        
        # Predict next byte and update probabilities
        predicted_data = bytearray()
        for i in range(len(data)):
            if i > 0:
                prediction = byte_predictor.predict_next_byte(predicted_data)
                probabilities[prediction] += 1
            predicted_data.append(data[i])
        
        # Normalize probabilities
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        # Encode the data
        encoded_data = arithmetic_coder.encode(bytes(predicted_data), probabilities)
        
        # Write the compressed data to the output file
        with open(output_path, 'wb') as outfile:
            outfile.write(encoded_data)
    except Exception as e:
        print(f"An error occurred: {e}")

def decompress_file(input_path: str, output_path: str, length: int) -> None:
    """
    Decompress the file at input_path and write the decompressed data to output_path.
    
    :param input_path: The path to the compressed file.
    :param output_path: The path where the decompressed data will be written.
    :param length: The length of the original message.
    """
    try:
        with open(input_path, 'rb') as infile:
            encoded_data = infile.read()
        
        # Initialize probabilities for each symbol (byte)
        probabilities = [1 / 256] * 256
        
        # Decode the data
        decoded_data = arithmetic_coder.decode(encoded_data, length, probabilities)
        
        # Write the decompressed data to the output file
        with open(output_path, 'wb') as outfile:
            outfile.write(decoded_data)
    except Exception as e:
        print(f"An error occurred: {e}")