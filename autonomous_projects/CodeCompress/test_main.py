import unittest
from arithmetic_coder import cumulative_distribution, find_interval, encode, decode
from byte_predictor import predict_next_byte
from compressor import compress_file, decompress_file
import os
import tempfile

class TestArithmeticCoder(unittest.TestCase):
    def test_cumulative_distribution(self):
        probabilities = [0.1, 0.2, 0.3, 0.4]
        expected = [0.1, 0.30000000000000004, 0.6000000000000001, 1.0]
        self.assertEqual(cumulative_distribution(probabilities), expected)

    def test_find_interval(self):
        cumulative = [0.1, 0.3, 0.6, 1.0]
        self.assertEqual(find_interval(0.25, cumulative), 1)
        self.assertEqual(find_interval(0.7, cumulative), 3)

    def test_encode_decode(self):
        message = b'hello'
        probabilities = [1 / 256] * 256
        encoded = encode(message, probabilities)
        decoded = decode(encoded, len(message), probabilities)
        self.assertEqual(decoded, message)

class TestBytePredictor(unittest.TestCase):
    def test_predict_next_byte(self):
        data = b'hello world'
        prediction = predict_next_byte(data)
        self.assertIsInstance(prediction, int)
        self.assertGreaterEqual(prediction, 0)
        self.assertLessEqual(prediction, 255)

class TestCompressor(unittest.TestCase):
    def setUp(self):
        self.input_path = 'test_input.txt'
        self.output_path = 'test_output.bin'
        self.decompressed_path = 'test_decompressed.txt'
        with open(self.input_path, 'wb') as f:
            f.write(b'hello world')

    def tearDown(self):
        for path in [self.input_path, self.output_path, self.decompressed_path]:
            if os.path.exists(path):
                os.remove(path)

        # Compress the file
        compress_file(self.input_path, self.output_path)
        
        # Check if the compressed file exists
        if not os.path.exists(self.output_path):
            raise FileNotFoundError(f'Compressed file {self.output_path} does not exist')
        
        # Decompress the file
        decompress_file(self.output_path, self.decompressed_path)

        # Check if the decompressed file matches the original
        with open(self.input_path, 'rb') as f:
            original_data = f.read()
        with open(self.decompressed_path, 'rb') as f:
            decompressed_data = f.read()
        # Check if the decompressed file matches the original
        with open(self.decompressed_path, 'rb') as f:
            decompressed_data = f.read()
        self.assertEqual(decompressed_data, original_data)

if __name__ == '__main__':
    unittest.main()
