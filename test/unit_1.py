import unittest
from unittest.mock import patch, AsyncMock
from ImageProcessor import ImageProcessor

class TestImageProcessor(unittest.TestCase):
    @patch('aiohttp.ClientSession.get')
    async def test_download_image(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read.return_value = b'test image data'
        mock_get.return_value.__aenter__.return_value = mock_response

        async with aiohttp.ClientSession() as session:
            img_path = await ImageProcessor.download_image(session, 'https://example.com/image.jpg')
            self.assertTrue(os.path.exists(img_path))
            os.remove(img_path)

if __name__ == '__main__':
    unittest.main()
