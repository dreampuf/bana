# Bana - Blog Application

Bana is a blog application built on Google Cloud Platform using Python 3 and Flask.

## Features

- Blog post management
- Category and tag organization
- Comment system
- Admin interface
- Multiple content formats (HTML, Markdown, reStructuredText, BBCode)
- Customizable templates

## Tech Stack

- Python 3.9
- Flask web framework
- Google Cloud Datastore (via NDB)
- Google Cloud Storage
- Jinja2 templates

## Setup

### Local Development

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up local environment variables:
   ```
   export GOOGLE_CLOUD_PROJECT=your-project-id
   export GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
   ```

3. Run the application:
   ```
   python main.py
   ```

### Deployment to Google App Engine

1. Make sure you have the Google Cloud SDK installed and configured.

2. Deploy the application:
   ```
   gcloud app deploy
   ```

## Project Structure

- `main.py`: Application entry point
- `config.py`: Configuration settings
- `utils.py`: Utility functions
- `models/`: Data models
- `routes/`: Route handlers
- `static/`: Static files (CSS, JS, images)
- `templates/`: HTML templates

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Original author: dreampuf
Updated by: Codegen
