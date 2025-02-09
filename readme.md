# Website Image Scraper

A Python application with a graphical user interface for scraping and downloading images from websites. The application allows you to preview images before downloading and select which ones you want to save.

## Installation

1. Install required dependencies:

```bash
pip install requests beautifulsoup4 Pillow
```

## Usage

1. Run the application:

```bash
python images_scrapper
```

## Example Usage

Let's try scraping images from Showcase Flowers (https://showcaseflowers.net/collections/homepage):

1. Launch the application
2. Enter the URL: `https://showcaseflowers.net/collections/homepage`
3. Select a download directory
4. Click "Scan for Images"
5. You'll see previews of various flower arrangements and product images
6. Select the images you want to download
7. Click "Download Selected"

The images will be saved to your chosen directory with numbered filenames (e.g., image_1.jpg, image_2.jpg, etc.)

## Requirements

- Python 3.6 or higher
- requests
- beautifulsoup4
- Pillow (PIL)
- tkinter (usually comes with Python)

## Project Structure

```
website-image-scraper/
│
├── images_scrapper      # Main application file
├── README.md            # This file
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Notes

- Some websites may block automated requests
- Always check a website's robots.txt and terms of service before scraping
- Be mindful of copyright and usage rights for downloaded images
